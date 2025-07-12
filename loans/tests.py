from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from decimal import Decimal
import json

from .models import Customer, Loan


class CreditApprovalAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'monthly_income': 50000,
            'phone_number': '1234567890'
        }
        
    def test_customer_registration(self):
        """Test customer registration endpoint"""
        response = self.client.post(
            reverse('register_customer'),
            data=json.dumps(self.customer_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('customer_id', response.data)
        self.assertEqual(response.data['name'], 'John Doe')
        
        # Check approved limit calculation (36 * monthly_salary rounded to lakh)
        expected_limit = round(36 * 50000 / 100000) * 100000
        self.assertEqual(response.data['approved_limit'], expected_limit)
        
    def test_loan_eligibility_check(self):
        """Test loan eligibility check endpoint"""
        # First create a customer
        customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000')
        )
        
        eligibility_data = {
            'customer_id': customer.customer_id,
            'loan_amount': 500000,
            'interest_rate': 10.5,
            'tenure': 12
        }
        
        response = self.client.post(
            reverse('check_eligibility'),
            data=json.dumps(eligibility_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)
        self.assertIn('monthly_installment', response.data)
        
    def test_loan_creation(self):
        """Test loan creation endpoint"""
        # Create a customer
        customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000')
        )
        
        loan_data = {
            'customer_id': customer.customer_id,
            'loan_amount': 500000,
            'interest_rate': 15.0,
            'tenure': 12
        }
        
        response = self.client.post(
            reverse('create_loan'),
            data=json.dumps(loan_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('loan_id', response.data)
        self.assertIn('loan_approved', response.data)
        
    def test_view_loan_details(self):
        """Test view loan details endpoint"""
        # Create customer and loan
        customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000')
        )
        
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=Decimal('500000'),
            tenure=12,
            interest_rate=Decimal('15.0'),
            monthly_repayment=Decimal('45000'),
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        
        response = self.client.get(
            reverse('view_loan', kwargs={'loan_id': loan.loan_id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], loan.loan_id)
        self.assertIn('customer', response.data)
        
    def test_view_customer_loans(self):
        """Test view customer loans endpoint"""
        # Create customer and loans
        customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000')
        )
        
        # Create multiple loans
        for i in range(3):
            Loan.objects.create(
                customer=customer,
                loan_amount=Decimal('100000'),
                tenure=12,
                interest_rate=Decimal('12.0'),
                monthly_repayment=Decimal('9000'),
                start_date='2023-01-01',
                end_date='2023-12-31'
            )
        
        response = self.client.get(
            reverse('view_loans_by_customer', kwargs={'customer_id': customer.customer_id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
    def test_credit_score_calculation(self):
        """Test credit score calculation"""
        customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            age=30,
            phone_number='1234567890',
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000')
        )
        
        # New customer should have default score
        score = customer.calculate_credit_score()
        self.assertEqual(score, 50)
        
        # Add a loan with good payment history
        Loan.objects.create(
            customer=customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('12.0'),
            monthly_repayment=Decimal('9000'),
            emis_paid_on_time=12,  # All payments on time
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        
        # Score should be higher now
        score = customer.calculate_credit_score()
        self.assertGreater(score, 50)
