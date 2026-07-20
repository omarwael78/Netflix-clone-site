# Netflix Clone

A full-featured Netflix-inspired web application built with Django, featuring user authentication, movie browsing by genre, search functionality, personal watchlists, and a rich media dashboard.

Built by **Omar Wael** — Full Stack Developer (Python/Django)

---

## Features

- **User Authentication** — Sign up, sign in, and logout with session management
- **Movie Catalog** — Browse movies with card thumbnails, hover overlays, and quick-access play buttons
- **Genre Filtering** — Explore movies by 14 genres (Action, Comedy, Drama, Horror, Sci-Fi, etc.)
- **Search** — Real-time search across movie titles
- **My List** — Add/remove movies to a personal watchlist via AJAX
- **Featured Banner** — Dynamic hero section highlighting featured movies
- **Movie Detail Page** — Dedicated page with video player, metadata, and view counter
- **Responsive Design** — Fully responsive UI across desktop, tablet, and mobile
- **Admin Panel** — Django admin interface for managing movies and user lists

---

## Tech Stack

| Layer      | Technology                   |
|------------|------------------------------|
| Backend    | Python, Django 6.0           |
| Database   | SQLite3 (dev) / PostgreSQL   |
| Frontend   | HTML5, CSS3, JavaScript, jQuery |
| Styling    | Custom Netflix-themed CSS    |
| Server     | Gunicorn (production)        |
| Media      | Pillow for image handling    |

---

## Project Structure

```
netflix-clone/
├── core/                   # Main application
│   ├── management/         # Custom management commands
│   │   └── commands/
│   │       └── seed_data.py  # Database seeder (31 sample movies)
│   ├── migrations/         # Database migrations
│   ├── admin.py            # Admin panel configuration
│   ├── models.py           # Movie & MovieList models
│   ├── urls.py             # App URL routing
│   └── views.py            # All application views
├── media/                  # Uploaded media files
│   ├── movie_images/       # Movie posters & card images
│   └── movie_videos/       # Video files
├── netflix_site/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── static/                 # Static assets (CSS)
│   └── assets/
│       ├── style.css       # Main stylesheet
│       └── login.css       # Auth pages stylesheet
├── staticfiles/            # Collected static files (production)
├── templates/              # HTML templates
│   ├── index.html          # Home / dashboard
│   ├── login.html          # Sign in page
│   ├── signup.html         # Sign up page
│   ├── movie.html          # Movie detail + video player
│   ├── genre.html          # Genre-filtered browsing
│   ├── search.html         # Search results
│   └── my_list.html        # User's personal watchlist
├── manage.py               # Django CLI entry point
├── requirements.txt        # Python dependencies
└── Procfile                # Heroku deployment config
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/omarwael78/Netflix-clone-site.git
cd Netflix-clone-site

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed the database with sample movies
python manage.py seed_data

# Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Usage

1. **Sign up** for a new account or **sign in** if you already have one
2. Browse the movie catalog on the home page with horizontal scrollable rows
3. Click **Play** on any movie card to watch and view details
4. Use the **Genres** dropdown to filter by category
5. Add movies to **My List** by clicking the + button
6. Use the **Search** bar to find movies by title

---

## Admin Panel

Access the admin interface at `/admin` after creating a superuser:

```bash
python manage.py createsuperuser
```

Manage movies, view stats, mark movies as featured, and oversee user lists.

---

## Deployment

The app is configured for deployment on platforms like Heroku, Render, or Railway:

```bash
# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn netflix_site.wsgi:application --bind 0.0.0.0:$PORT
```

For PostgreSQL (production), uncomment the PostgreSQL database block in `netflix_site/settings.py` and configure your credentials.

---

## API Endpoints

| Endpoint          | Method | Description                        |
|-------------------|--------|------------------------------------|
| `/`               | GET    | Home page (requires login)         |
| `/login`          | GET/POST | User sign in                     |
| `/signup`         | GET/POST | User registration                |
| `/logout`         | GET    | Log out                            |
| `/movie/<uuid>/`  | GET    | Movie detail page                  |
| `/genre/<slug>/`  | GET    | Movies filtered by genre           |
| `/my-list`        | GET    | User's personal watchlist          |
| `/add-to-list`    | POST   | Add/remove movie from list (AJAX)  |
| `/search`         | POST   | Search movies by title             |

---

## License

This project is for educational purposes.

---

## Author

**Omar Wael** — Full Stack Developer (Python/Django)
