FROM python:3.11

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["hypercorn",  "-b", "0.0.0.0:8000", "app:app"]
