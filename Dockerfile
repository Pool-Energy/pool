FROM debian:bookworm-slim

LABEL maintainer="contact@pool.energy"

ARG GITHUB_TOKEN

RUN apt-get update && \
    apt-get upgrade -y
RUN apt-get install -y python3-venv python3-yaml python3-aiohttp python3-dev libpq-dev gcc git vim procps net-tools iputils-ping apache2-utils simpleproxy

EXPOSE 8088

WORKDIR /root/pool

COPY ./requirements.txt .

RUN python3 -m venv venv
RUN ./venv/bin/pip install -r requirements.txt

COPY ./pool /root/pool/pool/
COPY ./hooks /root/pool/hooks/
COPY ./tools /root/pool/tools/
COPY ./docker/entrypoint.sh /entrypoint.sh

CMD ["bash", "/entrypoint.sh"]
