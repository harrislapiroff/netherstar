#!/usr/bin/env sh
./manage.py migrate --settings config.settings
./manage.py runserver 0.0.0.0:8000 --settings config.settings
