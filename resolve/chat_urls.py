from django.urls import path
from . import views

app_name = 'resolve'

urlpatterns = [
    # Existing URLs...
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/create/', views.create_chat, name='create_chat'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/<int:room_id>/send/', views.send_message, name='send_message'),
    path('chat/<int:room_id>/add_members/', views.add_members, name='add_members'),
    path('chat/<int:room_id>/remove_member/<int:user_id>/', views.remove_member, name='remove_member'),
]