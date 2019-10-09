__author__ = 'yuanshuai'

from django.conf import settings
from assets.models import Inventory
from ansible import constants
import ansible.constants as C
from ansible import context
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.module_utils.common.collections import ImmutableDict


class MyInventory:
    """
    Dynamic Creates and manages inventory
    By default, there are six group names
    """

    def __init__(self, resources):
        self.resource = resources
        self.loader = DataLoader()
        self.inventory = InventoryManager(loader=self.loader, sources=['%s/inventorys' % settings.BASE_DIR])
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.add_dynamic_group()

    def add_dynamic_group(self):
        """
            add hosts to a group
        """
        if not isinstance(self.resource, dict):
            return False
        group_name = self.resource['group_name']
        # 组名存在默认不再添加
        self.inventory.add_group(group_name)
        hosts = str(self.resource['hosts']).split(',')
        host_port = self.resource['port']
        # add host to group
        for host in hosts:
            # add to group
            self.inventory.add_host(host=host, group=group_name, port=host_port)


class ModelResultsCollector(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(ModelResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result


class PlayBookResultsCollector(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(PlayBookResultsCollector, self).__init__(*args, **kwargs)
        self.task_ok = {}
        self.task_skipped = {}
        self.task_failed = {}
        self.task_status = {}
        self.task_unreachable = {}

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.task_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.task_failed[result._host.get_name()] = result

    def v2_runner_on_unreachable(self, result):
        self.task_unreachable[result._host.get_name()] = result

    def v2_runner_on_skipped(self, result):
        self.task_ok[result._host.get_name()] = result

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            self.task_status[h] = {
                "ok": t['ok'],
                "changed": t['changed'],
                "unreachable": t['unreachable'],
                "skipped": t['skipped'],
                "failed": t['failures']
            }


class ANSRunner:
    """
    This is a General object for parallel execute modules.
    """

    def __init__(self, resources, *args, **kwargs):
        self.resource = resources
        self.inventory = None
        self.variable_manager = None
        self.loader = None
        self.passwords = None
        self.callback = None
        self.__initialize_data()
        self.results_raw = {}

    def __initialize_data(self):
        """ 初始化ansible """
        context.CLIARGS = ImmutableDict(listtags=False, listtasks=False,
                                        listhosts=False, syntax=False,
                                        connection="ssh", module_path=None,
                                        forks=100, private_key_file=None,
                                        ssh_common_args=None, ssh_extra_args=None,
                                        sftp_extra_args=None, scp_extra_args=None,
                                        become=False, become_method=None,
                                        become_user=None, start_at_task=None,
                                        verbosity=0, check=False)
        self.loader = DataLoader()
        self.passwords = dict()
        my_inventory = MyInventory(self.resource)
        self.inventory = my_inventory.inventory
        self.variable_manager = my_inventory.variable_manager

    def run_model(self, host_list, module_name, module_args):
        """
        run module from andible ad-hoc.
        module_name: ansible module_name
        module_args: ansible module args
        """
        play_source = dict(
            name="Ansible Play",
            hosts=host_list,
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name, args=module_args))]
        )

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        self.callback = ModelResultsCollector()
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback="minimal",
            )
            tqm._stdout_callback = self.callback
            C.HOST_KEY_CHECKING = False  # 关闭第一次使用ansible连接客户端是输入命令
            tqm.run(play)
        except Exception as err:
            print(err)
            return False
        finally:
            if tqm is not None:
                tqm.cleanup()

    def run_playbook(self, playbook_path, extra_vars=None):
        """
        run ansible palybook
        """
        try:
            self.callback = PlayBookResultsCollector()
            if extra_vars:
                self.variable_manager.extra_vars = extra_vars
            executor = PlaybookExecutor(
                playbooks=[playbook_path], inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader, passwords=self.passwords,
            )
            executor._tqm._stdout_callback = self.callback
            constants.HOST_KEY_CHECKING = False
            executor.run()
        except Exception as err:
            print(err)
            return False

    def get_model_result(self):
        self.results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.callback.host_ok.items():
            hostvisiable = host.replace('.', '_')
            self.results_raw['success'][hostvisiable] = result._result

        for host, result in self.callback.host_failed.items():
            hostvisiable = host.replace('.', '_')
            self.results_raw['failed'][hostvisiable] = result._result

        for host, result in self.callback.host_unreachable.items():
            hostvisiable = host.replace('.', '_')
            self.results_raw['unreachable'][hostvisiable] = result._result
        return self.results_raw

    def get_playbook_result(self):
        self.results_raw = {'skipped': {}, 'failed': {}, 'ok': {}, "status": {}, 'unreachable': {}, "changed": {}}
        for host, result in self.callback.task_ok.items():
            self.results_raw['ok'][host] = result

        for host, result in self.callback.task_failed.items():
            self.results_raw['failed'][host] = result

        for host, result in self.callback.task_status.items():
            self.results_raw['status'][host] = result

        # for host, result in self.callback.task_changed.items():
        #     self.results_raw['changed'][host] = result

        for host, result in self.callback.task_skipped.items():
            self.results_raw['skipped'][host] = result

        for host, result in self.callback.task_unreachable.items():
            self.results_raw['unreachable'][host] = result
        return self.results_raw
