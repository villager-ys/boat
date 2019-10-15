from django import forms
from django.forms import ModelForm
from .models import Playbook


class PlaybookForms(ModelForm):
    # playbook_name = ModelForm.CharField(label="playbook_name", widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': '请输出playbook名称，如：docker.yml'}))
    # playbook_description = ModelForm.CharField(label="playbook_description", widget=ModelForm.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': '请输入playbook描述'}))
    # playbook_content = ModelForm.FileField(label='上传文件', required=False)

    class Meta:
        model = Playbook
        fields = ['playbook_name', 'playbook_description', 'playbook_content', ]
        widgets = {
            'playbook_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '请输出playbook名称，如：docker.yml'}),
            'playbook_description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '请输入playbook描述'}),
            'playbook_content': forms.ClearableFileInput()
        }
        labels = {
            'playbook_name': "playbook_name",
            'playbook_description': "playbook_description",
            'playbook_content': "playbook_content"
        }


