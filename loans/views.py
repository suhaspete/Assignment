from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import HttpResponse
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .models import Customer, Loan, LoanApplication
from .serializers import (
    CustomerRegistrationSerializer, CustomerSerializer,
    LoanEligibilitySerializer, LoanEligibilityResponseSerializer,
    LoanApplicationSerializer, LoanApplicationResponseSerializer,
    LoanDetailSerializer, LoanListSerializer
)

logger = logging.getLogger(__name__)


def home_page(request):
    """Home page with API documentation"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Credit Approval System API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; line-height: 1.6; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .endpoint { background: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 10px 0; border-radius: 4px; }
            .method { background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
            .method.post { background: #ffc107; color: black; }
            .method.get { background: #17a2b8; }
            .code { background: #f1f1f1; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
            .status { color: #28a745; font-weight: bold; }
            .feature { background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏦 Credit Approval System API</h1>
            <p>Django-based loan approval system with intelligent credit scoring</p>
            <div class="status">✅ System Status: ONLINE</div>
        </div>

        <h2>🚀 Quick Start</h2>
        <p>Welcome to the Credit Approval System API! This system evaluates loan applications based on customer credit history and financial data.</p>

        <div class="feature">
            <strong>🎯 Key Features:</strong> Credit Score Calculation | Automated Loan Approval | Interest Rate Optimization | RESTful API
        </div>

        <h2>📡 API Endpoints</h2>

        <div class="endpoint">
            <h3><span class="method post">POST</span> /register/</h3>
            <p><strong>Register a new customer</strong></p>
            <div class="code">
{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "9876543210"
}
            </div>
            <p><em>Returns customer ID and calculated approved limit (36 × monthly_salary rounded to nearest lakh)</em></p>
        </div>

        <div class="endpoint">
            <h3><span class="method post">POST</span> /check-eligibility/</h3>
            <p><strong>Check loan eligibility based on credit score</strong></p>
            <div class="code">
{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.5,
    "tenure": 12
}
            </div>
            <p><em>Returns approval status, corrected interest rate, and monthly installment</em></p>
        </div>

        <div class="endpoint">
            <h3><span class="method post">POST</span> /create-loan/</h3>
            <p><strong>Create a new loan application</strong></p>
            <div class="code">
{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 12.0,
    "tenure": 12
}
            </div>
            <p><em>Processes loan application and creates loan if approved</em></p>
        </div>

        <div class="endpoint">
            <h3><span class="method get">GET</span> /view-loan/&lt;loan_id&gt;/</h3>
            <p><strong>View details of a specific loan</strong></p>
            <p><em>Returns loan details including customer information</em></p>
        </div>

        <div class="endpoint">
            <h3><span class="method get">GET</span> /view-loans/&lt;customer_id&gt;/</h3>
            <p><strong>View all loans for a customer</strong></p>
            <p><em>Returns list of all loans associated with the customer</em></p>
        </div>

        <h2>🧮 Credit Score Algorithm</h2>
        <ul>
            <li><strong>40%</strong> - Past loans paid on time</li>
            <li><strong>20%</strong> - Number of loans taken</li>
            <li><strong>20%</strong> - Loan activity in current year</li>
            <li><strong>20%</strong> - Total approved loan volume</li>
        </ul>

        <h2>📊 Loan Approval Rules</h2>
        <ul>
            <li><strong>Credit Score > 50:</strong> ✅ Approve loan</li>
            <li><strong>Credit Score 30-50:</strong> ✅ Approve with interest rate ≥ 12%</li>
            <li><strong>Credit Score 10-30:</strong> ✅ Approve with interest rate ≥ 16%</li>
            <li><strong>Credit Score < 10:</strong> ❌ Reject loan</li>
            <li><strong>Current EMIs > 50% of salary:</strong> ❌ Reject loan</li>
        </ul>

        <h2>🔗 Quick Links</h2>
        <ul>
            <li><a href="/admin/" target="_blank">🔧 Admin Panel</a> (admin/admin123)</li>
            <li><a href="https://github.com" target="_blank">📚 API Documentation</a></li>
            <li><a href="#" onclick="runTests()">🧪 Test API Endpoints</a></li>
        </ul>

        <h2>💡 Example Usage</h2>
        <div class="code">
# Register a customer
curl -X POST http://localhost:8080/register/ \\
  -H "Content-Type: application/json" \\
  -d '{"first_name": "Alice", "last_name": "Smith", "age": 28, "monthly_income": 60000, "phone_number": "9876543210"}'

# Check loan eligibility
curl -X POST http://localhost:8080/check-eligibility/ \\
  -H "Content-Type: application/json" \\
  -d '{"customer_id": 1, "loan_amount": 200000, "interest_rate": 11.0, "tenure": 24}'
        </div>

        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
            <p>Credit Approval System API | Built with Django REST Framework | © 2025</p>
        </footer>

        <script>
            function runTests() {
                alert('API test functionality would be implemented here. For now, please use the Python test script or curl commands.');
            }
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content)


@api_view(['POST'])
def register_customer(request):
    """Register a new customer"""
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        response_data = {
            'customer_id': customer.customer_id,
            'name': customer.full_name,
            'age': customer.age,
            'monthly_income': customer.monthly_salary,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_eligibility(request):
    """Check loan eligibility for a customer"""
    serializer = LoanEligibilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    customer_id = data['customer_id']
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']
    
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Calculate credit score
    credit_score = customer.calculate_credit_score()
    
    # Check eligibility based on credit score
    approval = False
    corrected_interest_rate = interest_rate
    
    if credit_score > 50:
        approval = True
    elif credit_score > 30:
        if interest_rate >= 12:
            approval = True
        else:
            corrected_interest_rate = Decimal('12.0')
    elif credit_score > 10:
        if interest_rate >= 16:
            approval = True
        else:
            corrected_interest_rate = Decimal('16.0')
    else:
        approval = False
    
    # Check if sum of current EMIs > 50% of monthly salary
    current_loans = customer.loans.filter(end_date__isnull=True)
    total_current_emis = sum(loan.monthly_repayment for loan in current_loans)
    
    if total_current_emis > customer.monthly_salary * Decimal('0.5'):
        approval = False
    
    # Calculate monthly installment
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
    
    response_data = {
        'customer_id': customer_id,
        'approval': approval,
        'interest_rate': interest_rate,
        'corrected_interest_rate': corrected_interest_rate,
        'tenure': tenure,
        'monthly_installment': monthly_installment
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_loan(request):
    """Create a new loan"""
    serializer = LoanApplicationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    customer_id = data['customer_id']
    loan_amount = data['loan_amount']
    interest_rate = data['interest_rate']
    tenure = data['tenure']
    
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check eligibility first
    eligibility_data = {
        'customer_id': customer_id,
        'loan_amount': loan_amount,
        'interest_rate': interest_rate,
        'tenure': tenure
    }
    
    # Re-use eligibility logic
    credit_score = customer.calculate_credit_score()
    
    # Check eligibility based on credit score
    approval = False
    corrected_interest_rate = interest_rate
    message = ""
    
    if credit_score > 50:
        approval = True
    elif credit_score > 30:
        if interest_rate >= 12:
            approval = True
        else:
            message = "Interest rate too low for your credit score"
    elif credit_score > 10:
        if interest_rate >= 16:
            approval = True
        else:
            message = "Interest rate too low for your credit score"
    else:
        approval = False
        message = "Credit score too low for loan approval"
    
    # Check if sum of current EMIs > 50% of monthly salary
    current_loans = customer.loans.filter(end_date__isnull=True)
    total_current_emis = sum(loan.monthly_repayment for loan in current_loans)
    
    if total_current_emis > customer.monthly_salary * Decimal('0.5'):
        approval = False
        message = "Current EMIs exceed 50% of monthly salary"
    
    loan_id = None
    monthly_installment = None
    
    if approval:
        # Use corrected interest rate if needed
        if credit_score <= 30 and interest_rate < 12:
            corrected_interest_rate = Decimal('12.0')
        elif credit_score <= 10 and interest_rate < 16:
            corrected_interest_rate = Decimal('16.0')
        
        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        
        # Create loan
        with transaction.atomic():
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=corrected_interest_rate,
                monthly_repayment=monthly_installment,
                start_date=datetime.now().date(),
                end_date=datetime.now().date() + timedelta(days=tenure * 30)
            )
            loan_id = loan.loan_id
            message = "Loan approved successfully"
    
    response_data = {
        'loan_id': loan_id,
        'customer_id': customer_id,
        'loan_approved': approval,
        'message': message,
        'monthly_installment': monthly_installment
    }
    
    return Response(response_data, status=status.HTTP_201_CREATED if approval else status.HTTP_200_OK)


@api_view(['GET'])
def view_loan(request, loan_id):
    """View loan details"""
    try:
        loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    """View all loans for a customer"""
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
    
    loans = customer.loans.all()
    serializer = LoanListSerializer(loans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def calculate_monthly_installment(principal, annual_rate, tenure_months):
    """Calculate monthly installment using compound interest"""
    principal = float(principal)
    monthly_rate = float(annual_rate) / 100 / 12
    months = int(tenure_months)
    
    if monthly_rate == 0:
        return round(principal / months, 2)
    
    # EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    emi = principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
    return round(emi, 2)
