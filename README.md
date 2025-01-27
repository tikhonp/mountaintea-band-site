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

We're using dockerized prod build in `compose.prod.yaml`.

On server install `docker`, `git`, and `make`. Clone the repo, create `.env` file and run:

```sh
$ make prod
```

Thats all :)
   
## 🔐 Security and vulnerabilities

If you think you've found a critical vulnerability that should not be exposed to the public yet, you can always email me directly by email: [tikhon.petrishchev@gmail.com](mailto:tikhon.petrishchev@gmail.com).

Please do not test vulnerabilities in public.

## 💼 License 

[MIT](LICENSE)

In other words, you can use the code for private and commercial purposes with an author attribution (by including the original license file).

Feel free to contact us via email [tikhon.petrishchev@gmail.com](mailto:tikhon.petrishchev@gmail.com).

❤️
