from django.contrib import admin
from .models import Customer, Loan, LoanApplication


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'first_name', 'last_name', 'phone_number', 'monthly_salary', 'approved_limit', 'current_debt']
    list_filter = ['created_at']
    search_fields = ['first_name', 'last_name', 'phone_number']
    readonly_fields = ['customer_id', 'created_at']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date', 'interest_rate']
    search_fields = ['customer__first_name', 'customer__last_name', 'loan_id']
    readonly_fields = ['loan_id', 'created_at']


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'loan_amount', 'interest_rate', 'tenure', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__first_name', 'customer__last_name']
    readonly_fields = ['created_at']
