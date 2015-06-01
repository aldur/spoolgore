#!/bin/sh

"$(dirname "$(readlink -f "$0")")"/../spoolgore \
    -smtpaddr 127.0.0.1:8025 \
    /tmp/spoolgore_t \
    -freq 1  \

