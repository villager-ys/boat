import re
from django import forms
from assets.models import Inventory


class AdhocForm(forms.Form):
    group = forms.MultipleChoiceField(required=False, choices=Inventory.GROUP_ENUM, label="group",
                                      widget=forms.widgets.CheckboxSelectMultiple())
    hosts = forms.CharField(label='hosts', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '请输入hosts，多个host请用逗号分隔开'}))
    module = forms.CharField(label="module", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '请输入模块名'}))
    args = forms.CharField(label='args', required=False, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入args'}))

    def changed_hosts(self):
        hosts = self.cleaned_data['hosts']
        host_list = hosts.split(',')
        for host in host_list:
            have_symbol = re.match(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}',
                                   host)
            if have_symbol is None:
                raise forms.ValidationError('Host must contain only numbers, or the domain name separated by "."')
        return hosts

