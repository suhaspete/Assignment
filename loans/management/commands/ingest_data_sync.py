from django.core.management.base import BaseCommand
from loans.tasks import ingest_customer_data, ingest_loan_data


class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files (synchronous)'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data ingestion...'))
        
        # Run customer ingestion
        self.stdout.write('Ingesting customer data...')
        customer_result = ingest_customer_data()
        self.stdout.write(self.style.SUCCESS(f'Customer ingestion: {customer_result}'))
        
        # Run loan ingestion
        self.stdout.write('Ingesting loan data...')
        loan_result = ingest_loan_data()
        self.stdout.write(self.style.SUCCESS(f'Loan ingestion: {loan_result}'))
        
        self.stdout.write(self.style.SUCCESS('Data ingestion completed!'))
