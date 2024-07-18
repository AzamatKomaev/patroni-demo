#!/bin/bash

for ((;;))
do
PGPASSWORD=1234 psql \
    --host=localhost \
    --port=$1 \
    --username=user \
    db -c "select count(*) from posts;"
    sleep 0.5
    clear
done

