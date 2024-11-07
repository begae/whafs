from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    your_name = forms.CharField(max_length=25)
    your_email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ['by_name', 'by_email', 'body']
        labels = {'by_name': 'Your name', 'by_email': 'Your email'}


class SearchForm(forms.Form):
    keywords = forms.CharField()