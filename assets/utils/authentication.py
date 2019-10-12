__author__ = "yuanshuai"

import os
from django.conf import settings
from taskDo.utils.ansiable_api import ANSRunner


def ssh_authentication(server_ip, port, user, password, groupname):
    dir_name = settings.BASE_DIR + "/conf"
    # 先测试一下连通性
    if os.system("ping %s -c 3 >>/dev/null" % server_ip):
        return "%s网络ping不通" % server_ip
    # 如果本机没有id_rsa,则生成私钥公钥对
    if not (os.path.exists("%s/.ssh/id_rsa" % dir_name) and os.path.exists("%s/.ssh/id_rsa.pub" % dir_name)):
        # 在客户端生成ssh密钥,使用ansible openssh_keypair,默认就是root用户(不是root用户生成不了id_rsa文件),暂不考虑权限的问题
        resources = str({'hostname': '127.0.0.1', 'port': port, 'user': user, 'conn_password': password})
        ans_runner = ANSRunner(resources)
        ans_runner.run_model("127.0.0.1", "openssh_keypair",
                             "path=%s/.ssh/id_rsa force=True" % dir_name)
        if result(ans_runner) == -1:
            return "本机密钥对生成失败"
    resources = {
        groupname: {
            "hosts": [
                {'user': user, 'password': password, 'ip': server_ip, 'hostname': server_ip,
                 'port': port},
            ],
            "vars": {}
        }
    }
    ans_runner = ANSRunner(resources)
    args = "user=%s state=present key=\"{{ lookup('file', '%s/.ssh/id_rsa.pub') }}\"" % (user, dir_name)
    ans_runner.run_model(server_ip, "authorized_key", args)
    if result(ans_runner) == -1:
        return "分发authorized_key失败"


def result(ans_runner):
    results_raw = ans_runner.get_model_result()
    failed = results_raw.get("failed")
    unreachable = results_raw.get('unreachable')
    if failed or unreachable:
        return -1
