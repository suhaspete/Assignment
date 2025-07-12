# Test API endpoints for Credit Approval System
# Make sure the server is running at http://localhost:8000

$baseUrl = "http://localhost:8000"

Write-Host "=== Credit Approval System API Testing ===" -ForegroundColor Green
Write-Host ""

# Test customer registration
Write-Host "Testing Customer Registration..." -ForegroundColor Yellow

$customerData = @{
    first_name = "John"
    last_name = "Doe"
    age = 30
    monthly_income = 50000
    phone_number = "1234567890"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/register/" -Method POST -Body $customerData -ContentType "application/json"
    Write-Host "✅ Customer Registration: SUCCESS" -ForegroundColor Green
    Write-Host "Customer ID: $($response.customer_id)"
    Write-Host "Name: $($response.name)"
    Write-Host "Approved Limit: $($response.approved_limit)"
    $customerId = $response.customer_id
} catch {
    Write-Host "❌ Customer Registration: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
    exit 1
}

Write-Host ""

# Test loan eligibility
Write-Host "Testing Loan Eligibility..." -ForegroundColor Yellow

$eligibilityData = @{
    customer_id = $customerId
    loan_amount = 500000
    interest_rate = 10.5
    tenure = 12
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/check-eligibility/" -Method POST -Body $eligibilityData -ContentType "application/json"
    Write-Host "✅ Loan Eligibility: SUCCESS" -ForegroundColor Green
    Write-Host "Approval: $($response.approval)"
    Write-Host "Interest Rate: $($response.interest_rate)"
    Write-Host "Corrected Interest Rate: $($response.corrected_interest_rate)"
    Write-Host "Monthly Installment: $($response.monthly_installment)"
} catch {
    Write-Host "❌ Loan Eligibility: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}

Write-Host ""

# Test loan creation
Write-Host "Testing Loan Creation..." -ForegroundColor Yellow

$loanData = @{
    customer_id = $customerId
    loan_amount = 500000
    interest_rate = 15.0
    tenure = 12
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/create-loan/" -Method POST -Body $loanData -ContentType "application/json"
    Write-Host "✅ Loan Creation: SUCCESS" -ForegroundColor Green
    Write-Host "Loan ID: $($response.loan_id)"
    Write-Host "Loan Approved: $($response.loan_approved)"
    Write-Host "Message: $($response.message)"
    Write-Host "Monthly Installment: $($response.monthly_installment)"
    $loanId = $response.loan_id
} catch {
    Write-Host "❌ Loan Creation: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}

Write-Host ""

# Test view loan details
if ($loanId) {
    Write-Host "Testing View Loan Details..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/view-loan/$loanId/" -Method GET
        Write-Host "✅ View Loan Details: SUCCESS" -ForegroundColor Green
        Write-Host "Loan ID: $($response.loan_id)"
        Write-Host "Customer: $($response.customer.first_name) $($response.customer.last_name)"
        Write-Host "Loan Amount: $($response.loan_amount)"
        Write-Host "Interest Rate: $($response.interest_rate)"
        Write-Host "Tenure: $($response.tenure)"
    } catch {
        Write-Host "❌ View Loan Details: FAILED" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)"
    }
}

Write-Host ""

# Test view customer loans
Write-Host "Testing View Customer Loans..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/view-loans/$customerId/" -Method GET
    Write-Host "✅ View Customer Loans: SUCCESS" -ForegroundColor Green
    Write-Host "Number of loans: $($response.Count)"
    foreach ($loan in $response) {
        Write-Host "  - Loan ID: $($loan.loan_id), Amount: $($loan.loan_amount)"
    }
} catch {
    Write-Host "❌ View Customer Loans: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "=== Testing Complete ===" -ForegroundColor Green
