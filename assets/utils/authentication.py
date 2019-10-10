__author__ = "yuanshuai"

import os
from taskDo.utils.ansiable_api import ANSRunner


def ssh_authentication(server_ip, port, user, password, group_name):
    # 先测试一下连通性
    if os.system("ping %s -c 3 >>/dev/null" % server_ip):
        return -1
    # 如果本机没有id_rsa,则生成私钥公钥对
    if not os.path.exists(os.path.expanduser("~/.ssh/id_rsa")) \
            and os.path.exists(os.path.expanduser("~/.ssh/id_rsa.pub")):
        if os.system("ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa"):  # 在客户端生成ssh密钥
            return -1
    resources = {'host': server_ip, 'port': port, 'user': user, 'conn_password': password, 'group_name': group_name}
    ansible_runner = ANSRunner(resources)
    ansible_runner.run_model(server_ip, "authorized_key",
                             "user=root state=present key=\"{{ lookup('file', '~/.ssh/id_rsa.pub') }}\"")
    return ansible_runner.get_model_result()
