# RobuxKingdomDjango

This repository now contains a Django project with a `main` application. The existing HTML layout is served through Django for further development.

## Quick start

Install dependencies (Django 5.x is required) and run migrations:

```bash
pip install -r requirements.txt  # or `pip install django`
python manage.py migrate
```

Launch the development server:

```bash
python manage.py runserver
```

The home page uses the layout in `robux_head_pc/index.html` and static files are served directly from the repository.
