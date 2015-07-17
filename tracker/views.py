# -*- coding: utf-8 -*-

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import ListView, RedirectView, DetailView
from django.views.generic.edit import FormView, View, CreateView

from tracker.models import Project, Task, Comment, TrackerUser
from tracker.forms import CreateProjectForm, CreateTaskForm, \
    DeveloperSearchForm, CreateCommentForm
from tracker.serializers import TaskSerializers
from utils.http import JSONResponse


class ProjectsListView(ListView):
    model = Project
    template_name = 'tracker/projects_list.html'

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.view_projects',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProjectsListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.request.user
        if not user.is_anonymous():
            kwargs['permissions'] = user.get_group_permissions()
            kwargs['projects'] = Project.objects.user_projects(user)
            if 'pk' in self.kwargs:
                kwargs['current_project_id'] = self.kwargs['pk']
                kwargs['project_tasks'] = Task.objects.filter(project__pk=self.kwargs['pk']).order_by('-created')
                kwargs['create_task_form'] = CreateTaskForm(
                    initial={'status': 'W'}, project_id=self.kwargs['pk'])
                kwargs['dev_search_form'] = DeveloperSearchForm()
                kwargs['project_developers'] = Project.objects.get(pk=self.kwargs['pk']).get_developers()
                if 'search_field' in self.request.session:
                    kwargs['search_dev_result'] = (TrackerUser.developers
                                                   .search_developers(self.request.session.pop('search_field')))
        return super(ProjectsListView, self).get_context_data(**kwargs)


class CreateProjectView(FormView):
    form_class = CreateProjectForm
    success_url = "/projects/"
    template_name = "tracker/create_project.html"

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.create_project',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CreateProjectView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        form.save(user=user)
        return super(CreateProjectView, self).form_valid(form)


class CreateTaskView(CreateView):
    form_class = CreateTaskForm

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.create_task',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CreateTaskView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateTaskView, self).get_form_kwargs()
        kwargs['project_id'] = self.kwargs['pk']
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('tracker:project_details', args=[self.kwargs['pk']])

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())


class SearchDevelopersView(RedirectView):
    permanent = False

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.add_developer',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SearchDevelopersView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.url = request.GET['referer']
        if 'search_field' in request.POST and request.POST['search_field']:
            request.session['search_field'] = request.POST['search_field']
        return redirect(self.url)


class ProjectDevelopersAddView(View):

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.add_developer',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProjectDevelopersAddView, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        project = Project.objects.get(pk=kwargs['proj_pk'])
        project.add_developer(dev_id=kwargs['dev_pk'])
        return HttpResponseRedirect(reverse('tracker:project_details',
                                            args=[project.pk]))


class ProjectDevelopersDeleteView(View):

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.add_developer',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProjectDevelopersDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        project = Project.objects.get(pk=kwargs['proj_pk'])
        project.delete_developer(dev_id=kwargs['dev_pk'])
        return HttpResponseRedirect(reverse('tracker:project_details',
                                            args=[project.pk]))


class TasksFilterView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TasksFilterView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        tasks = request.user.profile.get_project_tasks(
            project_id=request.POST['project_id'],
            filter=request.POST['filter'])
        serializer = TaskSerializers(tasks, many=True)
        return JSONResponse(serializer.data)


class TaskDetailsView(DetailView):
    model = Task
    template_name = 'tracker/task_details.html'
    context_object_name = 'task_details'

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.view_task_details',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(TaskDetailsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaskDetailsView, self).get_context_data(**kwargs)
        context['statuses_dict'] = Task.get_statuses_ordered_dict()
        context['create_comment_form'] = CreateCommentForm()
        task = self.get_object()
        context['comments'] = Comment.objects.filter(task__pk=task.id).order_by('-created')
        context['project_id'] = Project.objects.get(task__id=task.id).pk
        return context


class TaskStatusUpdateView(View):

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.change_task_status',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(TaskStatusUpdateView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        task = Task.objects.get(pk=request.POST['task_id'])
        task.status = request.POST['status']
        task.save()
        return JSONResponse('success')


class CommentAddView(View):

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.create_comment',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CommentAddView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        comment = Comment()
        comment.author = request.user
        comment.task = Task.objects.get(pk=kwargs['pk'])
        comment.text = request.POST['text']
        comment.save()
        return HttpResponseRedirect(reverse('tracker:task_details_view',
                                            args=[kwargs['pk']]))


class CommentDeleteView(View):

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.del_comment',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CommentDeleteView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        comment = Comment.objects.get(pk=kwargs['comment_pk'])
        comment.delete()
        return HttpResponseRedirect(reverse('tracker:task_details_view',
                                            args=[kwargs['task_pk']]))


class CommentUpdateView(View):

    @method_decorator(login_required)
    @method_decorator(permission_required('tracker.update_comment',
                                          raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CommentUpdateView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        comment = Comment.objects.get(pk=request.POST['comment_id'])
        comment.text = request.POST['comment_body']
        comment.save()
        return JSONResponse({'status': 'success', 'comment_body': comment.text})
