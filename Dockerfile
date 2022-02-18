FROM python:3.8-slim-bullseye
#FROM python:3.8-alpine
COPY requirements.txt /
RUN pip3 install --no-cache-dir --no-build-isolation -r /requirements.txt && rm -f /requirements.txt
RUN adduser --uid 1000 --home /app --no-create-home --disabled-password --gecos User --shell /bin/sh user
#RUN adduser -u 1000 -h /app -H -D -g User -s /bin/sh user
COPY src/ /app
RUN mkdir -p /app/data; chown -R 1000 /app/data
ARG BUILDTAG=unknown
ENV BUILDTAG=${BUILDTAG}
RUN echo "${BUILDTAG}" > /app/templates/build.txt
WORKDIR /app
EXPOSE 5000
USER user
#CMD ["python3", "app.py"]
CMD ["./gunicorn_app.py"]
