
#!/bin/bash

echo "Starting workers..."

rq worker high_priority &
rq worker normal &

echo "Starting Flask server..."

gunicorn app:app --bind 0.0.0.0:8080 --workers 5
