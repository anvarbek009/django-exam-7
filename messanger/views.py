from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Channel, UserChannel, Message, Notification, Group, UserMessage
from users.models import CustomUser
from django.views import View
from django.db.models import Q
from .forms import MessageForm,UserMessageForm
from django.http import JsonResponse
from django.http import HttpResponseBadRequest, HttpResponse

# Create your views here.

# @login_required
# def home(request):
#     followed_channels = UserChannel.objects.filter(user=request.user).select_related('channel')
#     joined_groups = Group.objects.filter(members=request.user)
#     user_chats = Chat.objects.filter(participants=request.user)
#     return render(request, 'base.html', {
#         'followed_channels': followed_channels,
#         'joined_groups': joined_groups,
#         'user_chats': user_chats
#     })
class Home(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'login_required.html')  # Render a template informing the user to log in

        query = request.GET.get('q', '')
        users_ = CustomUser.objects.none()
        chanels_ = Channel.objects.none()
        groups_ = Group.objects.none()

        if query:
            users_ = CustomUser.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
            chanels_ = Channel.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
            groups_ = Group.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        
        groups = Group.objects.all()
        channels = UserChannel.objects.all()
        users = CustomUser.objects.all()
        
        context = {
            'users_': users_,
            'query': query,
            'chanels_': chanels_,
            'groups_': groups_,
            'groups': groups,
            'channels': channels,
            'users': users,
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'users': list(users_.values()),
                'channels': list(chanels_.values()),
                'groups': list(groups_.values()),
            }
            return JsonResponse(data)

        return render(request, 'base.html', context=context)
    
    
@login_required
def channel_messages(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    messages = Message.objects.filter(channel=channel).order_by('-created_at')
    is_member = UserChannel.objects.filter(user=request.user, channel=channel).exists()
    return render(request, 'messanger/channel_messages.html', {
        'channel': channel,
        'messages': messages,
        'is_member': is_member
    })

@login_required
def send_message(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    is_member = UserChannel.objects.filter(user=request.user, channel=channel).exists()

    if not is_member:
        return redirect('messanger:channel_messages', channel_id=channel_id)
    else:
        if request.method == 'POST':
            content = request.POST.get('content')
            attachment = request.FILES.get('attachment')
            if content or attachment:
                Message.objects.create(
                    sender=request.user,
                    content=content,
                    attachment=attachment,
                    channel=channel
                )
    return redirect('messanger:channel_messages', channel_id=channel_id)


class GroupView(View):
    def get(self, request, pk):
        group = get_object_or_404(Group, id=pk)
        messages = Message.objects.filter(group=group).order_by('-created_at')
        message_form = MessageForm()
        return render(request, 'messanger/group.html', {'group': group, 'messages': messages, 'message_form': message_form})
    
    def post(self, request, pk):
        group = get_object_or_404(Group, id=pk)
        message_form = MessageForm(request.POST, request.FILES)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.sender = request.user
            message.group = group
            message.save()
            return redirect('messanger:group_messages', pk=group.id)
        else:
            context = {'message_form': message_form, 'group': group}
            return render(request, 'messanger/group.html', context=context)
        

# @login_required
# def chat_messages(request, chat_id):
#     chat = get_object_or_404(Chat, id=chat_id)
#     messages = Message.objects.filter(chat=chat).order_by('created_at')
#     return render(request, 'chat_messages.html', {'chat': chat, 'messages': messages})

# @login_required
# def send_chat_message(request, chat_id):
#     chat = get_object_or_404(Chat, id=chat_id)
#     if request.method == 'POST':
#         form = MessageForm(request.POST, request.FILES)
#         if form.is_valid():
#             content = form.cleaned_data['content']
#             attachment = form.cleaned_data['attachment']
#             Message.objects.create(sender=request.user, content=content, attachment=attachment, chat=chat)
#             return redirect('chat_messages', chat_id=chat_id)
#     else:
#         form = MessageForm()
#     return render(request, 'send_message.html', {'form': form})

@login_required
def send_message_to_user(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    if request.method == 'POST':
        form = UserMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = user
            if 'attachment' in request.FILES:
                message.attachment = request.FILES['attachment']
            message.save()
            return redirect('user_messages', pk=user.id)
    else:
        form = MessageForm()
    return render(request, 'messanger/send_to_user.html', {'form': form, 'user': user})


@login_required
def user_messages(request):
    # Get messages sent or received by the logged-in user
    user_messages = UserMessage.objects.filter(sender=request.user) | UserMessage.objects.filter(receiver=request.user)
    context = {
        'user_messages': user_messages
    }
    return render(request, 'messanger/user_messages.html', context)

@login_required
def send__message(request):
    if request.method == 'POST':
        sender = request.user  # Assuming sender is the logged-in user
        receiver_id = request.POST.get('receiver_id')  # Adjust how you get receiver_id based on your form data
        text = request.POST.get('text')
        
        # Validate receiver_id (optional)
        if not receiver_id:
            return HttpResponseBadRequest('Receiver ID is required.')

        # Retrieve receiver or return 404 if not found
        receiver = get_object_or_404(CustomUser, pk=receiver_id)

        # Create message instance
        message = UserMessage.objects.create(sender=sender, receiver=receiver, text=text)

        # Redirect or return JSON response as needed
        return HttpResponse('Message sent successfully!')
    else:
        return HttpResponseBadRequest('Invalid request method.')
    
@login_required
def delete_message(request, message_id):
    message = UserMessage.objects.get(pk=message_id)
    # Check if the logged-in user is either sender or receiver of the message
    if request.user == message.sender or request.user == message.receiver:
        message.delete()
    return redirect('messangeruser_messages')

class UserMessages(View):
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)
        messages = UserMessage.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) | (Q(sender=user) & Q(receiver=request.user))
        ).order_by('created_at')
        form = MessageForm()
        return render(request, 'messanger/user_messages.html', {'messages': messages, 'user': user, 'form': form})

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = user
            message.save()
            return redirect('user_messages', pk=pk)
        messages = UserMessage.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) | (Q(sender=user) & Q(receiver=request.user))
        ).order_by('created_at')
        return render(request, 'messanger/user_messages.html', {'messages': messages, 'user': user, 'form': form})
    
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'notifications': user_notifications
    }
    return render(request, 'messanger/notifications.html', context)

