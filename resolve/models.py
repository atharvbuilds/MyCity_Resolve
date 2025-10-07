from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Leader(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, help_text="e.g., 'Council Member', 'Mayor'")
    solved_problems = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to='leader_profiles/', null=True, blank=True)
    user_account = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, 
                                      help_text="Link to user account for login access")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.designation}"

    class Meta:
        ordering = ['-solved_problems']


class CitizenProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='citizen_profile')
    real_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    profile_picture = models.ImageField(upload_to='citizen_profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    hometown_latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True)
    hometown_longitude = models.DecimalField(max_digits=22, decimal_places=16, null=True)
    hometown_name = models.CharField(max_length=200, null=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    is_verified = models.BooleanField(default=False)
    issues_resolved = models.IntegerField(default=0)
    reputation_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return CitizenProfile.objects.filter(followers=self).count()

    def issue_count(self):
        return self.user.issues.count()

    def __str__(self):
        return f"Profile for {self.real_name}"

    class Meta:
        ordering = ['-created_at']





class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    usage_count = models.IntegerField(default=0)

    def __str__(self):
        return f'#{self.name}'

class Issue(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('pending_confirm', 'Pending Confirmation'),
        ('solved', 'Solved'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='issue_images/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    leader_tagged = models.ForeignKey(Leader, on_delete=models.CASCADE, related_name='tagged_issues')
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    hashtags = models.ManyToManyField(Hashtag, related_name='issues', blank=True)
    likes = models.ManyToManyField(User, related_name='liked_issues', blank=True)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_issues', blank=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    is_leader_resolved = models.BooleanField(default=False)
    is_user_confirmed = models.BooleanField(default=False)
    flag_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']

    @property
    def anonymous_user_id(self):
        """Return last 4 characters of user ID for anonymous display"""
        return str(self.user.id)[-4:]


# Signal to automatically create CitizenProfile when User is created
@receiver(post_save, sender=User)
def create_citizen_profile(sender, instance, created, **kwargs):
    if created:
        CitizenProfile.objects.create(
            user=instance,
            real_name=instance.get_full_name() or instance.username,
            contact_email=instance.email or ''
        )


@receiver(post_save, sender=User)
def save_citizen_profile(sender, instance, **kwargs):
    if hasattr(instance, 'citizenprofile'):
        instance.citizenprofile.save()


class Comment(models.Model):
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    def like_count(self):
        return self.likes.count()

    def reply_count(self):
        return self.replies.count()

    class Meta:
        ordering = ['-created_at']


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('follow', 'New Follower'),
        ('like', 'New Like'),
        ('comment', 'New Comment'),
        ('mention', 'Mention'),
        ('issue_update', 'Issue Update'),
        ('status_change', 'Status Change'),
        ('message', 'New Message'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    is_group_chat = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_name_for_user(self, user):
        """Get appropriate name for the chat based on whether it's group or direct"""
        if self.is_group_chat:
            return self.name
        else:
            # For direct messages, show the other participant's name
            other_participant = self.participants.exclude(id=user.id).first()
            return other_participant.username if other_participant else "Chat"

    class Meta:
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    class Meta:
        ordering = ['created_at']