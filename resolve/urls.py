from django.urls import path, include
from . import views, chat_views

urlpatterns = [
    # Chat URLs
    path('chat/', chat_views.chat_list, name='chat_list'),
    path('chat/create/', chat_views.create_chat, name='create_chat'),
    path('chat/<int:room_id>/', chat_views.chat_room, name='chat_room'),
    path('chat/<int:room_id>/send/', chat_views.send_message, name='send_message'),
    path('chat/<int:room_id>/add_members/', chat_views.add_members, name='add_members'),
    path('chat/<int:room_id>/remove_member/<int:user_id>/', chat_views.remove_member, name='remove_member'),

    # Existing URLs
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('feed/', views.issue_feed, name='issue_feed'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('submit/', views.submit_issue, name='submit_issue'),
    path('resolve/<int:issue_id>/', views.leader_resolve, name='leader_resolve'),
    path('confirm/<int:issue_id>/', views.user_confirm, name='user_confirm'),
    path('flag/<int:issue_id>/', views.flag_issue, name='flag_issue'),
    path('my-issues/', views.my_issues, name='my_issues'),
    
    # Social interaction URLs
    path('like/<int:issue_id>/', views.toggle_like, name='toggle_like'),
    path('bookmark/<int:issue_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('comment/<int:issue_id>/', views.add_comment, name='add_comment'),
    path('reply/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('tag/<str:tag_name>/', views.hashtag_view, name='hashtag_view'),
    path('activity/', views.activity_feed, name='activity_feed'),
    path('explore/', views.explore, name='explore'),
]
