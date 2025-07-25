"""
Django settings for robuxsite project.

Generated by 'django-admin startproject' using Django 5.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
from django.templatetags.static import static
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'

# Для разработки: дополнительные папки, где Django будет искать статику
STATICFILES_DIRS = [
    BASE_DIR / 'static',            # например, проект/static/
    # BASE_DIR / 'app_name' / 'static',  # можно ещё папки приложений
]

# Для продакшена: куда собирать все файлы командой collectstatic
STATIC_ROOT = BASE_DIR / 'static'  # например, проект/staticfiles/


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-do2-jmm4qfs^jcow988z0m$4@tg4#q8^0u^rhglll*-c6=!9nc"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'corsheaders',
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
]

UNFOLD = {
    # Принудительная тема: 'light' или 'dark'
    "THEME": "dark",

    # Переопределяем цвета
    "COLORS": {
        # Ваш фирменный жёлтый
        "primary": {
            "500": "255, 184, 0",    # #FFB800
        },
        # Фон (базовый) — тёмно‑синий
        "base": {
            "900": "10, 13, 27",     # #0A0D1B
        },
        # Цвета текста под ваши тона
        "font": {
            "default-light":  "var(--color-base-900)",    # основной текст
            "important-dark":"var(--color-primary-500)", # акцентный текст
        },
    },

    # Подключаем ваш скомпилированный CSS
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
}

CORS_ALLOW_ALL_ORIGINS = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',   # <- обязательно первым
    'django.middleware.common.CommonMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "robuxsite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "robuxsite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# FreeKassa configuration
FREEKASSA_MERCHANT_ID = os.getenv("FREEKASSA_MERCHANT_ID", "")
FREEKASSA_SECRET_1 = os.getenv("FREEKASSA_SECRET_1", "")
FREEKASSA_SECRET_2 = os.getenv("FREEKASSA_SECRET_2", "")
