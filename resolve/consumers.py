import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Issue, Comment, Notification

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        self.notification_group_name = f'notifications_{self.user.id}'

        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave notification group
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        
        if action == 'mark_read':
            notification_id = text_data_json.get('notification_id')
            await self.mark_notification_read(notification_id)
            
            await self.send(text_data=json.dumps({
                'action': 'notification_marked_read',
                'notification_id': notification_id
            }))

    async def notification_message(self, event):
        """Handle notification messages from other consumers"""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id, recipient=self.user
            )
            notification.read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False


class IssueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.issue_id = self.scope['url_route']['kwargs']['issue_id']
        self.issue_group_name = f'issue_{self.issue_id}'

        # Join issue group
        await self.channel_layer.group_add(
            self.issue_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave issue group
        await self.channel_layer.group_discard(
            self.issue_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        
        if action == 'new_comment':
            await self.handle_new_comment(text_data_json)
        elif action == 'new_like':
            await self.handle_new_like(text_data_json)

    async def issue_update(self, event):
        """Handle issue updates from other consumers"""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def handle_new_comment(self, data):
        issue = Issue.objects.get(id=self.issue_id)
        user = self.scope["user"]
        
        comment = Comment.objects.create(
            issue=issue,
            user=user,
            content=data.get('content')
        )
        
        # Create notification for issue owner
        if user != issue.user:
            Notification.objects.create(
                recipient=issue.user,
                sender=user,
                notification_type='comment',
                issue=issue,
                comment=comment,
                text=f"{user.username} commented on your issue."
            )
        
        return {
            'type': 'issue_update',
            'action': 'new_comment',
            'comment_id': comment.id,
            'username': user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%b %d, %Y %H:%M')
        }

    @database_sync_to_async
    def handle_new_like(self, data):
        issue = Issue.objects.get(id=self.issue_id)
        user = self.scope["user"]
        
        if issue.likes.filter(id=user.id).exists():
            issue.likes.remove(user)
            liked = False
        else:
            issue.likes.add(user)
            liked = True
            
            # Create notification for issue owner
            if user != issue.user:
                Notification.objects.create(
                    recipient=issue.user,
                    sender=user,
                    notification_type='like',
                    issue=issue,
                    text=f"{user.username} liked your issue."
                )
        
        return {
            'type': 'issue_update',
            'action': 'like_update',
            'liked': liked,
            'like_count': issue.likes.count()
        }