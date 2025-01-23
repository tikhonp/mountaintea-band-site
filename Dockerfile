# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt
COPY . .

FROM base AS dev
ENV DJANGO_SETTINGS_MODULE=mountaintea_band_site.settings.development
EXPOSE 8000
ADD --chmod=111 exec-scripts/start-dev.sh /start.sh 
CMD ["/start.sh"]

FROM dev AS makemigrations
CMD ["python", "manage.py", "makemigrations"]

FROM base AS staticfiles
ENV DJANGO_SETTINGS_MODULE=mountaintea_band_site.settings.production
RUN python manage.py collectstatic --noinput

FROM staticfiles AS prod
ENV DJANGO_SETTINGS_MODULE=mountaintea_band_site.settings.production
ADD --chmod=111 exec-scripts/start-prod.sh /start.sh 
CMD ["/start.sh"]

FROM nginx AS nginx-prod
COPY nginx/conf.d/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=staticfiles /app/mountaintea_band_site/static /usr/share/nginx/html/static
