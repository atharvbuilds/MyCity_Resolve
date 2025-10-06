from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Issue, Leader, CitizenProfile


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


# Register models
admin.site.register(Issue, IssueAdmin)
admin.site.register(Leader, LeaderAdmin)
admin.site.register(CitizenProfile, CitizenProfileAdmin)