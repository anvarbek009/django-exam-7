from django import forms
from .models import Message,UserMessage

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'attachment']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'attachment']

    attachment = forms.FileField(required=False)

class UserMessageForm(forms.ModelForm):
    class Meta:
        model = UserMessage
        fields = ['text', 'attachment']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type a message...'}),
        }
    attachment = forms.FileField(required=False)