# coding: utf-8
from django import forms


class UserForm(forms.Form):
    name = forms.CharField(required=True)
    pwd = forms.CharField(required=True)

