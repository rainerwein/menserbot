FROM python:3.10-alpine as base

FROM base as builder 

RUN mkdir /install
WORKDIR /install

COPY requirements.txt .
RUN apk add --no-cache git && \
    python -m pip install --no-cache-dir --target=/install -r requirements.txt


FROM base     

COPY --from=builder /install /usr/local/lib/python3.10/site-packages

ENV TZ="Europe/Berlin"

WORKDIR /menserbot
COPY helper.py config.py menserbot.py menser.py .

CMD [ "python3", "-u", "menserbot.py" ]
