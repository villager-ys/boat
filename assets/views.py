from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Inventory
from .forms import AssetsForm
from .utils.authentication import ssh_authentication


def assets(request, group_id):
    # get方法,请求资产表单,post方法,获取表单内容
    if request.method == "POST":
        asset_form = AssetsForm(request.POST)
        if asset_form.is_valid():
            # 数据校验通过，数据写入数据库同时写入文件中
            hosts = asset_form.cleaned_data['hosts']
            port = asset_form.cleaned_data['port']
            user = asset_form.cleaned_data['user']
            password = asset_form.cleaned_data['password']
            host_list = hosts.split(',')
            for host in host_list:
                # 做免密处理,判断免密是否成功，不成功
                result = ssh_authentication(host, port, user, password)
                if result is None:
                    inventory = Inventory()
                    inventory.host = host
                    inventory.password = password
                    inventory.port = port
                    inventory.user = user
                    inventory.group = group_id
                    inventory.save()
                    return redirect(reverse('home'))
                else:
                    messages.error(request, result)
    else:
        asset_form = AssetsForm()
    content = {"asset_form": asset_form, "group_id": group_id}
    return render(request, "inventory_form.html", content)


def asset_detail(request, group_id):
    inventorys = Inventory.objects.filter(group=group_id)
    content = {'group_id': group_id, 'group_name': group_by_id(group_id), 'inventorys': inventorys}
    return render(request, "inventory_detail.html", content)


def group_by_id(group_id):
    group_name = None
    group_list = Inventory.GROUP_ENUM
    for i in range(len(group_list)):
        id = group_list[i][0]
        if id == group_id:
            group_name = group_list[i][1]
            break
    return group_name
