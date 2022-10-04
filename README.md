# mountainteaband.ru

Сайт группы "Горный Чай" с продажей билетов

### Installation

```bash
sudo apt update
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```

Создание базы данных

```
sudo -u postgres psql
CREATE DATABASE gornijchaij;
CREATE USER gornijchaijuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE gornijchaij TO gornijchaijuser;
\q
```

Установка зависимостей python

```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv
python3 -m venv env; . env/bin/activate
pip install django gunicorn psycopg2-binary
```

Создание сокета

```
sudo vim /etc/systemd/system/gunicorn.socket

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

```
sudo vim /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/home/tikhon/gornijchaij
ExecStart=/home/tikhon/gornijchaij/env/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          gornijchaij.wsgi:application

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

```
sudo systemctl status gunicorn.socket
file /run/gunicorn.sock
curl --unix-socket /run/gunicorn.sock localhost
sudo systemctl status gunicorn
```

### TODO
