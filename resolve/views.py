from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .models import Issue, Leader, CitizenProfile
from .forms import IssueForm
from .ai_utils import check_content_safety


def home(request):
    """Home page with links to main features"""
    return render(request, 'resolve/home.html')


def signup(request):
    """User self-service registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'resolve/signup.html', {'form': form})


def issue_feed(request):
    """Display all issues in a social media style feed"""
    issues = Issue.objects.all().order_by('-created_at')
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
                    'Your post was flagged for potentially violating our community guidelines and could not be submitted.')
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
            messages.success(request, 'Your issue has been submitted successfully!')
            return redirect('issue_feed')
    else:
        form = IssueForm()
    
    context = {
        'form': form
    }
    return render(request, 'resolve/issue_submit.html', context)


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
    context = {
        'issues': issues
    }
    return render(request, 'resolve/my_issues.html', context)