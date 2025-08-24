#!/usr/bin/env python3
"""
Test script for daily email functionality
Generates HTML email content without sending to preserve costs
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.scheduler_service import scheduler_service
from services.email_service import email_service
from orm.controllers.controller_orders import OrderController


async def test_daily_email_html():
    """Test the daily email generation and save HTML to file"""
    print("Testing Daily Email HTML Generation")
    print("=" * 50)
    
    # Initialize order controller
    order_controller = OrderController()
    
    # Test with today's date and yesterday's date
    test_dates = [
        datetime.now().strftime('%Y-%m-%d'),  # Today
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday
    ]
    
    for i, test_date in enumerate(test_dates, 1):
        print(f"\nTest {i}: Generating email for {test_date}")
        
        try:
            # Get sales data using the same method as scheduler
            sales_data = await scheduler_service.get_real_daily_sales_data(test_date)
            
            if sales_data is None:
                print(f"[!] No sales data found for {test_date}")
                continue
                
            print(f"[+] Sales data retrieved successfully")
            print(f"   Total Revenue: ${sales_data['summary']['totalRevenue']:.2f}")
            print(f"   Total Transactions: {sales_data['summary']['totalTransactions']}")
            print(f"   Average Order Value: ${sales_data['summary']['averageOrderValue']:.2f}")
            
            # Create a modified email service that captures HTML instead of sending
            class TestEmailService:
                def __init__(self):
                    self.captured_html = None
                    self.captured_subject = None
                    
                def send_email(self, recipients, subject, html_body, text_body=None):
                    """Capture email data instead of sending"""
                    self.captured_html = html_body
                    self.captured_subject = subject
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
                recipients=['test@example.com'], 
                sales_data=sales_data, 
                date=test_date
            )
            
            # Restore original method
            email_service.send_email = original_send_email
            
            if result['success']:
                # Save HTML to file
                filename = f"daily_email_test_{test_date}.html"
                filepath = os.path.join(os.path.dirname(__file__), filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(test_service.captured_html)
                
                print(f"[+] HTML email generated successfully")
                print(f"   Subject: {test_service.captured_subject}")
                print(f"   File saved: {filename}")
                print(f"   File path: {filepath}")
                
                # Print some data verification
                html_content = test_service.captured_html
                print(f"\nData Verification:")
                print(f"   Revenue appears in HTML: {'€{:.2f}'.format(sales_data['summary']['totalRevenue']) in html_content}")
                print(f"   Transaction count appears: {str(sales_data['summary']['totalTransactions']) in html_content}")
                print(f"   Date appears: {test_date in html_content}")
                
                # Check for data accuracy indicators
                payment_methods = sales_data['summary']['paymentMethods']
                print(f"   Payment methods data:")
                for method, amount in payment_methods.items():
                    appears_in_html = f"€{amount:.2f}" in html_content
                    status = "[+]" if appears_in_html else "[!]"
                    print(f"     {method.title()}: €{amount:.2f} - {status}")
                
                if sales_data.get('topSellingItems'):
                    print(f"   Top selling items: {len(sales_data['topSellingItems'])} items")
                    for item in sales_data['topSellingItems'][:3]:
                        item_in_html = item['name'] in html_content
                        status = "[+]" if item_in_html else "[!]"
                        print(f"     {item['name']}: {item['quantitySold']} sold - {status}")
                
                if sales_data.get('staffPerformance'):
                    print(f"   Staff performance: {len(sales_data['staffPerformance'])} staff members")
                    for staff in sales_data['staffPerformance'][:3]:
                        staff_in_html = staff['name'] in html_content
                        status = "[+]" if staff_in_html else "[!]"
                        print(f"     {staff['name']}: {staff['transactions']} transactions - {status}")
                
            else:
                print(f"[!] Failed to generate email: {result['message']}")
                
        except Exception as e:
            print(f"[!] Error testing date {test_date}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\nTest completed!")
    print(f"HTML files saved in: {os.path.dirname(__file__)}")


def main():
    """Main function to run the test"""
    try:
        # Run the async test
        asyncio.run(test_daily_email_html())
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()