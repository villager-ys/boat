from django.shortcuts import render
from django.contrib import messages

from assets.models import Inventory
from .forms import AdhocForm
from taskDo.utils.ansiable_api import ANSRunner


# Create your views here.
def ad_hoc(request):
    if request.method == "POST":
        adhoc_form = AdhocForm(request.POST)
        if adhoc_form.is_valid():
            group = adhoc_form.cleaned_data['group']
            hosts = adhoc_form.cleaned_data['hosts']
            module = adhoc_form.cleaned_data['module']
            args = adhoc_form.cleaned_data['args']
            host_list = ""
            resources = dict()
            if group:
                group_list = list()
                for g in group:
                    groupname = group_by_id(g)
                    group_list.append(groupname)
                    inventorys = Inventory.objects.filter(group=g)
                    invnetory_list = []
                    for inv in inventorys:
                        invnetory_list.append(
                            {'user': inv.user, 'password': inv.password, 'ip': inv.host, 'hostname': inv.host,
                             'port': inv.port})
                    resources[groupname] = {'hosts': invnetory_list}
                host_list = ",".join(group_list)
            if hosts:
                if host_list:
                    host_list = host_list + ',' + hosts
                else:
                    host_list = hosts
                hosts_list = hosts.split(',')
                a_list = []
                for i in hosts_list:
                    a_list.append({'ip': i, 'hostname': i})
                resources["default_group"] = {'hosts': a_list}
            if not group and not hosts:
                host_list = "all"
            print(resources)
            ans_runner = ANSRunner(resources)
            ans_runner.run_model(host_list, module, args)
            result = ans_runner.get_model_result()
            if result.get("unreachable") or result.get("failed"):
                messages.error(request, str(result.get("unreachable")) + str(result.get("failed")))
    else:
        adhoc_form = AdhocForm()
    content = {"adhoc_form": adhoc_form}
    return render(request, 'ad_hoc.html', content)


def group_by_id(group_id):
    group_name = None
    group_list = Inventory.GROUP_ENUM
    for i in range(len(group_list)):
        id = group_list[i][0]
        if id == int(group_id):
            group_name = group_list[i][1]
            break
    return group_name
