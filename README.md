# gornijchaij
Официальный сайт группы "Горный Чай"

### TODO
- ~~Добавить рассылку сообщений с qr кодом и возможность сканирования их и отметки как пройденные~~
- Добавить рассылку с qr кодом, код уже есть
- Заново сверстать емайлы
- Переименовать Горный Чай ltd в горный чай
- Добавить время концерта
- Добавить форму для бесплатного билета в стаф
- Добавить поле для ввода номера билета
- Изменить описание про выход альбома

### Email fix

```
Атрибуты Alt обеспечивают текстовую альтернативу Вашим изображениям.
Это полезный обходной путь для людей, страдающих от проблем со зрением и для случаев, когда Ваше изображение не может быть отображено.
<img src="https://mountainteaband.ru/static/email/ticket_bottom.png" height="10" width="600" class="mcnImage" style="display: block;max-width: 600px;border:
<img src="https://mountainteaband.ru/static/email/ticket_bottom.png" height="10" width="600" class="mcnImage" style="display: block;max-width: 600px;border:
Если вы не хотите заполнять атрибут alt, выставите его как пустое значение: alt=""
```

```
[404 - Error : Not found] https://mountainteaband.ru/concerts/email/
```

### Скрипт для установки будет:

```bash
sudo apt update
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```

```
sudo -u postgres psql
CREATE DATABASE myproject;
CREATE USER myprojectuser WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;
\q
```

```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv
pip install django gunicorn psycopg2-binary
```
```
sudo nano /etc/systemd/system/gunicorn.socket

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

```
sudo nano /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/home/sammy/myprojectdir
ExecStart=/home/sammy/myprojectdir/myprojectenv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          myproject.wsgi:application

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



