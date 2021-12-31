#FROM python:3.7-slim-bullseye
FROM python:3.7-alpine
COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt && rm -f /requirements.txt
RUN adduser -u 1000 -h /app -H -D -g User -s /bin/sh user
COPY src/ /app
RUN date +%Y-%m-%d_%H-%M-%SZ > /app/templates/build.txt
WORKDIR /app
EXPOSE 5000
USER user
#CMD ["python3", "app.py"]
CMD gunicorn --bind 0.0.0.0:5000 --access-logfile - wsgi:app
