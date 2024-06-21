from django.contrib import admin
from .models import Channel, UserChannel, Message, Notification, Group, UserMessage
# Register your models here.
admin.site.register(Channel)
admin.site.register(UserChannel)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(Group)
admin.site.register(UserMessage)
