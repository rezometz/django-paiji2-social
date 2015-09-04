# -*- encoding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.views import generic
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Message, Comment, Group
from .forms import CommentForm, MessageForm
from django.conf import settings
try:
    import rezo
    REZO = True
except ImportError:
    REZO = False


class MessageListView(generic.ListView):
    model = Message
    paginate_by = 5
    context_object_name = 'news'
    template_name = 'social/index.html'

    def get_queryset(self):
        qs = super(MessageListView, self).get_queryset()
        if not self.request.user.is_authenticated():
            qs = qs.filter(public=True)

        return qs.order_by('-pubDate').select_related('author')


class MessageFormMixin(object):

    form_class = MessageForm

    def get_form_kwargs(self):
        kwargs = super(MessageFormMixin, self).get_form_kwargs()
        kwargs.update({
            'groups': Group.objects.filter(
                bureaus__members__utilisateur=self.request.user,
                )
        })
        return kwargs


class MessageCreateView(MessageFormMixin, generic.CreateView):
    model = Message
    template_name = 'social/message_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(MessageCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(
            self.request,
            _('Your request has been saved successfully :P'),
        )
        return reverse('index')


class OwnershipMessageCheck(object):
    def dispatch(self, request, *args, **kwargs):
        """ Making sure that only authors can update Messages """
        obj = self.get_object()
        if obj.author != self.request.user:
            return HttpResponseNotFound(
                _('Rezo is not hacked. You don\'t have the permission xD')
            )
        return super(OwnershipMessageCheck, self).dispatch(
            request, *args, **kwargs
        )


class MessageEditView(
                     OwnershipMessageCheck,
                     MessageFormMixin,
                     generic.UpdateView
                    ):
    model = Message
    template_name = 'social/message_form.html'
    message_update = _(
        'Your Message has been updated, it will be refreshed in a moment'
    )

    def get_success_url(self):
        messages.success(
            self.request,
            self.message_update,
        )
        return reverse('index')


class MessageDeleteView(OwnershipMessageCheck, generic.DeleteView):
    model = Message
    template_name = 'social/message_confirm_delete.html'
    message_delete = _(
        'Your Message has been removed, it will be refreshed in a moment'
    )

    def get_success_url(self):
        messages.success(
            self.request,
            self.message_delete,
        )
        success_url = self.request.POST.get('next')
        return success_url if success_url != '' else reverse('index')


class CommentCreateView(generic.CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']

    def form_valid(self, form):
        # TODO: it should check that the message exists before
        #       showing the form
        message = Message.objects.get(id=self.kwargs['on_message'])
        form.instance.author = self.request.user
        form.instance.message = message
        # TODO use auto_now_add=True
        form.instance.pubDate = timezone.now()
        return super(CommentCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(
            self.request,
            _("Your comment has been successfully saved."),
        )
        success_url = self.request.POST.get('next')
        return success_url if success_url != '' else reverse('index')


class GroupView(generic.DetailView):
    model = Group
    template_name = 'social/group_detail.html'


class GroupMixin(object):

    def dispatch(self, *args, **kwargs):
        self.group = get_object_or_404(Group, slug=kwargs['slug'])
        return super(GroupMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self):
        cd = super(GroupMixin, self).get_context_data()
        cd['group'] = self.group
        return cd


class GroupNewsView(GroupMixin, generic.ListView):
    model = Message
    template_name = 'social/news_list.html'
    context_object_name = 'news'
    paginate_by = 8

    def get_queryset(self):
        qs = super(GroupNewsView, self).get_queryset()
        qs = qs.filter(group=self.group)
        qs = qs.order_by(
            '-pubDate'
        ).select_related(
            'author'
        )
        return qs


class GroupMembersView(GroupMixin, generic.ListView):
    model = get_user_model()
    template_name = 'social/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        qs = super(GroupMembersView, self).get_queryset()
        qs = qs.filter(posts__bureau__group=self.group)
        return qs


class UserDirectoryView(generic.ListView):
    model = get_user_model()
    context_object_name = 'users'
    ordering = ['last_name', 'first_name', 'username']
    template_name = 'social/directory.html'
    paginate_by = 20
    last_room_update = None
    try:
        min_update_delta = settings.MIN_ROOM_UPDATE_DELTA
    except:
        print('no MIN_ROOM_UPDATE_DELTA setting found…')
        min_update_delta = timedelta(days=7)

    def _update_user_rooms(self):
        if (
            REZO and (
                UserDirectoryView.last_room_update is None or
                UserDirectoryView.min_update_delta <
                timezone.now() - UserDirectoryView.last_room_update
            )
        ):
            if REZO:
                rezo.models.update_user_rooms()
                UserDirectoryView.last_room_update = timezone.now()

    def get_queryset(self):
        self._update_user_rooms()
        if 'q' in self.request.GET:
            query = self.request.GET['q']
            words = query.split(' ')
            Qobj = Q()
            filtered = False
            for word in words:
                if word != '':
                    filtered = True
                    Qobj |= (
                        Q(first_name__icontains=word) |
                        Q(last_name__icontains=word) |
                        Q(username__icontains=word) |
                        Q(email__icontains=word)
                    )
                    if REZO:
                        Qobj |= Q(room__icontains=word)
            if filtered:
                return self.model.objects.filter(Qobj)
        return super(UserDirectoryView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(UserDirectoryView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q', '')
        context.update({'q': q})
        return context


class GroupDirectoryView(generic.ListView):
    model = Group
    context_object_name = 'groups'
    ordering = ['name', 'category', 'createdOn']
    template_name = 'social/groups.html'
