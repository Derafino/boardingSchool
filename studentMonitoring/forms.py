from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User

from .models import Subject, Form, MarkValue, StudentInfo, StudentMark, StudentHealth, Violation


class SelectSubjectFormForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), label="Предмет", empty_label="Оберіть предмет")
    form = forms.ModelChoiceField(queryset=Form.objects.all(), label="Клас", empty_label="Оберіть Клас")
    # form = forms.ModelChoiceField(queryset=.objects.all())


class SelectFormForm(forms.Form):
    form = forms.ModelChoiceField(queryset=Form.objects.all(), label="Клас", empty_label="Оберіть Клас")


class AddMarkForm(forms.ModelForm):
    class Meta:
        model = StudentMark
        fields = ['mark_value', 'mark_type']
        labels = {
            'mark_value': 'Значення оцінки',
            'mark_type': 'Тип оцінки',
        }


class AddHealthForm(forms.ModelForm):
    class Meta:
        model = StudentHealth
        fields = "__all__"
        fields = ['temperature', 'pressure', 'pulse', 'breath']
        # labels = {
        #     'mark_value': 'Значення оцінки',
        #     'mark_type': 'Тип оцінки',
        # }


class AddViolationForm(forms.ModelForm):
    violation_text = forms.CharField(widget=forms.Textarea(attrs={
        'cols': 20,
        'rows': 10,
        'style': 'width: 50%'
    }), label='Текст порушення')

    class Meta:
        model = Violation
        fields = "__all__"
        fields = ['violation_text']


class MyAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=("Логін"), max_length=75)
    password = forms.CharField(label=("Пароль"),widget=forms.PasswordInput)
