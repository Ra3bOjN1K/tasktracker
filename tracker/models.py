# -*- coding: utf-8 -*-

from collections import OrderedDict

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save

from tracker.managers import DevelopersManager, ProjectManagersManager, \
    ProjectObjManager


class TrackerUser(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='profile')
    objects = models.Manager()
    developers = DevelopersManager()
    project_managers = ProjectManagersManager()

    def is_project_manager(self):
        return 'manager' in self.user.groups.values_list('name', flat=True)

    def is_developer(self):
        return 'developer' in self.user.groups.values_list('name', flat=True)

    def get_project_tasks(self, project_id, filter='all_tasks'):
        if project_id is None:
            raise AttributeError()
        if filter == 'my_tasks' and self.is_developer():
            tasks = (Task.objects.filter(Q(project__pk=project_id) &
                                         Q(executors__id__exact=str(self.user.id)))
                     .order_by('-created'))
        else:
            tasks = Task.objects.filter(project__pk=project_id).order_by('-created')
        return tasks


class Project(models.Model):
    name = models.CharField(max_length=60)
    creator = models.ForeignKey(User, related_name='project_creator')
    members = models.ManyToManyField(User, related_name='project_members')
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProjectObjManager()

    class Meta:
        permissions = (
            ("view_projects", "Can see available projects"),
            ("create_project", "Can create projects"),
            ("add_developer", "Can add developer to the project"),
        )

    def get_developers(self):
        if self.members.count():
            return self.members.order_by('first_name')
        else:
            return self.members.all()

    def add_developer(self, dev_id):
        dev = User.objects.get(pk=dev_id)
        self.members.add(dev)

    def delete_developer(self, dev_id):
        dev = User.objects.get(pk=dev_id)
        self.members.remove(dev)


class Task(models.Model):
    STATUS_CHOICES = (
        ('W', 'waiting'),
        ('I', 'implementation'),
        ('V', 'verifying'),
        ('R', 'releasing'),
    )

    name = models.CharField(max_length=60)
    creator = models.ForeignKey(User, related_name='task_creator')
    executors = models.ManyToManyField(User, related_name='task_executors')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project)

    @classmethod
    def get_statuses_ordered_dict(cls):
        return OrderedDict(cls.STATUS_CHOICES)

    class Meta:
        permissions = (
            ("view_tasks", "Can see available tasks"),
            ("filter_tasks", "Can filter tasks"),
            ("create_task", "Can create tasks"),
            ("view_task_details", "Can view task details"),
            ("change_task_status", "Can change task status"),
            ("attach_task_to_developer", "Can attach task to developer"),
        )

    def get_verbose_status_val(self):
        return dict(self.STATUS_CHOICES)[self.status]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User)
    task = models.ForeignKey(Task)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ("view_comments", "Can see available comments"),
            ("create_comment", "Can create comment"),
            ("update_comment", "Can update comment"),
            ("del_comment", "Can delete comment"),
        )


def get_manager_group():
    try:
        group = Group.objects.get(name='manager')
    except ObjectDoesNotExist:
        group = Group(name='manager')
        group.save()
        group.permissions = [
            Permission.objects.get(codename='view_projects'),
            Permission.objects.get(codename='create_project'),
            Permission.objects.get(codename='add_developer'),
            Permission.objects.get(codename='view_tasks'),
            Permission.objects.get(codename='create_task'),
            Permission.objects.get(codename='create_comment'),
            Permission.objects.get(codename='view_comments'),
            Permission.objects.get(codename='update_comment'),
            Permission.objects.get(codename='del_comment'),
            Permission.objects.get(codename='view_task_details'),
            Permission.objects.get(codename='change_task_status'),
            Permission.objects.get(codename='attach_task_to_developer'),
        ]
    return group


def get_developer_group():
    try:
        group = Group.objects.get(name='developer')
    except ObjectDoesNotExist:
        group = Group(name='developer')
        group.save()
        group.permissions = [
            Permission.objects.get(codename='view_projects'),
            Permission.objects.get(codename='view_tasks'),
            Permission.objects.get(codename='filter_tasks'),
            Permission.objects.get(codename='create_task'),
            Permission.objects.get(codename='view_comments'),
            Permission.objects.get(codename='create_comment'),
            Permission.objects.get(codename='update_comment'),
            Permission.objects.get(codename='del_comment'),
            Permission.objects.get(codename='view_task_details'),
            Permission.objects.get(codename='change_task_status'),
        ]
    return group


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = TrackerUser.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)
