# Start Gunicorn for Django
echo "Starting Gunicorn..."
gunicorn backend.wsgi:application
 
# Notify Gunicorn has started
echo "Gunicorn started successfully!"
 
# Start Daphne for ASGI
echo "Starting Daphne..."
daphne -p 8000 --bind 0.0.0.0 backend.asgi:application
 
# Notify Daphne has started
echo "Daphne started successfully!"
 
# Run your scheduler
python scheduler.py