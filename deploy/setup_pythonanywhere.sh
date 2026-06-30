#!/bin/bash
# PythonAnywhere free-plan deployment setup script
# Run this from a PythonAnywhere Bash console after cloning the repo.

# --- Configuration (change these) ---
REPO_DIR="$HOME/Real-time-Chat-Application"
DJANGO_SETTINGS_MODULE="django_project.settings_production"
PA_DOMAIN="yourusername.pythonanywhere.com"  # set to your actual domain

# --- 1. Create virtualenv and install dependencies ---
cd "$REPO_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_production.txt

# --- 2. Generate a secure SECRET_KEY and store it ---
mkdir -p "$HOME/.secrets"
python3 -c "
import secrets, string
key = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*()') for _ in range(64))
with open('$HOME/.secrets/django_secret_key.txt', 'w') as f:
    f.write(key)
print('Secret key saved to ~/.secrets/django_secret_key.txt')
"

# --- 3. Run migrations ---
python manage.py migrate --settings="$DJANGO_SETTINGS_MODULE"

# --- 4. Collect static files ---
python manage.py collectstatic --settings="$DJANGO_SETTINGS_MODULE" --noinput

# --- 5. Create superuser (interactive) ---
echo "Creating superuser (follow the prompts)..."
python manage.py createsuperuser --settings="$DJANGO_SETTINGS_MODULE"

# --- 6. Create media and logs directories ---
mkdir -p "$HOME/media"
mkdir -p "$HOME/logs"

# --- 7. Post-setup instructions ---
echo ""
echo "============================================="
echo "Setup complete! Next steps in the Web tab:"
echo "============================================="
echo "1. Go to the Web tab and create a new web app"
echo "2. Manual configuration -> Python 3.x"
echo "3. Source code: $REPO_DIR"
echo "4. Working directory: $REPO_DIR"
echo "5. Virtualenv: $REPO_DIR/venv"
echo "6. WSGI config file: $REPO_DIR/deploy/pythonanywhere_wsgi.py"
echo "   (copy content to the WSGI file)"
echo "7. Static files:"
echo "   URL: /static/   Directory: $HOME/staticfiles"
echo "   URL: /media/    Directory: $HOME/media"
echo "8. Environment variables (in WSGI file):"
echo "   SECRET_KEY: read from ~/.secrets/django_secret_key.txt"
echo "   PYTHONANYWHERE_DOMAIN: $PA_DOMAIN"
echo "9. Reload web app"
echo ""
echo "NOTE: WebSockets are not supported on the free plan."
echo "The chat app will fall back to HTTP POST for sending messages."
echo "============================================="
