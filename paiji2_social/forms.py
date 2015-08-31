from django import forms
from django.utils.translation import ugettext as _

from .models import Comment, Message
from tinymce.widgets import TinyMCE


class CommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['content'].label = _('Write a comment...')

    class Meta:
        model = Comment
        fields = ('content', )


class MessageForm(forms.ModelForm):

    def __init__(self, groups, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = groups

    class Meta:
        model = Message
        fields = (
            'group',
            'title',
            'content',
            'public',
        )
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 20}),
        }
