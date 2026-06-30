"""
PythonAnywhere WSGI configuration file.

Place this content in the WSGI file at:
    /var/www/<yourusername>_pythonanywhere_com_wsgi.py

Configured via the Web tab -> Code -> WSGI configuration file.
"""
import os
import sys

# Add your project directory to the Python path
path = os.path.join(os.environ.get("HOME", ""), "Real-time-Chat-Application")
if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "django_project.settings_production"

# PythonAnywhere sets SECRET_KEY via a secret in the Web tab
# or via a file that you create:
# os.environ["SECRET_KEY"] = open(
#     os.path.join(os.environ["HOME"], ".secrets", "django_secret_key.txt")
# ).read().strip()

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
