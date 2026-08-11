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

    # Auto-migrate on runserver/runworker (D-19, D-20).
    # 迁移失败必须中止启动（WR-04），否则服务在 schema 不匹配的库上静默运行。
    if len(sys.argv) > 1 and sys.argv[1] in ('runserver', 'runworker'):
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', verbosity=1)  # 异常向上抛，中止启动

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
