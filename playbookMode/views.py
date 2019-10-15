from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages
from .forms import PlaybookForms
from .models import Playbook
from taskDo.utils.ansiable_api import ANSRunner


# Create your views here.
def playbook_form(request):
    if request.method == 'POST':
        playbook = PlaybookForms(request.POST, request.FILES)
        if playbook.is_valid():
            playbook.save()
    else:
        playbook = PlaybookForms()
    content = {'playbook_form': playbook}
    return render(request, 'playbook_form.html', content)


def playbook_list(request):
    page_num = request.GET.get('page', 1)
    playbooks = Playbook.objects.all()
    prt = Paginator(playbooks, settings.EACH_PAGE_BLOG_NUM)
    playbook_with_page = prt.get_page(page_num)
    total = prt.num_pages
    current_page_num = playbook_with_page.number  # 获取当前页码
    page_size = list(range(max(current_page_num - 2, 1), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, total) + 1))
    # 加上省略号 # 不是第一页加上第一页,不是最后一个追加最后一页
    if page_size[0] - 1 >= 1:
        page_size.insert(0, 1)
        page_size.insert(1, '...')
    if total - page_size[-1] >= 1:
        page_size.append('...')
        page_size.append(total)
    content = {'playbooks': playbook_with_page, "page_size": page_size}
    return render(request, 'playbook_list.html', content)


def playbook_do(request, playbook_id):
    playbook = get_object_or_404(Playbook, pk=playbook_id)
    path = "%s/conf/media/" % settings.BASE_DIR + str(playbook.playbook_content)
    ans_runner = ANSRunner(str())
    ans_runner.run_playbook(path)
    result = ans_runner.get_playbook_result()
    return render(request, 'playbook_list.html')
