# MyCity Resolve

A Django-based civic engagement platform that connects citizens with city leaders to resolve community issues through a two-step verification process.

## Features

- **Issue Submission**: Citizens can submit issues with photos and precise location data using Google Maps
- **AI Content Moderation**: Automatic filtering of spam and inappropriate content
- **Two-Step Resolution**: Leaders mark issues as resolved, citizens confirm the resolution
- **Community Flagging**: Users can flag issues as unsolved for accountability
- **Gamified Leaderboard**: Track which leaders are solving the most problems
- **Anonymous Posting**: Citizens remain anonymous while maintaining accountability
- **Admin Dashboard**: Full management interface for data oversight

## Quick Start

### 1. Install Dependencies
```bash
pip install Django Pillow
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Load Sample Data
```bash
python manage.py load_sample_data
```

### 5. Map Integration (No API Key Required!)
The application uses OpenStreetMap with Leaflet.js - completely free with no API key required!

### 6. Run Development Server
```bash
python manage.py runserver
```

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
