from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "lolo_guide",
        "USER": "postgres",
        "PASSWORD": "lolo",
        "HOST": "127.0.0.1",
        "PORT": "5432",
        "OPTIONS": {"options": "-c search_path=public"},
    }
}