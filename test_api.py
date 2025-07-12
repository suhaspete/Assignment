#!/usr/bin/env python3
"""
Script to test all API endpoints of the Credit Approval System
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8080"

def test_customer_registration():
    """Test customer registration endpoint"""
    print("Testing Customer Registration...")
    
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "1234567890"
    }
    
    response = requests.post(
        f"{BASE_URL}/register/",
        json=customer_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()['customer_id']
    else:
        print("❌ Customer registration failed")
        return None

def test_loan_eligibility(customer_id):
    """Test loan eligibility check endpoint"""
    print(f"\nTesting Loan Eligibility for Customer {customer_id}...")
    
    eligibility_data = {
        "customer_id": customer_id,
        "loan_amount": 500000,
        "interest_rate": 10.5,
        "tenure": 12
    }
    
    response = requests.post(
        f"{BASE_URL}/check-eligibility/",
        json=eligibility_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Loan eligibility check successful")
        return response.json()
    else:
        print("❌ Loan eligibility check failed")
        return None

def test_loan_creation(customer_id):
    """Test loan creation endpoint"""
    print(f"\nTesting Loan Creation for Customer {customer_id}...")
    
    loan_data = {
        "customer_id": customer_id,
        "loan_amount": 500000,
        "interest_rate": 15.0,
        "tenure": 12
    }
    
    response = requests.post(
        f"{BASE_URL}/create-loan/",
        json=loan_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('loan_approved'):
            print("✅ Loan creation successful")
            return result.get('loan_id')
        else:
            print("⚠️ Loan was not approved")
            return None
    else:
        print("❌ Loan creation failed")
        return None

def test_view_loan(loan_id):
    """Test view loan details endpoint"""
    if not loan_id:
        print("\nSkipping loan details test (no loan ID available)")
        return
    
    print(f"\nTesting View Loan Details for Loan {loan_id}...")
    
    response = requests.get(f"{BASE_URL}/view-loan/{loan_id}/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ View loan details successful")
    else:
        print("❌ View loan details failed")

def test_view_customer_loans(customer_id):
    """Test view customer loans endpoint"""
    print(f"\nTesting View Customer Loans for Customer {customer_id}...")
    
    response = requests.get(f"{BASE_URL}/view-loans/{customer_id}/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ View customer loans successful")
    else:
        print("❌ View customer loans failed")

def main():
    """Main function to run all tests"""
    print("=== Credit Approval System API Testing ===\n")
    
    # Test customer registration
    customer_id = test_customer_registration()
    if not customer_id:
        print("Cannot continue testing without a customer ID")
        return
    
    # Test loan eligibility
    eligibility_result = test_loan_eligibility(customer_id)
    
    # Test loan creation
    loan_id = test_loan_creation(customer_id)
    
    # Test view loan details
    test_view_loan(loan_id)
    
    # Test view customer loans
    test_view_customer_loans(customer_id)
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
