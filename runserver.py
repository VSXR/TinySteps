import os
import sys
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
os.environ['PYTHONIOENCODING'] = 'utf-8'

def print_header():
    print("═══════════════════════════════════════════════════")
    print("▶ TinySteps Development Server Starting")
    print("═══════════════════════════════════════════════════")

# python runserver.py 0:8080 --noreload
if __name__ == '__main__':
    django.setup()
    print_header()
    run_args = ['manage.py', 'runserver']
    
    if len(sys.argv) > 1:
        run_args.extend(sys.argv[1:])
    execute_from_command_line(run_args)