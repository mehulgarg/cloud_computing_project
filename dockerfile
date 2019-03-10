from alpine:3.7

RUN apk add --no-cache python3-dev \
    && pip3 install --upgrade pip

WORKDIR /app

COPY . /app

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt


