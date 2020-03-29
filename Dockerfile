FROM alpine:edge

RUN set -ex \
    && echo "@edgetest http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

RUN apk add --update-cache \
      chromium \
      git \
      pandoc@edgetest \
      py3-gitpython@edgetest \
      py3-jinja2 \
      py3-yaml \
      tidyhtml \
    && rm -rf /var/cache/apk/*

RUN mkdir -p /opr/base16 \
    && adduser -D builder \
    && chown builder:builder /opr

RUN set -ex \
    && wget http://deb.debian.org/debian/pool/main/f/fonts-lato/fonts-lato_2.0.orig.tar.xz \
    && tar -xf fonts-lato_2.0.orig.tar.xz -C /usr/share/fonts/TTF/ \
    && fc-cache -fr

VOLUME ["/opr"]

USER builder
WORKDIR /opr
CMD ["python3", "build.py"]
