import os
import paramiko


# TODO 暂时不做详细的结果处理
def ssh_authentication(server_ip, port, user, passwd):
    """进行ssh的免密码认证"""
    # server_ip 备份服务器地址，字符串
    if os.system("ping %s -c 3 >>/dev/null" % server_ip):
        # 先测试一下连通性
        return -1

    if not os.path.exists(os.path.expanduser("~/.ssh/id_rsa")) \
            and os.path.exists(os.path.expanduser("~/.ssh/id_rsa.pub")):
        if os.system("ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa"):  # 在客户端生成ssh密钥,设置好参数，这样就不会中途要求输入
            return -1

    # 使用用户名，密码建立ssh链接
    sock = server_ip + ":" + port
    transport = paramiko.Transport(sock)
    try:
        transport.connect(username=user, password=passwd)
    except Exception as err:
        print(err)
        return -1

    ssh = paramiko.SSHClient()
    ssh._transport = transport  # 将sftp和ssh一同建立
    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.put(os.path.expanduser("~/.ssh/id_rsa.pub"), "/root/.ssh/filebackkey.pub")  # 上传公钥

    stdin, stdout, stderr = ssh.exec_command(
        "cat /root/.ssh/filebackkey.pub >> /root/.ssh/authorized_keys")  # 添加公钥 这里根据实际情况进行修改，设置成用户名下的.ssh
    if stderr.channel.recv_exit_status():
        ssh.close()
        return -1

    stdin, stdout, stderr = ssh.exec_command("chmod 600 /root/.ssh/authorized_keys")
    if stderr.channel.recv_exit_status():
        ssh.close()
        return -1

    stdin, stdout, stderr = ssh.exec_command("systemctl restart sshd")  # 重启ssh服务
    if stderr.channel.recv_exit_status():
        ssh.close()
        return -1

    transport.close()
    ssh.close()

    if os.system("eval `ssh-agent` && ssh-add"):  # 客户端添加私钥
        return -1
    return 0
