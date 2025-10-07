# MyCity Resolve

A Django-based civic engagement platform that connects citizens with city leaders to resolve community issues through a two-step verification process. Features include real-time chat, social interactions, and comprehensive issue tracking.

## Key Features

### Civic Engagement
- **Issue Submission**: Submit issues with photos and precise location data
- **Two-Step Resolution**: Leaders mark issues as resolved, citizens confirm
- **Community Flagging**: Users can flag issues as unsolved
- **Gamified Leaderboard**: Track leaders solving the most problems

### Social Features
- **User Profiles**: Customizable profiles with bio and stats
- **Follow System**: Follow other users and leaders
- **Real-time Chat**: Private messaging and group chats
- **Activity Feed**: See updates from followed users
- **Hashtags**: Organize and discover issues by topics

### Interactive Features
- **Like & Comment**: Engage with posted issues
- **Bookmarks**: Save important issues
- **Real-time Updates**: Get instant notifications
- **Explore Page**: Discover trending issues
- **Anonymous Posting**: Optional anonymous submissions

## Prerequisites

- Python 3.13+
- Django 5.2+
- Redis (optional, for production)

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/atharvbuilds/MyCity_Resolve.git
cd MyCity_Resolve
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply database migrations**
```bash
python manage.py migrate
```

5. **Create a superuser**
```bash
python manage.py createsuperuser
```

6. **Load sample data** (optional)
```bash
python manage.py load_sample_data
```

## Running the Application

1. **Start the development server**
```bash
python manage.py runserver
```

2. **Access the application**
- Main site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

Visit `http://127.0.0.1:8000` to see the application.

## Sample Login Credentials

- **Admin**: `admin` / `password` (you set this during superuser creation)
- **Citizens**: `citizen1`, `citizen2`, etc. / `password123`

## Project Structure

```
MyCityResolve/
├── manage.py
├── MyCityResolve/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py
├── resolve/                 # Main application
│   ├── models.py            # Leader, CitizenProfile, Issue models
│   ├── views.py             # All view functions
│   ├── forms.py             # Issue submission form
│   ├── admin.py             # Django admin configuration
│   ├── signals.py           # Two-step resolution logic
│   ├── ai_utils.py          # Content moderation
│   ├── urls.py              # App URL patterns
│   └── templates/resolve/   # HTML templates
└── static/                  # Static files
```

## Key Models

### Leader
- Public figures (Mayor, Council Members, etc.)
- Tracks solved problems count
- Can be linked to user accounts for login access

### CitizenProfile
- Private user data (real name, contact info)
- Automatically created when users register
- Only accessible to admins

### Issue
- Community complaints with location data
- Two-step resolution tracking
- Community flagging system

## Two-Step Resolution Process

1. **Citizen submits issue** → Status: "Open"
2. **Leader marks as resolved** → Status: "Pending Confirmation"
3. **Citizen confirms resolution** → Status: "Solved"
4. **Leader's solved count increments**

## Admin Features

Access the admin panel at `/admin/` to:
- Manage leaders and their user account links
- View all issues and their resolution status
- Monitor citizen profiles
- Track resolution statistics

## API Endpoints

- `/` - Home page
- `/feed/` - Issue feed (social media style)
- `/leaderboard/` - Leader rankings
- `/submit/` - Submit new issue (requires login)
- `/resolve/<id>/` - Leader resolution action
- `/confirm/<id>/` - User confirmation action
- `/flag/<id>/` - Community flagging
- `/my-issues/` - User's submitted issues

## Development Notes

- The application uses Django signals for automatic status updates
- Google Maps integration requires a valid API key
- AI moderation uses keyword filtering (can be extended with real AI APIs)
- All user uploads are stored in the `media/` directory
- Static files are served from the `static/` directory

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure media file serving
5. Set up proper logging
6. Use environment variables for sensitive settings

## License

This project is open source and available under the MIT License.
=======
# MyCity_Resolve
>>>>>>> 4d178275348fb5535c15ad5a9e324250230f2149
