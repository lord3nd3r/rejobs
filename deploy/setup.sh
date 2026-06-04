#!/bin/bash
# deploy/setup.sh — First-time VPS setup for Re Jobs
# Run as root or with sudo

set -euo pipefail

APP_USER="rejobs"
APP_DIR="/home/$APP_USER/app"
VENV_DIR="/home/$APP_USER/venv"

echo "=== Creating system user ==="
id -u $APP_USER &>/dev/null || useradd --system --create-home --shell /bin/bash $APP_USER

echo "=== Installing system packages ==="
apt-get update -qq
apt-get install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx certbot python3-certbot-nginx

echo "=== Creating directories ==="
mkdir -p /var/log/rejobs
chown $APP_USER:www-data /var/log/rejobs

echo "=== Creating virtualenv ==="
sudo -u $APP_USER python3.12 -m venv $VENV_DIR
sudo -u $APP_USER $VENV_DIR/bin/pip install --upgrade pip

echo "=== Installing Python dependencies ==="
sudo -u $APP_USER $VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt

echo "=== Collecting static files ==="
cd $APP_DIR
sudo -u $APP_USER DJANGO_SETTINGS_MODULE=config.settings.production $VENV_DIR/bin/python manage.py collectstatic --noinput

echo "=== Running migrations ==="
sudo -u $APP_USER DJANGO_SETTINGS_MODULE=config.settings.production $VENV_DIR/bin/python manage.py migrate

echo "=== Installing systemd service ==="
cp $APP_DIR/deploy/gunicorn.service /etc/systemd/system/rejobs.service
systemctl daemon-reload
systemctl enable rejobs
systemctl start rejobs

echo "=== Installing nginx config ==="
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/rejobs
ln -sf /etc/nginx/sites-available/rejobs /etc/nginx/sites-enabled/rejobs
nginx -t && systemctl reload nginx

echo ""
echo "=== DONE. Run: sudo certbot --nginx -d your-domain.com ==="
