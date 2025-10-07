from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    is_group_chat = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_chats')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_name_for_user(self, user=None):
        """Get room name from perspective of a user"""
        if self.name:
            return self.name
        if not user:
            return "Chat Room"
        # For direct messages, show other participant's name
        if not self.is_group_chat:
            other_user = self.participants.exclude(id=user.id).first()
            return other_user.username if other_user else "Chat Room"
        return "Group Chat"

    def get_avatar_url(self, user=None):
        """Get avatar URL for the chat room"""
        if not user:
            return "/static/default_avatar.png"
        if not self.is_group_chat:
            other_user = self.participants.exclude(id=user.id).first()
            if other_user and hasattr(other_user, 'citizen_profile'):
                return other_user.citizen_profile.profile_picture.url if other_user.citizen_profile.profile_picture else "/static/default_avatar.png"
        return "/static/default_group.png"

    @property
    def latest_message(self):
        """Get the latest message in the room"""
        return self.messages.order_by('-created_at').first()

    def unread_count(self, user):
        """Get number of unread messages for a user"""
        return self.messages.exclude(read_by=user).count()

    class Meta:
        ordering = ['-updated_at']

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    read_by = models.ManyToManyField(User, related_name='read_messages')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.room}"

    class Meta:
        ordering = ['created_at']