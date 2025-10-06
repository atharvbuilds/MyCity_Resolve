from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from resolve.models import Leader, Issue
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Load sample data for MyCity Resolve'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')
        
        # Create sample leaders
        leaders_data = [
            {
                'name': 'Mayor Sarah Johnson',
                'designation': 'Mayor',
                'solved_problems': 15,
            },
            {
                'name': 'Council Member Mike Chen',
                'designation': 'City Council Member',
                'solved_problems': 12,
            },
            {
                'name': 'Council Member Lisa Rodriguez',
                'designation': 'City Council Member',
                'solved_problems': 8,
            },
            {
                'name': 'Public Works Director Tom Wilson',
                'designation': 'Public Works Director',
                'solved_problems': 20,
            },
            {
                'name': 'Parks Commissioner Jane Davis',
                'designation': 'Parks Commissioner',
                'solved_problems': 6,
            }
        ]
        
        leaders = []
        for leader_data in leaders_data:
            leader, created = Leader.objects.get_or_create(
                name=leader_data['name'],
                defaults=leader_data
            )
            leaders.append(leader)
            if created:
                self.stdout.write(f'Created leader: {leader.name}')
        
        # Create sample users if they don't exist
        sample_users = []
        for i in range(1, 6):
            username = f'citizen{i}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'Citizen',
                    'last_name': f'{i}',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {username}')
            sample_users.append(user)
        
        # Create sample issues
        sample_issues = [
            {
                'title': 'Pothole on Main Street',
                'description': 'Large pothole causing damage to vehicles. Located near intersection with Oak Avenue.',
                'latitude': Decimal('40.7128'),
                'longitude': Decimal('-74.0060'),
                'leader': leaders[0],  # Mayor
                'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400',
            },
            {
                'title': 'Broken Streetlight',
                'description': 'Streetlight has been out for 3 days on Elm Street. Dark area is a safety concern.',
                'latitude': Decimal('40.7589'),
                'longitude': Decimal('-73.9851'),
                'leader': leaders[1],  # Council Member
                'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400',
            },
            {
                'title': 'Garbage Collection Missed',
                'description': 'Garbage wasn\'t collected on our street this week. Bins are overflowing.',
                'latitude': Decimal('40.7505'),
                'longitude': Decimal('-73.9934'),
                'leader': leaders[3],  # Public Works Director
                'image': 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=400',
            },
            {
                'title': 'Park Bench Needs Repair',
                'description': 'Bench in Central Park is broken and unsafe for use.',
                'latitude': Decimal('40.7829'),
                'longitude': Decimal('-73.9654'),
                'leader': leaders[4],  # Parks Commissioner
                'image': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400',
            },
            {
                'title': 'Traffic Signal Malfunction',
                'description': 'Traffic light at 5th and Broadway is stuck on red in all directions.',
                'latitude': Decimal('40.7614'),
                'longitude': Decimal('-73.9776'),
                'leader': leaders[2],  # Council Member
                'image': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400',
            },
            {
                'title': 'Sidewalk Crack',
                'description': 'Large crack in sidewalk on Pine Street making it difficult for wheelchair access.',
                'latitude': Decimal('40.7505'),
                'longitude': Decimal('-73.9934'),
                'leader': leaders[1],  # Council Member
                'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400',
            }
        ]
        
        for i, issue_data in enumerate(sample_issues):
            # Randomly assign some issues as resolved
            is_leader_resolved = random.choice([True, False])
            is_user_confirmed = is_leader_resolved and random.choice([True, False])
            
            if is_leader_resolved and is_user_confirmed:
                status = 'solved'
            elif is_leader_resolved:
                status = 'pending_confirm'
            else:
                status = 'open'
            
            issue, created = Issue.objects.get_or_create(
                title=issue_data['title'],
                defaults={
                    'description': issue_data['description'],
                    'user': sample_users[i % len(sample_users)],
                    'leader_tagged': issue_data['leader'],
                    'latitude': issue_data['latitude'],
                    'longitude': issue_data['longitude'],
                    'status': status,
                    'is_leader_resolved': is_leader_resolved,
                    'is_user_confirmed': is_user_confirmed,
                    'flag_count': random.randint(0, 3),
                }
            )
            if created:
                self.stdout.write(f'Created issue: {issue.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded sample data!')
        )
        self.stdout.write('Sample login credentials:')
        self.stdout.write('Admin: admin / password (you set this)')
        self.stdout.write('Citizens: citizen1, citizen2, etc. / password123')
