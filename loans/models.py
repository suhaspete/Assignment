from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'customers'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def calculate_credit_score(self):
        """Calculate credit score based on loan history"""
        loans = self.loans.all()
        
        if not loans.exists():
            return 50  # Default score for new customers
        
        # Check if sum of current loans > approved limit
        current_loans = loans.filter(end_date__isnull=True)
        total_current_amount = sum(loan.loan_amount for loan in current_loans)
        
        if total_current_amount > self.approved_limit:
            return 0
        
        # Calculate components
        total_loans = loans.count()
        loans_paid_on_time = sum(1 for loan in loans if loan.emis_paid_on_time >= loan.tenure * 0.9)
        
        # Current year activity
        from datetime import datetime
        current_year_loans = loans.filter(start_date__year=datetime.now().year).count()
        
        # Approved volume (total loan amount)
        total_approved_volume = sum(loan.loan_amount for loan in loans)
        
        # Calculate score (simplified algorithm)
        score = 0
        
        # Past loans paid on time (40% weight)
        if total_loans > 0:
            score += (loans_paid_on_time / total_loans) * 40
        
        # Number of loans factor (20% weight)
        if total_loans <= 2:
            score += 20
        elif total_loans <= 5:
            score += 15
        else:
            score += 10
        
        # Current year activity (20% weight)
        if current_year_loans <= 2:
            score += 20
        elif current_year_loans <= 4:
            score += 15
        else:
            score += 10
        
        # Approved volume factor (20% weight)
        if total_approved_volume <= self.approved_limit * 0.5:
            score += 20
        elif total_approved_volume <= self.approved_limit * 0.8:
            score += 15
        else:
            score += 10
        
        return min(100, max(0, int(score)))


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField(help_text="Loan tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'loans'
    
    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.full_name}"
    
    @property
    def repayments_left(self):
        """Calculate remaining EMIs"""
        return max(0, self.tenure - self.emis_paid_on_time)
    
    @property
    def is_active(self):
        """Check if loan is still active"""
        return self.end_date is None or self.repayments_left > 0
    
    def calculate_monthly_installment(self):
        """Calculate monthly installment using compound interest"""
        principal = float(self.loan_amount)
        rate = float(self.interest_rate) / 100 / 12  # Monthly rate
        months = self.tenure
        
        if rate == 0:
            return principal / months
        
        # EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        emi = principal * rate * (1 + rate) ** months / ((1 + rate) ** months - 1)
        return round(emi, 2)


class LoanApplication(models.Model):
    """Model to track loan applications"""
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='applications')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    approved_loan = models.OneToOneField(Loan, null=True, blank=True, on_delete=models.SET_NULL)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'loan_applications'
    
    def __str__(self):
        return f"Application {self.id} - {self.customer.full_name}"
