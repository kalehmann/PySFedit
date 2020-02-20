FROM debian:10-slim

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    gir1.2-gtk-3.0 \
    python3 \
    python3-gi-cairo \
    python3-pillow \
    python3-pkg-resources \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*
