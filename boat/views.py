from django.shortcuts import render
from assets.models import Inventory


def home(request):
    content = {'display': Inventory.GROUP_ENUM}
    return render(request, 'home.html', content)
