from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, F
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.utils import timezone
from django.db.models.functions import Power, Sqrt
from .models import Issue, Leader, CitizenProfile, Comment, Hashtag, Notification
from .forms import IssueForm, SignupForm, CommentForm, HashtagForm
from .utils import process_hashtags, format_hashtags
from .ai_utils import check_content_safety


def home(request):
    """Home page with links to main features"""
    return render(request, 'resolve/home.html')


def signup(request):
    """User self-service registration with hometown selection"""
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'resolve/signup.html', {'form': form})


from django.db.models import F
from django.db.models.functions import Power, Sqrt

def issue_feed(request):
    """Display issues in a social media style feed with location-based recommendations"""
    issues = Issue.objects.all()
    
    # If user is authenticated and has hometown location set, sort by distance
    if request.user.is_authenticated:
        try:
            profile = CitizenProfile.objects.get(user=request.user)
            if profile.hometown_latitude and profile.hometown_longitude:
                # Calculate distance using the Pythagorean theorem
                # This is a simplified distance calculation, good enough for sorting by relative distance
                issues = issues.annotate(
                    distance=Sqrt(
                        Power(F('latitude') - profile.hometown_latitude, 2) +
                        Power(F('longitude') - profile.hometown_longitude, 2)
                    )
                ).order_by('distance', '-created_at')
            else:
                issues = issues.order_by('-created_at')
        except CitizenProfile.DoesNotExist:
            issues = issues.order_by('-created_at')
    else:
        issues = issues.order_by('-created_at')
    
    context = {
        'issues': issues
    }
    return render(request, 'resolve/issue_feed.html', context)


def leaderboard(request):
    """Display leaderboard of leaders sorted by solved problems"""
    leaders = Leader.objects.all().order_by('-solved_problems')
    context = {
        'leaders': leaders
    }
    return render(request, 'resolve/leaderboard.html', context)


@login_required
def submit_issue(request):
    """Handle issue submission with AI content moderation"""
    if request.method == 'POST':
        form = IssueForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the cleaned data
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            
            # Check content safety using AI moderation
            title_safe = check_content_safety(title)
            description_safe = check_content_safety(description)
            
            if title_safe == 'FALSE_OR_ABUSIVE' or description_safe == 'FALSE_OR_ABUSIVE':
                messages.error(request, 
                    'Your post was flagged for potentially violating our community guidelines.')
                return render(request, 'resolve/issue_submit.html', {'form': form})
            
            # Create the issue
            issue = form.save(commit=False)
            issue.user = request.user
            
            # Get coordinates from hidden form fields
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if latitude and longitude:
                issue.latitude = float(latitude)
                issue.longitude = float(longitude)
            else:
                messages.error(request, 'Please select a location on the map.')
                return render(request, 'resolve/issue_submit.html', {'form': form})
            
            issue.save()
            
            # Process hashtags in description
            if description:
                process_hashtags(description, issue)
            
            messages.success(request, 'Your issue has been submitted successfully!')
            return redirect('issue_feed')
    else:
        form = IssueForm()
    
    context = {
        'form': form,
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'resolve/issue_submit.html', context)

@login_required
@require_POST
def toggle_like(request, issue_id):
    """Toggle like status for an issue"""
    issue = get_object_or_404(Issue, id=issue_id)
    if issue.likes.filter(id=request.user.id).exists():
        issue.likes.remove(request.user)
        liked = False
    else:
        issue.likes.add(request.user)
        liked = True
        if request.user != issue.user:
            Notification.objects.create(
                recipient=issue.user,
                sender=request.user,
                notification_type='like',
                issue=issue,
                text=f"{request.user.username} liked your issue."
            )
    return JsonResponse({
        'liked': liked,
        'like_count': issue.likes.count()
    })

@login_required
@require_POST
def toggle_bookmark(request, issue_id):
    """Toggle bookmark status for an issue"""
    issue = get_object_or_404(Issue, id=issue_id)
    if issue.bookmarks.filter(id=request.user.id).exists():
        issue.bookmarks.remove(request.user)
        bookmarked = False
    else:
        issue.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({
        'bookmarked': bookmarked,
        'bookmark_count': issue.bookmarks.count()
    })

