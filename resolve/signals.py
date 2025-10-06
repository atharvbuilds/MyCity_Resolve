from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Issue


@receiver(post_save, sender=Issue)
def handle_issue_resolution(sender, instance, created, **kwargs):
    """
    Handle the two-step resolution logic for issues.
    This signal is triggered whenever an Issue is saved.
    """
    # Prevent recursive saves by temporarily disconnecting the signal
    post_save.disconnect(handle_issue_resolution, sender=Issue)
    
    try:
        # Check for Final Solve: Both leader and user have confirmed
        if (instance.is_leader_resolved and 
            instance.is_user_confirmed and 
            instance.status != 'solved'):
            
            instance.status = 'solved'
            # Increment the leader's solved_problems count
            leader = instance.leader_tagged
            leader.solved_problems += 1
            leader.save()
            
        # Check for Leader Action: Leader resolved but user hasn't confirmed yet
        elif (instance.is_leader_resolved and 
              not instance.is_user_confirmed and 
              instance.status != 'pending_confirm'):
            
            instance.status = 'pending_confirm'
        
        # Save the issue with updated status
        if instance.status in ['solved', 'pending_confirm']:
            # Use update_fields to avoid triggering the signal again
            Issue.objects.filter(pk=instance.pk).update(status=instance.status)
            
    finally:
        # Reconnect the signal
        post_save.connect(handle_issue_resolution, sender=Issue)
