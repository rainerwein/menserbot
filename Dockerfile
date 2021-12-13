FROM python:3.10-slim-buster

WORKDIR /menserbot

COPY requirements.txt .

RUN apt-get update && \
    apt-get -y install git && \
    python -m pip install -r requirements.txt && \
    apt-get -y remove git

COPY menserbot.py menser.py .

CMD [ "python3", "-u", "menserbot.py" ]
