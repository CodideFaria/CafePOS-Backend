#!/usr/bin/env python3
"""
Test script for daily email functionality with sample data
Generates HTML email content with mock data to test template accuracy
"""

import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.email_service import email_service


def test_email_with_sample_data():
    """Test the daily email generation with comprehensive sample data"""
    print("Testing Daily Email with Sample Data")
    print("=" * 50)
    
    # Create comprehensive sample data to test all email sections
    sample_sales_data = {
        "date": "2025-08-24",
        "summary": {
            "totalRevenue": 2456.75,
            "totalTransactions": 42,
            "averageOrderValue": 58.49,
            "taxCollected": 245.68,
            "discountsGiven": 123.45,
            "refundsProcessed": 87.50,
            "paymentMethods": {
                "cash": 1200.25,
                "card": 1256.50
            }
        },
        "topSellingItems": [
            {
                "name": "Premium Coffee Blend",
                "quantitySold": 25,
                "revenue": 125.00
            },
            {
                "name": "Chocolate Croissant",
                "quantitySold": 18,
                "revenue": 108.00
            },
            {
                "name": "Iced Americano",
                "quantitySold": 15,
                "revenue": 67.50
            },
            {
                "name": "Blueberry Muffin",
                "quantitySold": 12,
                "revenue": 48.00
            },
            {
                "name": "Espresso Shot",
                "quantitySold": 22,
                "revenue": 88.00
            }
        ],
        "staffPerformance": [
            {
                "userId": "staff-001",
                "name": "Alice Johnson",
                "transactions": 18,
                "revenue": 1050.25,
                "averageOrderValue": 58.35
            },
            {
                "userId": "staff-002", 
                "name": "Bob Smith",
                "transactions": 15,
                "revenue": 875.50,
                "averageOrderValue": 58.37
            },
            {
                "userId": "staff-003",
                "name": "Carol Davis",
                "transactions": 9,
                "revenue": 531.00,
                "averageOrderValue": 59.00
            }
        ]
    }
    
    print(f"Sample data prepared:")
    print(f"   Total Revenue: ${sample_sales_data['summary']['totalRevenue']:.2f}")
    print(f"   Total Transactions: {sample_sales_data['summary']['totalTransactions']}")
    print(f"   Top Items: {len(sample_sales_data['topSellingItems'])} items")
    print(f"   Staff Members: {len(sample_sales_data['staffPerformance'])} staff")
    
    try:
        # Capture the HTML output
        class TestEmailService:
            def __init__(self):
                self.captured_html = None
                self.captured_subject = None
                self.captured_text = None
                
            def send_email(self, recipients, subject, html_body, text_body=None):
                """Capture email data instead of sending"""
                self.captured_html = html_body
                self.captured_subject = subject
                self.captured_text = text_body
                return {
                    'success': True,
                    'message': 'Email captured for testing',
                    'mock': True
                }
        
        # Use the real email service method but capture output
        test_service = TestEmailService()
        
        # Temporarily replace the email service method
        original_send_email = email_service.send_email
        email_service.send_email = test_service.send_email
        
        # Generate the email
        result = email_service.send_daily_sales_summary(
            recipients=['test@cafepos.com'], 
            sales_data=sample_sales_data, 
            date=sample_sales_data['date']
        )
        
        # Restore original method
        email_service.send_email = original_send_email
        
        if result['success']:
            # Save HTML to file
            filename = f"daily_email_sample_data_{sample_sales_data['date']}.html"
            filepath = os.path.join(os.path.dirname(__file__), filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(test_service.captured_html)
            
            # Also save text version
            text_filename = f"daily_email_sample_data_{sample_sales_data['date']}.txt"
            text_filepath = os.path.join(os.path.dirname(__file__), text_filename)
            
            with open(text_filepath, 'w', encoding='utf-8') as f:
                f.write(test_service.captured_text or "No text version generated")
            
            print(f"\n[+] HTML email generated successfully")
            print(f"   Subject: {test_service.captured_subject}")
            print(f"   HTML file: {filename}")
            print(f"   Text file: {text_filename}")
            
            # Verify all data appears correctly in HTML
            html_content = test_service.captured_html
            print(f"\nData Accuracy Verification:")
            
            # Check key metrics
            print(f"Key Metrics:")
            total_revenue = sample_sales_data['summary']['totalRevenue']
            total_transactions = sample_sales_data['summary']['totalTransactions']
            avg_order_value = sample_sales_data['summary']['averageOrderValue']
            tax_collected = sample_sales_data['summary']['taxCollected']
            
            print(f"   Revenue €{total_revenue:.2f}: {'[+]' if f'€{total_revenue:.2f}' in html_content else '[!]'}")
            print(f"   Transactions {total_transactions}: {'[+]' if str(total_transactions) in html_content else '[!]'}")
            print(f"   Avg Order €{avg_order_value:.2f}: {'[+]' if f'€{avg_order_value:.2f}' in html_content else '[!]'}")
            print(f"   Tax €{tax_collected:.2f}: {'[+]' if f'€{tax_collected:.2f}' in html_content else '[!]'}")
            
            # Check payment methods
            print(f"Payment Methods:")
            for method, amount in sample_sales_data['summary']['paymentMethods'].items():
                appears = f'€{amount:.2f}' in html_content
                print(f"   {method.title()} €{amount:.2f}: {'[+]' if appears else '[!]'}")
            
            # Check adjustments section (discounts/refunds)
            discounts = sample_sales_data['summary']['discountsGiven']
            refunds = sample_sales_data['summary']['refundsProcessed']
            print(f"Adjustments:")
            print(f"   Discounts €{discounts:.2f}: {'[+]' if f'€{discounts:.2f}' in html_content else '[!]'}")
            print(f"   Refunds €{refunds:.2f}: {'[+]' if f'€{refunds:.2f}' in html_content else '[!]'}")
            
            # Check top selling items
            print(f"Top Selling Items:")
            for item in sample_sales_data['topSellingItems'][:3]:
                name_appears = item['name'] in html_content
                quantity_appears = str(item['quantitySold']) in html_content
                revenue_appears = f"€{item['revenue']:.2f}" in html_content
                
                print(f"   {item['name']}: Name {'[+]' if name_appears else '[!]'}, "
                      f"Qty {item['quantitySold']} {'[+]' if quantity_appears else '[!]'}, "
                      f"Rev €{item['revenue']:.2f} {'[+]' if revenue_appears else '[!]'}")
            
            # Check staff performance
            print(f"Staff Performance:")
            for staff in sample_sales_data['staffPerformance']:
                name_appears = staff['name'] in html_content
                transactions_appear = str(staff['transactions']) in html_content
                revenue_appears = f"€{staff['revenue']:.2f}" in html_content
                avg_appears = f"€{staff['averageOrderValue']:.2f}" in html_content
                
                print(f"   {staff['name']}: Name {'[+]' if name_appears else '[!]'}, "
                      f"Trans {staff['transactions']} {'[+]' if transactions_appear else '[!]'}, "
                      f"Rev €{staff['revenue']:.2f} {'[+]' if revenue_appears else '[!]'}, "
                      f"Avg €{staff['averageOrderValue']:.2f} {'[+]' if avg_appears else '[!]'}")
            
            # Check date
            date_appears = sample_sales_data['date'] in html_content
            print(f"Date {sample_sales_data['date']}: {'[+]' if date_appears else '[!]'}")
            
            # Email sections verification
            print(f"\nEmail Template Sections:")
            sections_to_check = [
                ("Header with cafe name", "CafePOS Daily Sales Summary"),
                ("Key Metrics section", "Key Metrics"),
                ("Payment Methods table", "Payment Methods"),
                ("Top Selling Items table", "Top Selling Items"),
                ("Staff Performance table", "Staff Performance"),
                ("Adjustments section", "Adjustments"),
                ("Footer with timestamp", "Generated automatically")
            ]
            
            for section_name, search_text in sections_to_check:
                found = search_text in html_content
                print(f"   {section_name}: {'[+]' if found else '[!]'}")
            
        else:
            print(f"[!] Failed to generate email: {result['message']}")
            
    except Exception as e:
        print(f"[!] Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\nTest completed!")
    print(f"Files saved in: {os.path.dirname(__file__)}")


def main():
    """Main function to run the test"""
    try:
        test_email_with_sample_data()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()