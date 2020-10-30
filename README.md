# ZORA (Zelda One Randomizer for All)

This is the source code repositiory for the ZORA randomizer. For more information and to generate seeds using the web UI, go to https://zora.tetra.ly 

If you're familiar with programming in Python and want to run ZORA locally or contribute to it, follow these instructions. If you're stuck or have questions, feel free to ask @tetraly on Twitter or tetraly#1131 on Discord.

## Install Python

This app is written in Python 3, which is sort of implied by the requirements since Django 2.0 and beyond no longer support Python 2.  You should install the latest version of Python 3 on your system, [instructions available on the official site](https://www.python.org).

## Installing required packages

I would recommend making a virtual environment using something like virtualenv, or Pipenv.  Then install the required packages:

```> pip install -r requirements.txt```

## Running the command line interface

To create a seed from the command line, run the following command:

```>  python zora_cli.py --input_filename="[ROM filename]" --flag_string="[flags]" --seed=[seed number]```

For example: 

```>  python zora_cli.py --input_filename="/path/to/my-zelda-rom.nes" --flag_string="C Hz F T Xblst" --seed=12345```

## Running the webserver locally

1. Make a copy of `example_local.py` and call it `local_settings.py`. This is where you will enter any deployment-specific settings for your instance of the website.

   ```> cp example_local.py local_settings.py```

1. Change `local_settings.py` as needed.  Generally the only thing that would be different in your deployment is the database settings.  The default is a local SQLite file.  This is fine for local development, but I recommend something more robust for production, ex. PostgreSQL.

1. Run all migrations for your database:

   ```> python manage.py migrate```

1. Collect all the static files as per standard Django deployment:

   ```> python manage.py collectstatic```

1. Set up your Django web server however you prefer.  There are plenty of resources out there on this topic for production, but for a local development environment you can just run the local test server as normal:

   ```> python manage.py runserver```
