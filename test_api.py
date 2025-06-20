"""
Test script for the Invoice to Order Processing API
"""
import requests
import os
import json
from pathlib import Path

# API endpoint URL
BASE_URL = "http://localhost:8080"

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Health check response: {response.json()}")
    else:
        print(f"Health check failed: {response.text}")
        
def test_extract_text():
    """Test the text extraction endpoint with a sample invoice"""
    # Path to sample invoice
    sample_path = Path("samples/invoice.pdf")
    
    if not sample_path.exists():
        print(f"Sample invoice not found at {sample_path}")
        return
    
    # Create a sample file to upload
    with open(sample_path, "rb") as f:
        files = {"file": (sample_path.name, f, "application/pdf")}
        response = requests.post(f"{BASE_URL}/extract-text/", files=files)
    
    print(f"Extract text status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Text content: {result['text_content'][:100]}...")  # Print first 100 chars
        print(f"File processed: {result['filename']}")
    else:
        print(f"Extract text failed: {response.text}")

def test_process_invoice():
    """Test the invoice processing endpoint with a sample invoice"""
    # Since we haven't implemented the process-invoice endpoint yet,
    # we'll use extract-text again for demonstration
    
    # Path to sample invoice
    sample_path = Path("samples/invoice.pdf")
    
    if not sample_path.exists():
        print(f"Sample invoice not found at {sample_path}")
        return
    
    # Create a sample file to upload
    with open(sample_path, "rb") as f:
        files = {"file": (sample_path.name, f, "application/pdf")}
        data = {
            "shiprocket_email": "",  # Leave empty to skip order creation
            "shiprocket_password": ""
        }
        # Use extract-text endpoint since we don't have process-invoice yet
        response = requests.post(f"{BASE_URL}/extract-text/", files=files, data=data)
    
    print(f"Process invoice status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Filename: {result['filename']}")
        print(f"Text content: {result['text_content'][:100]}...")
    else:
        print(f"Process invoice failed: {response.text}")

if __name__ == "__main__":
    print("Testing Invoice to Order Processing API...")
    print("-" * 60)
    
    test_health()
    print("-" * 60)
    
    test_extract_text()
    print("-" * 60)
    
    test_process_invoice()
    print("-" * 60)
    
    print("Tests completed.") 