#!/bin/bash


echo "Waiting for database..."
while ! python -c "import psycopg2; psycopg2.connect(host='db', database='KPILAB3', user='postgres', password='aika1711')" 2>/dev/null; do
    sleep 1
done
echo "Database is ready!"


rm -rf migrations/


flask db init


flask db migrate -m "Initial migration"


flask db upgrade


flask run --host=0.0.0.0