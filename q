[0;1;32m●[0m gunicorn.service - gunicorn daemon
   Loaded: loaded (/etc/systemd/system/gunicorn.service; disabled; vendor preset: enabled)
   Active: [0;1;32mactive (running)[0m since Чт 2021-02-04 10:52:11 EST; 38s ago
 Main PID: 22050 (gunicorn)
   CGroup: /system.slice/gunicorn.service
           ├─22050 /home/tikhon/gornijchaij/gchayenv/bin/python /home/tikhon/gornijchaij/gchayenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock gornijchaij.wsgi:application
           ├─22053 /home/tikhon/gornijchaij/gchayenv/bin/python /home/tikhon/gornijchaij/gchayenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock gornijchaij.wsgi:application
           ├─22054 /home/tikhon/gornijchaij/gchayenv/bin/python /home/tikhon/gornijchaij/gchayenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock gornijchaij.wsgi:application
           └─22055 /home/tikhon/gornijchaij/gchayenv/bin/python /home/tikhon/gornijchaij/gchayenv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock gornijchaij.wsgi:application

фев 04 10:52:11 gornychay systemd[1]: Started gunicorn daemon.
фев 04 10:52:11 gornychay gunicorn[22050]: [2021-02-04 10:52:11 -0500] [22050] [INFO] Starting gunicorn 20.0.4
фев 04 10:52:11 gornychay gunicorn[22050]: [2021-02-04 10:52:11 -0500] [22050] [INFO] Listening at: unix:/run/gunicorn.sock (22050)
фев 04 10:52:11 gornychay gunicorn[22050]: [2021-02-04 10:52:11 -0500] [22050] [INFO] Using worker: sync
фев 04 10:52:11 gornychay gunicorn[22050]: [2021-02-04 10:52:11 -0500] [22053] [INFO] Booting worker with pid: 22053
фев 04 10:52:11 gornychay gunicorn[22050]: [2021-02-04 10:52:11 -0500] [22054] [INFO] Booting worker with pid: 22054
фев 04 10:52:11 gornychay gunicorn[22050]: [2021-02-04 10:52:11 -0500] [22055] [INFO] Booting worker with pid: 22055
фев 04 10:52:12 gornychay gunicorn[22050]: Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
фев 04 10:52:12 gornychay gunicorn[22050]: Bad Request: /
фев 04 10:52:12 gornychay gunicorn[22050]:  - - [04/Feb/2021:18:52:12 +0300] "GET / HTTP/1.1" 400 56664 "-" "curl/7.47.0"
