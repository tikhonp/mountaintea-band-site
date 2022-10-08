git pull origin main || exit
pip install -r requirements.txt
./manage.py makemigrations
./manage.py migrate
./manage.py collectstatic
sudo systemctl restart gunicorn || exit
sudo systemctl status gunicorn || exit
