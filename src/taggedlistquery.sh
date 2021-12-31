#!/bin/sh
exec python3 -m taggedlist -r model/hostlist.yaml model/internal.yaml model/external.yaml 'model/./_docs/./*/*.json' "$@"
