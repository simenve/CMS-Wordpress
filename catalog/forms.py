from django import forms
from .models import Article, User, Tag
from django.contrib.auth.forms import UserCreationForm
from catalog.models import User, Comment, RateComment, ColorScheme, Layout, Request




class PostFormNew(forms.ModelForm):

    class Meta:
        model = Article
        fields = ('title', 'text', 'author', 'thumb', 'layout', 'tag')


class PostFormEdit(forms.ModelForm):

    class Meta:
        model = Article
        fields = ('title', 'text', 'author', 'thumb', 'layout', 'tag', 'is_published','assigned_proof_read', 'is_reviewed' )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        super(PostFormEdit, self).__init__(*args, **kwargs)

        if not request.user.is_executive_editor():
            del self.fields['assigned_proof_read']
            del self.fields['is_published']

            if request.user.is_author():
                del self.fields['is_reviewed']



class RegistrationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')


class EditUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profile_pic','bio',)


class EditorForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('is_published',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

class RateCommentForm(forms.ModelForm):
    class Meta:
        model = RateComment
        fields = ('name', 'email', 'body', 'rating')

class CreateTagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ('name',)


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('role',)

class ColorForm(forms.ModelForm):
    class Meta:
        model = ColorScheme
        fields = ('color',)

class LayoutForm(forms.ModelForm):
    class Meta:
        model = Layout
        fields = ('layout',)
