from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Issue, Leader, CitizenProfile
from .models import ChatRoom, ChatMessage


class IssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'leader_tagged', 'status', 'is_leader_resolved', 
                   'is_user_confirmed', 'flag_count', 'created_at']
    list_filter = ['status', 'is_leader_resolved', 'is_user_confirmed', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'is_leader_resolved', 'is_user_confirmed']


class LeaderAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'solved_problems', 'user_account', 'created_at']
    list_filter = ['designation', 'created_at']
    search_fields = ['name', 'designation']
    readonly_fields = ['created_at', 'updated_at']


class CitizenProfileAdmin(admin.ModelAdmin):
    list_display = ['real_name', 'user', 'contact_email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['real_name', 'user__username', 'contact_email']
    readonly_fields = ['created_at', 'updated_at']


# Chat admin models
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_group_chat', 'creator', 'created_at']
    list_filter = ['is_group_chat', 'created_at']
    search_fields = ['name', 'creator__username']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at', 'updated_at']

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'content', 'is_read', 'created_at']
    list_filter = ['created_at', 'room', 'is_read']
    search_fields = ['content', 'sender__username']
    readonly_fields = ['created_at']

# Register models
admin.site.register(Issue, IssueAdmin)
admin.site.register(Leader, LeaderAdmin)
admin.site.register(CitizenProfile, CitizenProfileAdmin)
admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)