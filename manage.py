#!/usr/bin/env python
import os
import sys
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

    try:
        execute_from_command_line(sys.argv)
    except Exception as exc:
        raise exc

if __name__ == '__main__':
    main()
