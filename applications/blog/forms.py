# applications/blog/forms.py
from django import forms
from .models import Post
from ckeditor_5.widgets import CKEditor5Widget

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = Post
        fields = '__all__'
