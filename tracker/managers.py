#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q


class DevelopersManager(models.Manager):
    def all(self):
        return super(DevelopersManager, self).filter(user__groups__name='developer')

    def search_developers(self, search_data):
        developers = self.all().filter(
            Q(user__first_name__istartswith=search_data) |
            Q(user__last_name__istartswith=search_data) |
            Q(user__username__istartswith=search_data))
        return developers


class ProjectManagersManager(models.Manager):
    def all(self):
        return super(ProjectManagersManager, self).filter(user__groups__name='manager')


class ProjectObjManager(models.Manager):
    def user_projects(self, user):
        if user.profile.is_project_manager():
            projects = self.filter(creator=user).order_by('created')
        elif user.profile.is_developer():
            projects = (self.all()
                        .filter(members__id__exact=user.id)
                        .order_by('created'))
        else:
            raise TypeError('User group is not defined...')
        return projects
