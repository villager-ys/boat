from django import forms


class PlaybookForms(forms.Form):
    playbook_name = forms.CharField(label="playbook_name", )