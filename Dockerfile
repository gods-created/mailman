FROM python:3.14-slim 

COPY . /app

WORKDIR /app
EXPOSE 8001

RUN chmod +x /app/entrypoint.sh
RUN apt-get update
RUN pip install --upgrade --no-cache-dir -r requirements.txt

STOPSIGNAL SIGINT

HEALTHCHECK --interval=15s --timeout=15s --start-period=5s --retries=1 NONE 
CMD [ "/app/entrypoint.sh" ]