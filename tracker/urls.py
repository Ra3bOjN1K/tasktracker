# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from tracker import views


urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='tracker:projects_list', permanent=True)),
    url(r'^projects/$', views.ProjectsListView.as_view(),
        name='projects_list'),
    url(r'^project/(?P<pk>[0-9]*)/details/$', views.ProjectsListView.as_view(),
        name='project_details'),
    url(r'^project/create/$', views.CreateProjectView.as_view(),
        name='create_project'),
    url(r'^developers/search/$', views.SearchDevelopersView.as_view(),
        name='search_developers'),
    url(r'^project/(?P<proj_pk>[0-9]*)/developer/(?P<dev_pk>[0-9]*)/add/$',
        views.ProjectDevelopersAddView.as_view(), name='add_dev_to_project'),
    url(r'^project/(?P<proj_pk>[0-9]*)/developer/(?P<dev_pk>[0-9]*)/del/$',
        views.ProjectDevelopersDeleteView.as_view(), name='del_dev_from_project'),
    url(r'^tasks/$', views.TasksFilterView.as_view(),
        name='developer_tasks'),
    url(r'^project/(?P<pk>[0-9]*)/task/create/$', views.CreateTaskView.as_view(),
        name='create_task'),
    url(r'^task/(?P<pk>[0-9]*)/details/$', views.TaskDetailsView.as_view(),
        name='task_details_view'),
    url(r'^task/status-update/$', views.TaskStatusUpdateView.as_view(),
        name='task_status_update_view'),
    url(r'^task/(?P<pk>[0-9]*)/comment/add/$', views.CommentAddView.as_view(),
        name='add_comment_view'),
    url(r'^task/(?P<task_pk>[0-9]*)/comment/(?P<comment_pk>[0-9]*)/delete/$',
        views.CommentDeleteView.as_view(), name='del_comment_view'),
    url(r'^comment/edit/$', views.CommentUpdateView.as_view(),
        name='edit_comment_view'),
]
