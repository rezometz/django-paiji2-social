from django.shortcuts import get_object_or_404
from django.views import generic
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.contrib.auth import get_user_model

from tinymce.widgets import TinyMCE

from .models import Message, Comment, Group
from .forms import CommentForm
# from django.conf import settings


class MessageListView(generic.ListView):
    model = Message
    paginate_by = 8
    context_object_name = 'news'
    template_name = 'home/index.html'

    def get_queryset(self):
        qs = super(MessageListView, self).get_queryset()
        if not self.request.user.is_authenticated():
            qs = qs.filter(public=True)

        return qs.order_by('-pubDate').select_related('author')


class MessageCreateView(generic.CreateView):
    model = Message
    fields = ('group', 'title', 'content', 'public')
    template_name = 'social/message_form.html'

    def get_form(self, form_class):
        form = super(MessageCreateView, self).get_form(form_class)
        form.fields['group'].queryset = Group.objects.filter(
            bureaus__members__utilisateur=self.request.user
        )
        form.fields['content'].widget = TinyMCE(attrs={'cols': 80, 'rows': 20})
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(MessageCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(
            self.request,
            _('Your request has been saved successfully :P'),
        )
        success_url = self.request.POST.get('next')
        return success_url if success_url != '' else reverse('index')


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


class MessageEditView(OwnershipMessageCheck, generic.UpdateView):
    model = Message
    fields = ('group', 'title', 'content', 'public')
    template_name = 'social/message_form.html'
    message_update = _(
        'Your Message has been updated, it will be refreshed in a moment'
    )

    def get_form(self, form_class):
        form = super(MessageEditView, self).get_form(form_class)
        form.fields['group'].queryset = Group.objects.filter(
            bureaus__members__utilisateur=self.request.user
        )
        form.fields['content'].widget = TinyMCE(attrs={'cols': 80, 'rows': 20})
        return form

    def get_success_url(self):
        messages.success(
            self.request,
            self.message_update,
        )
        success_url = self.request.POST.get('next')
        return success_url if success_url != '' else reverse('index')


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
        return reverse('index')


class GroupView(generic.DetailView):
    model = Group
    template_name = 'social/group_detail.html'


# TODO; factorize group retrieving
class GroupNewsView(generic.ListView):
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

    def dispatch(self, *args, **kwargs):
        self.group = get_object_or_404(Group, slug=kwargs['slug'])
        return super(GroupNewsView, self).dispatch(*args, **kwargs)

    def get_context_data(self):
        cd = super(GroupNewsView, self).get_context_data()
        cd['group'] = self.group
        return cd


class GroupMembersView(generic.ListView):
    model = get_user_model()
    template_name = 'social/member_list.html'
    context_object_name = 'members'

    def dispatch(self, *args, **kwargs):
        self.group = get_object_or_404(Group, slug=kwargs['slug'])
        return super(GroupMembersView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super(GroupMembersView, self).get_queryset()
        qs = qs.filter(posts__bureau__group=self.group)
        return qs

    def get_context_data(self):
        cd = super(GroupMembersView, self).get_context_data()
        cd['group'] = self.group
        return cd
