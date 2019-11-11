#!/bin/bash

source ../env/bin/activate


celery -A tasks worker --loglevel=info &
python3.7 app.py

kill -9 $(ps aux | grep +1Keeper/env/bin/celery)