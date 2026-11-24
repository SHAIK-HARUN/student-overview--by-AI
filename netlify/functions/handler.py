import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_portal.settings')

# Ensure migrations are applied in serverless environment
try:
    import django
    django.setup()
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Serverless migration setup info: {e}")

from student_portal.wsgi import application
from mangum import Mangum

# Mangum wraps ASGI/WSGI applications to run on AWS Lambda / Netlify Functions
handler = Mangum(application)
