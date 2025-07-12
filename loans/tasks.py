from celery import shared_task
from django.conf import settings
import pandas as pd
import logging
from datetime import datetime
from decimal import Decimal
from .models import Customer, Loan

logger = logging.getLogger(__name__)


@shared_task
def ingest_customer_data():
    """
    Ingest customer data from Excel file
    """
    try:
        # Read customer data
        customer_file = settings.BASE_DIR / 'customer_data.xlsx'
        df = pd.read_excel(customer_file)
        
        customers_created = 0
        customers_updated = 0
        
        for _, row in df.iterrows():
            customer_id = row['Customer ID']
            
            # Check if customer exists
            customer, created = Customer.objects.get_or_create(
                customer_id=customer_id,
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'age': row['Age'],
                    'phone_number': str(row['Phone Number']),
                    'monthly_salary': Decimal(str(row['Monthly Salary'])),
                    'approved_limit': Decimal(str(row['Approved Limit'])),
                    'current_debt': Decimal('0.00')
                }
            )
            
            if created:
                customers_created += 1
                logger.info(f"Created customer: {customer.full_name}")
            else:
                # Update existing customer
                customer.first_name = row['First Name']
                customer.last_name = row['Last Name']
                customer.age = row['Age']
                customer.phone_number = str(row['Phone Number'])
                customer.monthly_salary = Decimal(str(row['Monthly Salary']))
                customer.approved_limit = Decimal(str(row['Approved Limit']))
                customer.save()
                customers_updated += 1
                logger.info(f"Updated customer: {customer.full_name}")
        
        logger.info(f"Customer data ingestion completed. Created: {customers_created}, Updated: {customers_updated}")
        return f"Success: Created {customers_created}, Updated {customers_updated} customers"
        
    except Exception as e:
        logger.error(f"Error ingesting customer data: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def ingest_loan_data():
    """
    Ingest loan data from Excel file
    """
    try:
        # Read loan data
        loan_file = settings.BASE_DIR / 'loan_data.xlsx'
        df = pd.read_excel(loan_file)
        
        loans_created = 0
        loans_updated = 0
        
        for _, row in df.iterrows():
            try:
                customer_id = row['Customer ID']
                loan_id = row['Loan ID']
                
                # Get customer
                try:
                    customer = Customer.objects.get(customer_id=customer_id)
                except Customer.DoesNotExist:
                    logger.warning(f"Customer {customer_id} not found for loan {loan_id}")
                    continue
                
                # Parse dates
                start_date = pd.to_datetime(row['Date of Approval']).date()
                end_date = pd.to_datetime(row['End Date']).date()
                
                # Check if loan exists
                loan, created = Loan.objects.get_or_create(
                    loan_id=loan_id,
                    defaults={
                        'customer': customer,
                        'loan_amount': Decimal(str(row['Loan Amount'])),
                        'tenure': int(row['Tenure']),
                        'interest_rate': Decimal(str(row['Interest Rate'])),
                        'monthly_repayment': Decimal(str(row['Monthly payment'])),
                        'emis_paid_on_time': int(row['EMIs paid on Time']),
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )
                
                if created:
                    loans_created += 1
                    logger.info(f"Created loan: {loan_id} for customer {customer.full_name}")
                else:
                    # Update existing loan
                    loan.customer = customer
                    loan.loan_amount = Decimal(str(row['Loan Amount']))
                    loan.tenure = int(row['Tenure'])
                    loan.interest_rate = Decimal(str(row['Interest Rate']))
                    loan.monthly_repayment = Decimal(str(row['Monthly payment']))
                    loan.emis_paid_on_time = int(row['EMIs paid on Time'])
                    loan.start_date = start_date
                    loan.end_date = end_date
                    loan.save()
                    loans_updated += 1
                    logger.info(f"Updated loan: {loan_id} for customer {customer.full_name}")
                    
            except Exception as e:
                logger.error(f"Error processing loan row {row.to_dict()}: {str(e)}")
                continue
        
        logger.info(f"Loan data ingestion completed. Created: {loans_created}, Updated: {loans_updated}")
        return f"Success: Created {loans_created}, Updated {loans_updated} loans"
        
    except Exception as e:
        logger.error(f"Error ingesting loan data: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def ingest_all_data():
    """
    Ingest both customer and loan data
    """
    logger.info("Starting data ingestion process...")
    
    # First ingest customers
    customer_result = ingest_customer_data()
    
    # Then ingest loans
    loan_result = ingest_loan_data()
    
    result = f"Customer ingestion: {customer_result}\nLoan ingestion: {loan_result}"
    logger.info("Data ingestion process completed")
    
    return result
