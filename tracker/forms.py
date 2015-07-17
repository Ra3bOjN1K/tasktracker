#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from tracker.models import get_manager_group, get_developer_group, Project, \
    Task, Comment


class SignUpForm(forms.Form):
    ROLE_CHOICES = (
        ('MAN', 'Manager'),
        ('DEV', 'Developer'),
    )
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def signup(self, request, user):
        # user.is_active = False
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        user.save()
        if self.cleaned_data['role'] == 'MAN':
            group = get_manager_group()
        elif self.cleaned_data['role'] == 'DEV':
            group = get_developer_group()
        else:
            raise TypeError()
        group.user_set.add(user)


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')

    def save(self, user=None, commit=True):
        project = super(CreateProjectForm, self).save(commit=False)
        project.creator = user
        project.name = self.cleaned_data['name']
        project.description = self.cleaned_data['description']
        if commit:
            project.save()
        return project


class CreateTaskForm(forms.ModelForm):
    executor = forms.ModelChoiceField(queryset=User.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        qs_developers = []
        if 'project_id' in kwargs:
            self.current_project = Project.objects.get(pk=kwargs.pop('project_id'))
            qs_developers = self.current_project.get_developers()
        if 'user' in kwargs:
            self.current_user = kwargs.pop('user')
        super(CreateTaskForm, self).__init__(*args, **kwargs)
        if qs_developers:
            self.fields['executor'].queryset = qs_developers

    class Meta:
        model = Task
        fields = ('name', 'description', 'status')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter a task name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description',
                                                 'rows': 8,
                                                 'style': 'resize:none'}),
        }

    def save(self, commit=True):
        task = super(CreateTaskForm, self).save(commit=False)
        task.creator = self.current_user
        if commit:
            task.project = self.current_project
            task.save()
            if self.current_user.has_perm("tracker.attach_task_to_developer"):
                executor = self.cleaned_data['executor']
            else:
                executor = self.current_user
            task.executors.add(executor)
        return task

    def is_valid(self):
        has_executor = 'executor' in self.data and self.data['executor']
        if (self.current_user.has_perm("tracker.attach_task_to_developer") and
                not has_executor):
            self.add_error('executor', "Field 'executor' is required!")
        return super(CreateTaskForm, self).is_valid()


class DeveloperSearchForm(forms.Form):
    search_field = forms.CharField(max_length=60, label='',
                                   widget=forms.TextInput(attrs={'placeholder': 'Enter first or last name'}))


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Add a comment',
                                          'rows': 3,
                                          'style': 'resize:none'}),
        }
