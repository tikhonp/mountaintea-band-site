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
2. Create a `.env` file in the root directory of the project and add the environment variables from `.env_example` to it

3. Assuming that you have docker and make installed just run

    ```sh
    $ make
    ```
   
This will start the application in development mode on [http://0.0.0.0:8000/](http://0.0.0.0:8000/). 

If you want to develop `/staff/qrcode/` page, you need to set up _Vue.js_ workspace:

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

We're using dockerized prod build in `compose.prod.yaml`.

On server install `docker`, `git`, and `make`. Clone the repo, create `.env` file and run:

```sh
$ make prod
```

Thats all :)

## 📧 Setup Email

For proper mailing you need a smtp service that provides DKIM and SPF records.

1. So first you need smtp service domain. Add to `.env`: `EMAIL_HOST=example.smtp.com`
2. Then you need smtp username note that it would be great if that's will be `noreply@mountainteaband.ru`, the sender adress. At least this record MUST EXIST ON SERVER otherwise shitty mail.ru regects all. Put `EMAIL_HOST_USER=noreply@mountainteaband.ru` into `.env`.
3. Password in `.env`: `EMAIL_HOST_PASSWORD=password`
4. Add `DKIM` and `SPF` dns records to domain
5. `As long it's just email sending service not recieveing, add NULL MX record.` - that's will not work because of shitty mail.ru... You have to add MX record to mx server of email sending service
6. And finally `_dmarc.` record to strict the DKIM and SPF policies: `v=DMARC1; p=quarantine; adkim=s; aspf=s;`

   
## 🔐 Security and vulnerabilities

If you think you've found a critical vulnerability that should not be exposed to the public yet, you can always email me directly by email: [tikhon.petrishchev@gmail.com](mailto:tikhon.petrishchev@gmail.com).

Please do not test vulnerabilities in public.

## 💼 License 

[MIT](LICENSE)

In other words, you can use the code for private and commercial purposes with an author attribution (by including the original license file).

Feel free to contact us via email [tikhon.petrishchev@gmail.com](mailto:tikhon.petrishchev@gmail.com).

❤️
