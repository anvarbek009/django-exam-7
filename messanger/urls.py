# urls.py
from django.urls import path
from .views import Home, channel_messages,  send_message,UserMessages,send_message_to_user,GroupView,notifications

app_name = 'messanger'
urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('send_message/<int:channel_id>/', send_message, name='send_message'),
    path('messages/channel/<int:channel_id>/', channel_messages, name='channel_messages'),
    path('message/<int:pk>/user/', UserMessages.as_view(), name='user_messages'),
    path('message/<int:pk>/', send_message_to_user, name='user'),
    path('group/<int:pk>/', GroupView.as_view(), name='group_messages'),
    path('notifications/', notifications, name='notifications'),


    # path('messages/chat/<int:chat_id>/', chat_messages, name='chat_messages'),
]