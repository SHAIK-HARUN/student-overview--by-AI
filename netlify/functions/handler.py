import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_portal.settings')

# Ensure Django setup and serverless migrations
import django
django.setup()

try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Serverless migration setup info: {e}")

from student_portal.wsgi import application
import serverless_wsgi

def handler(event, context):
    return serverless_wsgi.handle_wsgi(application, event, context)
