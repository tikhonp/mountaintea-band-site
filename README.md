<div align="center">
  <br>
  <h1> 🎸 mountainteaband.ru</h1>
</div>

Welcome to the [mountainteaband.ru](https://mountainteaband.ru) codebase.
We're little musicians from Russia, who love to play music and share it with the world.

[mountainteaband.ru](https://mountainteaband.ru) is a service for the sale of tickets and event announcements.

## 🛠 Tech stack

💻 **TL;DR: Django, Postgres, Vue.js**

The trickiest part of our stack is how we develop the frontend and backend as a single service. We don't use SPA, as many people do, but only make parts of the page dynamic by inserting Vue.js components directly into Django templates. This may seem weird, but it actually makes it very easy for one person to develop and maintain the entire site.

## 🔮 Installing and running locally

1. Clone the repo

    ```sh
    $ git clone https://github.com/TikhonP/mountaintea-band-site.git
    $ cd mountaintea_band_site
    ```

2. Assuming that you have Python and virtualenv installed, set up your environment and install the required dependencies

    ```sh
    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory of the project and add the environment variables from `.env_example` to it

4. Export the environment variable, make and run the migrations

    ```sh
    $ export DJANGO_SETTINGS_MODULE=mountaintea_band_site.settings.development
    $ python manage.py makemigrations
    $ python manage.py migrate
    ```

5. Run

    ```sh
    $ python manage.py runserver
    ```
   
This will start the application in development mode on [http://127.0.0.1:8000/](http://127.0.0.1:8000/) with _SQLite_ database. 

If you want to develop `/staff/qrcode/` page, you need to setup _Vue.js_ workspace:

1. Go to `qrcode_scanner_app_dev` directory

    ```sh
    $ cd qrcode_scanner_app_dev
    ```

2. Install and run:

    ```sh
    $ npm install
    $ npm run dev
    ```

## 🚢 Deployment

We're using simple _nginx_ + _gunicorn_ setup.

Installation for ubuntu and debian:

1. Install packages

    ```sh
    $ sudo apt update
    $ sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
    ```

2. Create postgres user and database

    ```sh
    $ sudo -u postgres psql
    postgres=# CREATE USER mountaintea_band_site_user WITH PASSWORD 'password';
    postgres=# ALTER ROLE mountaintea_band_site_user SET client_encoding TO 'utf8';
    postgres=# ALTER ROLE mountaintea_band_site_user SET default_transaction_isolation TO 'read committed';
    postgres=# ALTER ROLE mountaintea_band_site_user SET timezone TO 'Europe/Moscow';
    postgres=# CREATE DATABASE mountaintea_band_site_db;
    postgres=# GRANT ALL PRIVILEGES ON DATABASE mountaintea_band_site_db TO mountaintea_band_site_user;
    postgres=# \q
    ```

3. Set up _python_ environment and install the required dependencies

    ```sh
    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install -r requirements.txt
    ```

4. Create `.env` file in the root directory of the project and add the environment variables from `.env_example` to it

5. Export the environment variable, make and run the migrations

    ```sh
    $ export DJANGO_SETTINGS_MODULE=mountaintea_band_site.settings.production
    $ python manage.py makemigrations
    $ python manage.py migrate
    ```

6. Create gunicorn socket and service

    ```sh
    $ sudo vim /etc/systemd/system/gunicorn.socket
    ```

    ```sh
    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn.sock

    [Install]
    WantedBy=sockets.target
    ```

    ```sh
    $ sudo vim /etc/systemd/system/gunicorn.service
    ```

    ```sh
    [Unit]
    Description=gunicorn daemon
    Requires=gunicorn.socket
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/mountaintea-band-site
    ExecStart=/home/ubuntu/mountaintea-band-site/env/bin/gunicorn \
              --access-logfile - \
              --workers 3 \
              --bind unix:/run/gunicorn.sock \
              mountaintea_band_site.wsgi:application

    [Install]
    WantedBy=multi-user.target
    ```

    ```sh
    $ sudo systemctl start gunicorn.socket
    $ sudo systemctl enable gunicorn.socket
    ```

7. Create nginx config from template file `nginx.conf` and put it to `/etc/nginx/sites-available/`

    ```sh
    $ sudo vim /etc/nginx/sites-available/mountaintea-band-site
    ```
    ```sh
    $ sudo ln -s /etc/nginx/sites-available/mountaintea-band-site /etc/nginx/sites-enabled
    $ sudo nginx -t
    $ sudo systemctl restart nginx
    $ sudo ufw delete allow 8000
    $ sudo ufw allow 'Nginx Full'
    ```
   
## 🔐 Security and vulnerabilities

If you think you've found a critical vulnerability that should not be exposed to the public yet, you can always email me directly by email: [tikhon.petrishchev@gmail.com](mailto:tikhon.petrishchev@gmail.com).

Please do not test vulnerabilities in public.

## 💼 License 

[MIT](LICENSE)

In other words, you can use the code for private and commercial purposes with an author attribution (by including the original license file).

Feel free to contact us via email [tikhon.petrishchev@gmail.com](mailto:tikhon.petrishchev@gmail.com).

❤️
