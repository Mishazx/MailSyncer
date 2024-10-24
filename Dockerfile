FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# CMD [ "python", "runserver.py" ]
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "MailSyncer.asgi:application"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
