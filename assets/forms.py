import re
from django import forms


class AssetsForm(forms.Form):
    group_id = forms.IntegerField(widget=forms.HiddenInput)
    group_name = forms.CharField(widget=forms.HiddenInput)
    hosts = forms.CharField(label="hosts", widget=forms.TextInput(
        attrs={"class": 'form-controller', 'placeholder': '请输入hosts，多个host请用逗号分隔开'}))
    port = forms.IntegerField(label='port', initial=22, widget=forms.NumberInput(
        attrs={'class': 'form-controller', 'placeholder': '请输入端口号[22-65535]整数)'}))
    user = forms.CharField(label="user", initial="root", widget=forms.TextInput(
        attrs={'class': 'form-controller', 'placeholder': '请输入ssh连接用户'}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '请输入ssh连接密码'}))

    def clean_group_hosts(self):
        hosts = self.cleaned_data['hosts']
        host_list = hosts.split(',')
        for host in host_list:
            have_symbol = re.match('[^a-z0-9.-]+', host)
            wrong_ip = re.match('^0.|^255.', host)
            if have_symbol:
                raise forms.ValidationError('Host must contain only numbers, or the domain name separated by "."')
            elif wrong_ip:
                raise forms.ValidationError('Wrong IP address')
        return hosts

    def clean_port(self):
        port = self.cleaned_data['port']
        # have_symbol = re.match(
        #     r"^([0-9]|[1-9]\d|[1-9]\d{2}|[1-9]\d{3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$", port)
        if port > 65535 or port < 22:
            raise forms.ValidationError('port must be 22-65535的整数')
        return port


