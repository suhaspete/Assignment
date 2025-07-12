# Credit Approval System

A Django-based credit approval system that processes loan applications based on customer credit scores and historical data.

## Features

- Customer registration with automatic credit limit calculation
- Loan eligibility checking based on credit score
- Loan application processing
- Data ingestion from Excel files using Celery background tasks
- PostgreSQL database with Docker support
- REST API endpoints for all operations
- Interactive API documentation homepage
- Django admin interface for data management

## API Endpoints

### 1. Customer Registration
- **URL**: `/register/`
- **Method**: POST
- **Description**: Register a new customer with automatic credit limit calculation

### 2. Check Loan Eligibility
- **URL**: `/check-eligibility/`
- **Method**: POST
- **Description**: Check if a customer is eligible for a loan based on credit score

### 3. Create Loan
- **URL**: `/create-loan/`
- **Method**: POST
- **Description**: Create a new loan if eligible

### 4. View Loan Details
- **URL**: `/view-loan/<loan_id>/`
- **Method**: GET
- **Description**: Get details of a specific loan

### 5. View Customer Loans
- **URL**: `/view-loans/<customer_id>/`
- **Method**: GET
- **Description**: Get all loans for a specific customer

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Customer and loan data in Excel format (customer_data.xlsx, loan_data.xlsx)

### Running the Application

1. **Clone the repository and navigate to the project directory**

2. **Place your Excel files**:
   - `customer_data.xlsx` - Customer data
   - `loan_data.xlsx` - Loan data

3. **Start the application**:
   ```bash
   docker-compose up --build
   ```

4. **The application will be available at**:
   - API: http://localhost:8080/ (Home page with documentation)
   - API Endpoints: http://localhost:8080/register/, /check-eligibility/, etc.
   - Admin Panel: http://localhost:8080/admin/
   - Default admin credentials: admin/admin123

### Manual Setup (without Docker)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**:
   - Create a database named `creditapproval`
   - Update database settings in `settings.py`

3. **Start Redis server**:
   ```bash
   redis-server
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Ingest data**:
   ```bash
   python manage.py ingest_data_sync
   ```

7. **Start Celery worker**:
   ```bash
   celery -A credit_approval worker --loglevel=info
   ```

8. **Start Django server**:
   ```bash
   python manage.py runserver 8080
   ```

**Note**: The application runs on port 8080. Visit http://localhost:8080/ for the API documentation homepage.

## Data Models

### Customer
- customer_id (Primary Key)
- first_name, last_name
- age, phone_number
- monthly_salary, approved_limit
- current_debt

### Loan
- loan_id (Primary Key)
- customer (Foreign Key)
- loan_amount, tenure, interest_rate
- monthly_repayment, emis_paid_on_time
- start_date, end_date

## Credit Score Calculation

The system calculates credit scores based on:
1. Past loans paid on time (40% weight)
2. Number of loans taken (20% weight)
3. Loan activity in current year (20% weight)
4. Loan approved volume (20% weight)

## Interest Rate Rules

- Credit score > 50: Approve loan
- Credit score 30-50: Approve with interest rate ≥ 12%
- Credit score 10-30: Approve with interest rate ≥ 16%
- Credit score < 10: Reject loan

## Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Containerization**: Docker & Docker Compose
- **Data Processing**: Pandas, OpenPyXL

## Development

### Running Tests
```bash
python manage.py test
```

### Accessing Admin Panel
1. Go to http://localhost:8080/admin/
2. Login with admin credentials
3. View and manage customers, loans, and applications

### API Documentation
- Visit http://localhost:8080/ for interactive API documentation
- The home page provides endpoint details, examples, and testing information

### Background Tasks
The system uses Celery for background data ingestion:
- Customer data ingestion
- Loan data ingestion
- Can be triggered via management commands or admin interface

## Production Deployment

For production deployment:
1. Set DEBUG=False in settings
2. Configure proper SECRET_KEY
3. Use environment variables for sensitive data
4. Set up proper logging
5. Configure CORS settings
6. Use a production WSGI server like Gunicorn
