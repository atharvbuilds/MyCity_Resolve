from django.urls import re_path
from . import consumers
from .chat_consumer import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/issue/(?P<issue_id>\d+)/$', consumers.IssueConsumer.as_asgi()),
]