@login_required
def add_comment(request, issue_id):
    """Add a comment to an issue"""
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.issue = issue
            
            # Check content safety
            content_safe = check_content_safety(comment.content)
            if content_safe == 'FALSE_OR_ABUSIVE':
                messages.error(request, 'Your comment was flagged for potentially violating our community guidelines.')
                return redirect('issue_detail', pk=issue_id)
            
            comment.save()
            
            # Process hashtags in comment
            process_hashtags(comment.content, issue)
            
            # Create notification
            if request.user != issue.user:
                Notification.objects.create(
                    recipient=issue.user,
                    sender=request.user,
                    notification_type='comment',
                    issue=issue,
                    comment=comment,
                    text=f"{request.user.username} commented on your issue."
                )
            
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'username': request.user.username,
                'content': format_hashtags(comment.content),
                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M')
            })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def add_reply(request, comment_id):
    """Add a reply to a comment"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.issue = parent_comment.issue
            reply.parent = parent_comment
            
            # Check content safety
            content_safe = check_content_safety(reply.content)
            if content_safe == 'FALSE_OR_ABUSIVE':
                messages.error(request, 'Your reply was flagged for potentially violating our community guidelines.')
                return redirect('issue_detail', pk=parent_comment.issue.id)
            
            reply.save()
            
            # Create notification
            if request.user != parent_comment.user:
                Notification.objects.create(
                    recipient=parent_comment.user,
                    sender=request.user,
                    notification_type='comment',
                    issue=parent_comment.issue,
                    comment=reply,
                    text=f"{request.user.username} replied to your comment."
                )
            
            return JsonResponse({
                'status': 'success',
                'reply_id': reply.id,
                'username': request.user.username,
                'content': format_hashtags(reply.content),
                'created_at': reply.created_at.strftime('%b %d, %Y %H:%M')
            })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def hashtag_view(request, tag_name):
    """Display issues with a specific hashtag"""
    hashtag = get_object_or_404(Hashtag, name=tag_name)
    issues = Issue.objects.filter(hashtags=hashtag).order_by('-created_at')
    return render(request, 'resolve/hashtag_feed.html', {
        'hashtag': hashtag,
        'issues': issues
    })


@login_required
def leader_resolve(request, issue_id):
    """Allow leaders to mark an issue as resolved"""
    issue = get_object_or_404(Issue, id=issue_id)
    
    # Check if the current user is the tagged leader
    if not hasattr(request.user, 'leader') or request.user.leader != issue.leader_tagged:
        messages.error(request, 'You are not authorized to resolve this issue.')
        return redirect('issue_feed')
    
    # Mark as resolved by leader
    issue.is_leader_resolved = True
    issue.save()
    
    messages.success(request, f'You have marked the issue "{issue.title}" as resolved. Waiting for user confirmation.')
    return redirect('issue_feed')


@login_required
def user_confirm(request, issue_id):
    """Allow users to confirm that their issue has been resolved"""
    issue = get_object_or_404(Issue, id=issue_id)
    
    # Check if the current user is the issue owner
    if issue.user != request.user:
        messages.error(request, 'You are not authorized to confirm this issue.')
        return redirect('issue_feed')
    
    # Mark as confirmed by user
    issue.is_user_confirmed = True
    issue.save()
    
    messages.success(request, f'Thank you for confirming that "{issue.title}" has been resolved!')
    return redirect('issue_feed')


@require_POST
@csrf_exempt
def flag_issue(request, issue_id):
    """Allow users to flag an issue as unsolved"""
    issue = get_object_or_404(Issue, id=issue_id)
    issue.flag_count += 1
    issue.save()
    
    return JsonResponse({
        'success': True,
        'flag_count': issue.flag_count,
        'message': 'Issue flagged successfully'
    })


@login_required
def my_issues(request):
    """Display user's own issues"""
    issues = Issue.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'resolve/my_issues.html', {'issues': issues})


@login_required
def activity_feed(request):
    """Display user's activity feed and notifications"""
    # Get user's notifications
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:50]
    
    # Get trending hashtags from the last 7 days
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    
    trending_hashtags = Hashtag.objects.filter(
        issue__created_at__gte=seven_days_ago
    ).annotate(
        issue_count=Count('issue')
    ).order_by('-issue_count')[:10]
    
    return render(request, 'resolve/activity_feed.html', {
        'notifications': notifications,
        'trending_hashtags': trending_hashtags
    })


