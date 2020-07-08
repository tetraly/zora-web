# ZORA (Zelda One Randomizer for All)


[add text here]

For most users, go to [link] to . If you're a tech-savy user and want to run a ZORA server locally, follow these instructions:

## Install Python

This app is written in Python 3, which is sort of implied by the requirements since Django 2.0 and beyond doesn't support Python 2 any longer.  You should install the latest version of Python 3 on your system, [instructions available on the official site](https://www.python.org).

## Installing required packages

I would recommend making a virtual environment using something like virtualenv, or Pipenv.  Then install the required packages:

```> pip install -r requirements.txt```

## Setting up

1. Make a copy of `example_local.py` and call it `local_settings.py`. This is where you will enter any deployment-specific settings for your instance of the website.

   ```> cp example_local.py local_settings.py```

1. Change `local_settings.py` as needed.  Generally the only thing that would be different in your deployment is the database settings.  The default is a local SQLite file.  This is fine for local development, but I recommend something more robust for production, ex. PostgreSQL.

1. Run all migrations for your database:

   ```> python manage.py migrate```

1. Collect all the static files as per standard Django deployment:

   ```> python manage.py collectstatic```

1. Set up your Django web server however you prefer.  There are plenty of resources out there on this topic for production, but for a local development environment you can just run the local test server as normal:

   ```> python manage.py runserver```
