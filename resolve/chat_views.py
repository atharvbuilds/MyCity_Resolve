from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.core.files.storage import default_storage
from django.db.models import Q
import json

from .models import ChatRoom, ChatMessage, User

@login_required
def chat_list(request):
    """Display list of chat rooms for the current user"""
    chat_rooms = ChatRoom.objects.filter(
        Q(participants=request.user)
    ).distinct().prefetch_related('participants')
    
    available_users = User.objects.exclude(id=request.user.id)
    
    return render(request, 'resolve/messages.html', {
        'chat_rooms': chat_rooms,
        'available_users': available_users,
    })

@login_required
def chat_room(request, room_id):
    """Display a specific chat room with messages"""
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    # Mark messages as read
    unread_messages = ChatMessage.objects.filter(
        room=room,
        read_by__exclude=request.user
    )
    for message in unread_messages:
        message.read_by.add(request.user)

    # Get all messages for this room
    messages = ChatMessage.objects.filter(room=room).order_by('created_at')
    
    chat_rooms = ChatRoom.objects.filter(
        Q(participants=request.user)
    ).distinct().prefetch_related('participants')
    
    available_users = User.objects.exclude(
        Q(id=request.user.id) | 
        Q(id__in=room.participants.values_list('id', flat=True))
    )
    
    return render(request, 'resolve/messages.html', {
        'active_room': room,
        'messages': messages,
        'chat_rooms': chat_rooms,
        'available_users': available_users,
    })

@login_required
def create_chat(request):
    """Create a new chat room"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        is_group_chat = data.get('is_group_chat', False)
        name = data.get('name') if is_group_chat else None
        participants = data.get('participants', [])
        
        if not participants:
            return JsonResponse({'error': 'No participants selected'}, status=400)
            
        # For direct messages, check if chat already exists
        if not is_group_chat and len(participants) == 1:
            existing_chat = ChatRoom.objects.filter(
                participants=request.user,
                is_group_chat=False
            ).filter(participants=participants[0]).first()
            
            if existing_chat:
                return JsonResponse({'room_id': existing_chat.id})
        
        # Create new chat room
        room = ChatRoom.objects.create(
            name=name,
            is_group_chat=is_group_chat,
            creator=request.user
        )
        
        # Add participants including the creator
        room.participants.add(request.user)
        room.participants.add(*participants)
        
        return JsonResponse({'room_id': room.id})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def send_message(request, room_id):
    """Send a message in a chat room"""
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    message_text = request.POST.get('message', '').strip()
    
    if not message_text:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    message = ChatMessage.objects.create(
        room=room,
        sender=request.user,
        content=message_text
    )
    
    # Handle file attachment if any
    if request.FILES.get('file'):
        file = request.FILES['file']
        filename = default_storage.save(f'chat_attachments/{file.name}', file)
        message.file_attachment = filename
        message.save()
    
    # Mark message as read by sender
    message.read_by.add(request.user)
    
    return JsonResponse({
        'status': 'success',
        'message_id': message.id
    })

@login_required
def add_members(request, room_id):
    """Add members to a group chat"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Only creator can add members to group chat
    if not room.is_group_chat or room.creator != request.user:
        return HttpResponseForbidden()
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        members = data.get('members', [])
        
        if not members:
            return JsonResponse({'error': 'No members selected'}, status=400)
        
        # Add new members
        users_to_add = User.objects.filter(id__in=members)
        room.participants.add(*users_to_add)
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def remove_member(request, room_id, user_id):
    """Remove a member from a group chat"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Only creator can remove members from group chat
    if not room.is_group_chat or room.creator != request.user:
        return HttpResponseForbidden()
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        user = User.objects.get(id=user_id)
        
        # Creator cannot remove themselves
        if user == request.user:
            return JsonResponse({
                'error': 'Cannot remove yourself from the group'
            }, status=400)
        
        room.participants.remove(user)
        return JsonResponse({'status': 'success'})
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)