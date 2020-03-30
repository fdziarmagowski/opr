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

RUN set -ex \
    && wget http://deb.debian.org/debian/pool/main/f/fonts-lato/fonts-lato_2.0.orig.tar.xz \
    && tar -xf fonts-lato_2.0.orig.tar.xz -C /usr/share/fonts/TTF/ \
    && fc-cache -fr

COPY build.py /opr/
COPY content/* /opr/content/
COPY static/* /opr/static/
COPY templates/* /opr/templates/

RUN mkdir -p /opr/base16 /opr/output \
    && adduser -D builder \
    && chown builder:builder -R /opr

VOLUME ["/opr/base16", "/opr/content", "/opt/output"]

COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

USER builder
WORKDIR /opr
CMD ["python3", "build.py"]
