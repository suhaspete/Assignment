#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
python manage.py wait_for_db

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created: admin/admin123")
else:
    print("Superuser already exists")
EOF

# Ingest data if tables are empty
echo "Checking for existing data..."
python manage.py shell << EOF
from loans.models import Customer, Loan
if Customer.objects.count() == 0:
    print("No existing data found. Starting data ingestion...")
    from loans.tasks import ingest_customer_data, ingest_loan_data
    customer_result = ingest_customer_data()
    loan_result = ingest_loan_data()
    print(f"Customer ingestion: {customer_result}")
    print(f"Loan ingestion: {loan_result}")
else:
    print("Data already exists, skipping ingestion")
EOF

# Start the server
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
