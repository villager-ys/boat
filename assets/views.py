from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Inventory
from .forms import AssetsForm
from .utils.ssh_no_pass import ssh_authentication
from taskDo.utils.ansiable_api import MyInventory


def assets(request, group_id):
    # get方法,请求资产表单,post方法,获取表单内容
    if request.method == "POST":
        assets_form = AssetsForm(request.POST)
        if assets_form.is_valid():
            # 数据校验通过，数据写入数据库同时写入文件中
            group_name = assets_form.cleaned_data['group_name']
            hosts = assets_form.cleaned_data['hosts']
            port = assets_form.cleaned_data['port']
            user = assets_form.cleaned_data['user']
            password = assets_form.cleaned_data['password']
            host_list = hosts.split(',')
            for host in host_list:
                inventory = Inventory()
                inventory.host = host
                inventory.password = password
                inventory.port = port
                inventory.user = user
                inventory.group = group_id
                inventory.save()
                # 做免密处理
                result = ssh_authentication(host, port, user, password)
                if result != 0:
                    # TODO 记录到日志
                    print("%s免密处理失败", host)
            # 数据库存完，直接调用ansible-api完成动态资产更改
            resources = {'group_name': group_name, 'hosts': hosts, 'port': port}
            MyInventory(resources)
            return redirect(reverse('home'))
    else:
        group_name = None
        group_list = Inventory.GROUP_ENUM
        for i in range(len(group_list)):
            id = group_list[i][0]
            if id == group_id:
                group_name = group_list[i][1]
        inventorys = Inventory.objects.filter(group=group_id)
        content = {'group_id': group_id, 'group_name': group_name, 'inventorys': inventorys}
        return render(request, "inventory_detail.html", content)
