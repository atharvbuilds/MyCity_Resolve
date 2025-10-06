from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Leader(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, help_text="e.g., 'Council Member', 'Mayor'")
    solved_problems = models.IntegerField(default=0)
    profile_picture = models.CharField(max_length=200, null=True, blank=True, help_text="URL to profile picture")
    user_account = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, 
                                      help_text="Link to user account for login access")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.designation}"

    class Meta:
        ordering = ['-solved_problems']


class CitizenProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    real_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.real_name}"

    class Meta:
        ordering = ['-created_at']


class Issue(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('pending_confirm', 'Pending Confirmation'),
        ('solved', 'Solved'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.CharField(max_length=200, null=True, blank=True, help_text="URL to issue image")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    leader_tagged = models.ForeignKey(Leader, on_delete=models.CASCADE, related_name='tagged_issues')
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
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