@login_required
def explore(request):
    """Display explore page with trending and recent issues"""
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    
    # Handle search
    search_query = request.GET.get('q')
    if search_query:
        # Search in title, description, and hashtags
        issues = Issue.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(hashtags__name__icontains=search_query)
        ).distinct().order_by('-created_at')
        return render(request, 'resolve/explore.html', {
            'issues': issues,
            'search_query': search_query
        })
    
    # Get trending issues (most likes and comments in the last 7 days)
    trending_issues = Issue.objects.filter(
        created_at__gte=seven_days_ago
    ).annotate(
        engagement_score=Count('likes') + Count('comments')
    ).order_by('-engagement_score')[:10]
    
    # Get recent issues
    recent_issues = Issue.objects.order_by('-created_at')[:10]
    
    # Get trending hashtags
    trending_hashtags = Hashtag.objects.filter(
        issue__created_at__gte=seven_days_ago
    ).annotate(
        issue_count=Count('issue')
    ).order_by('-issue_count')[:10]
    
    # Get most active users
    active_users = CitizenProfile.objects.filter(
        user__issue__created_at__gte=seven_days_ago
    ).annotate(
        issue_count=Count('user__issue')
    ).order_by('-issue_count')[:10]
    
    return render(request, 'resolve/explore.html', {
        'trending_issues': trending_issues,
        'recent_issues': recent_issues,
        'trending_hashtags': trending_hashtags,
        'active_users': active_users
    })


@login_required
@require_POST
def toggle_like(request, issue_id):
    """Toggle like status for an issue"""
    issue = get_object_or_404(Issue, id=issue_id)
    if issue.likes.filter(id=request.user.id).exists():
        issue.likes.remove(request.user)
        liked = False
    else:
        issue.likes.add(request.user)
        liked = True
        if request.user != issue.user:
            Notification.objects.create(
                recipient=issue.user,
                sender=request.user,
                notification_type='like',
                issue=issue,
                text=f"{request.user.username} liked your issue."
            )
    return JsonResponse({
        'liked': liked,
        'like_count': issue.likes.count()
    })


@login_required
@require_POST
def toggle_bookmark(request, issue_id):
    """Toggle bookmark status for an issue"""
    issue = get_object_or_404(Issue, id=issue_id)
    if issue.bookmarks.filter(id=request.user.id).exists():
        issue.bookmarks.remove(request.user)
        bookmarked = False
    else:
        issue.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({
        'bookmarked': bookmarked,
        'bookmark_count': issue.bookmarks.count()
    })


@login_required
def add_comment(request, issue_id):
    """Add a comment to an issue"""
    issue = get_object_or_404(Issue, id=issue_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.issue = issue
            
            # Check content safety
            content_safe = check_content_safety(comment.content)
            if content_safe == 'FALSE_OR_ABUSIVE':
                messages.error(request, 'Your comment was flagged for potentially violating our community guidelines.')
                return redirect('issue_detail', pk=issue_id)
            
            comment.save()
            
            # Process hashtags in comment
            process_hashtags(comment.content, issue)
            
            # Create notification
            if request.user != issue.user:
                Notification.objects.create(
                    recipient=issue.user,
                    sender=request.user,
                    notification_type='comment',
                    issue=issue,
                    comment=comment,
                    text=f"{request.user.username} commented on your issue."
                )
            
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'username': request.user.username,
                'content': format_hashtags(comment.content),
                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M')
            })
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def add_reply(request, comment_id):
    """Add a reply to a comment"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.issue = parent_comment.issue
            reply.parent = parent_comment
            
            # Check content safety
            content_safe = check_content_safety(reply.content)
            if content_safe == 'FALSE_OR_ABUSIVE':
                messages.error(request, 'Your reply was flagged for potentially violating our community guidelines.')
                return redirect('issue_detail', pk=parent_comment.issue.id)
            
            reply.save()
            
            # Create notification
            if request.user != parent_comment.user:
                Notification.objects.create(
                    recipient=parent_comment.user,
                    sender=request.user,
                    notification_type='comment',
                    issue=parent_comment.issue,
                    comment=reply,
                    text=f"{request.user.username} replied to your comment."
                )
            
            return JsonResponse({
                'status': 'success',
                'reply_id': reply.id,
                'username': request.user.username,
                'content': format_hashtags(reply.content),
                'created_at': reply.created_at.strftime('%b %d, %Y %H:%M')
            })
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def hashtag_view(request, tag_name):
    """Display issues with a specific hashtag"""
    hashtag = get_object_or_404(Hashtag, name=tag_name)
    issues = Issue.objects.filter(hashtags=hashtag).order_by('-created_at')
    return render(request, 'resolve/hashtag_feed.html', {
        'hashtag': hashtag,
        'issues': issues
    })