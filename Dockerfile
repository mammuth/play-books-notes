FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./app /app

WORKDIR /app

RUN pip install pipenv
RUN pipenv install --system
