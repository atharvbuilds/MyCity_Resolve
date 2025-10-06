from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('feed/', views.issue_feed, name='issue_feed'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('submit/', views.submit_issue, name='submit_issue'),
    path('resolve/<int:issue_id>/', views.leader_resolve, name='leader_resolve'),
    path('confirm/<int:issue_id>/', views.user_confirm, name='user_confirm'),
    path('flag/<int:issue_id>/', views.flag_issue, name='flag_issue'),
    path('my-issues/', views.my_issues, name='my_issues'),
]
