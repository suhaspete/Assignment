from django.core.management.base import BaseCommand
from django.db import connection, models
from loans.models import Customer, Loan, LoanApplication


class Command(BaseCommand):
    help = 'Fix database sequences for primary key fields'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Fix customer sequence
            max_customer_id = Customer.objects.aggregate(max_id=models.Max('customer_id'))['max_id'] or 0
            cursor.execute(f"SELECT setval('customers_customer_id_seq', {max_customer_id + 1});")
            self.stdout.write(f"Set customer sequence to {max_customer_id + 1}")
            
            # Fix loan sequence
            max_loan_id = Loan.objects.aggregate(max_id=models.Max('loan_id'))['max_id'] or 0
            cursor.execute(f"SELECT setval('loans_loan_id_seq', {max_loan_id + 1});")
            self.stdout.write(f"Set loan sequence to {max_loan_id + 1}")
            
            # Fix loan application sequence
            max_app_id = LoanApplication.objects.aggregate(max_id=models.Max('id'))['max_id'] or 0
            cursor.execute(f"SELECT setval('loan_applications_id_seq', {max_app_id + 1});")
            self.stdout.write(f"Set loan application sequence to {max_app_id + 1}")
            
        self.stdout.write(
            self.style.SUCCESS('Successfully fixed all sequences')
        )
