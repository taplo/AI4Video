#!/usr/bin/env python

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'framework.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Auto-migrate on runserver/runworker (D-19, D-20)
    if len(sys.argv) > 1 and sys.argv[1] in ('runserver', 'runworker'):
        try:
            from django.core.management import call_command
            call_command('migrate', '--run-syncdb', verbosity=0)
        except Exception as e:
            print(f"Auto-migrate failed: {e}")

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
