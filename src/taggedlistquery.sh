#!/bin/sh
export DOTENV=model/env
exec python3 -m taggedlist "$@"
