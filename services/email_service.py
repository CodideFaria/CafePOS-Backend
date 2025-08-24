import requests
from datetime import datetime, timezone
from decouple import config
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.postmark_token = config('POSTMARK_SERVER_TOKEN', default='')
        self.postmark_url = "https://api.postmarkapp.com/email"
        self.email_from = config('EMAIL_FROM', default='noreply@cafepos.local')
        self.use_mock = not self.postmark_token or self.postmark_token == ''

    def send_email(self, to_addresses, subject, html_body, text_body=None, attachments=None):
        """
        Send email using Postmark API
        
        Args:
            to_addresses (list): List of recipient email addresses
            subject (str): Email subject
            html_body (str): HTML email content
            text_body (str, optional): Plain text email content
            attachments (list, optional): List of attachments (not implemented for Postmark yet)
            
        Returns:
            dict: Result with success status and message
        """
        try:
            if self.use_mock:
                # For development - just log the email
                logger.info(f"EMAIL SENT (MOCK): To={to_addresses}, Subject={subject}")
                return {
                    'success': True,
                    'message': 'Email sent successfully (mock mode)',
                    'mock': True
                }

            # Send via Postmark API
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': self.postmark_token
            }

            # Postmark supports multiple recipients, but it's better to send individual emails
            for recipient in to_addresses:
                payload = {
                    'From': self.email_from,
                    'To': recipient,
                    'Subject': subject,
                    'HtmlBody': html_body,
                    'MessageStream': 'outbound'
                }

                # Add text body if provided
                if text_body:
                    payload['TextBody'] = text_body

                response = requests.post(self.postmark_url, json=payload, headers=headers)
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get('Message', f'HTTP {response.status_code}')
                    logger.error(f"Postmark API error for {recipient}: {error_msg}")
                    return {
                        'success': False,
                        'message': f'Postmark API error: {error_msg}',
                        'error': error_msg
                    }

            return {
                'success': True,
                'message': f'Email sent successfully to {len(to_addresses)} recipients',
                'mock': False
            }

        except Exception as e:
            logger.error(f"Failed to send email via Postmark: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send email: {str(e)}',
                'error': str(e)
            }


    def send_daily_sales_summary(self, recipients, sales_data, date):
        """
        Send daily sales summary email with formatted data
        
        Args:
            recipients (list): List of recipient email addresses
            sales_data (dict): Daily sales data from reports API
            date (str): Date for the report
            
        Returns:
            dict: Result with success status and message
        """
        try:
            subject = f"CafePOS Daily Sales Summary - {date}"
            
            # Generate payment methods table
            payment_methods_html = ""
            total_revenue = sales_data['summary']['totalRevenue']
            for method, amount in sales_data['summary']['paymentMethods'].items():
                percentage = (amount / total_revenue) * 100 if total_revenue > 0 else 0
                payment_methods_html += f"""
                <tr>
                    <td>{method.title()}</td>
                    <td>€{amount:.2f}</td>
                    <td>{percentage:.1f}%</td>
                </tr>"""

            # Generate top selling items table
            top_items_html = ""
            if sales_data.get('topSellingItems'):
                for item in sales_data['topSellingItems'][:5]:
                    top_items_html += f"""
                    <tr>
                        <td>{item['name']}</td>
                        <td>{item['quantitySold']}</td>
                        <td>€{item['revenue']:.2f}</td>
                    </tr>"""

            # Generate staff performance table
            staff_performance_html = ""
            if sales_data.get('staffPerformance'):
                for staff in sales_data['staffPerformance']:
                    staff_performance_html += f"""
                    <tr>
                        <td>{staff['name']}</td>
                        <td>{staff['transactions']}</td>
                        <td>€{staff['revenue']:.2f}</td>
                        <td>€{staff['averageOrderValue']:.2f}</td>
                    </tr>"""

            # Generate HTML email template
            summary = sales_data['summary']
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Daily Sales Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #8B4513; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .summary-box {{ background: #f4f4f4; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric {{ background: white; padding: 15px; border-left: 4px solid #8B4513; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #8B4513; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
        .footer {{ background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>☕ CafePOS Daily Sales Summary</h1>
        <p>{date}</p>
    </div>
    
    <div class="content">
        <div class="summary-box">
            <h2>📊 Key Metrics</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">€{summary['totalRevenue']:.2f}</div>
                    <div class="metric-label">Total Revenue</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary['totalTransactions']}</div>
                    <div class="metric-label">Total Transactions</div>
                </div>
                <div class="metric">
                    <div class="metric-value">€{summary['averageOrderValue']:.2f}</div>
                    <div class="metric-label">Average Order Value</div>
                </div>
                <div class="metric">
                    <div class="metric-value">€{summary['taxCollected']:.2f}</div>
                    <div class="metric-label">Tax Collected</div>
                </div>
            </div>
        </div>

        <div class="summary-box">
            <h2>💳 Payment Methods</h2>
            <table>
                <tr>
                    <th>Payment Method</th>
                    <th>Amount</th>
                    <th>Percentage</th>
                </tr>
                {payment_methods_html}
            </table>
        </div>"""

            # Add top selling items section if data exists
            if sales_data.get('topSellingItems'):
                html_body += f"""
        <div class="summary-box">
            <h2>🏆 Top Selling Items</h2>
            <table>
                <tr>
                    <th>Item</th>
                    <th>Quantity Sold</th>
                    <th>Revenue</th>
                </tr>
                {top_items_html}
            </table>
        </div>"""

            # Add staff performance section if data exists
            if sales_data.get('staffPerformance'):
                html_body += f"""
        <div class="summary-box">
            <h2>👥 Staff Performance</h2>
            <table>
                <tr>
                    <th>Staff Member</th>
                    <th>Transactions</th>
                    <th>Revenue</th>
                    <th>Avg Order Value</th>
                </tr>
                {staff_performance_html}
            </table>
        </div>"""

            # Add adjustments section if there are discounts or refunds
            if summary.get('discountsGiven', 0) > 0 or summary.get('refundsProcessed', 0) > 0:
                html_body += f"""
        <div class="summary-box">
            <h2>💰 Adjustments</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value negative">€{summary.get('discountsGiven', 0):.2f}</div>
                    <div class="metric-label">Discounts Given</div>
                </div>
                <div class="metric">
                    <div class="metric-value negative">€{summary.get('refundsProcessed', 0):.2f}</div>
                    <div class="metric-label">Refunds Processed</div>
                </div>
            </div>
        </div>"""

            html_body += f"""
    </div>
    
    <div class="footer">
        <p>Generated automatically by CafePOS at {timestamp}</p>
        <p>This is an automated email - please do not reply</p>
    </div>
</body>
</html>"""

            # Generate plain text version
            text_body = f"""
CafePOS Daily Sales Summary - {date}
{'=' * 50}

KEY METRICS:
- Total Revenue: €{sales_data['summary']['totalRevenue']:.2f}
- Total Transactions: {sales_data['summary']['totalTransactions']}
- Average Order Value: €{sales_data['summary']['averageOrderValue']:.2f}
- Tax Collected: €{sales_data['summary']['taxCollected']:.2f}

PAYMENT METHODS:
"""
            for method, amount in sales_data['summary']['paymentMethods'].items():
                text_body += f"- {method.title()}: €{amount:.2f}\n"

            if sales_data.get('topSellingItems'):
                text_body += f"\nTOP SELLING ITEMS:\n"
                for item in sales_data['topSellingItems'][:5]:
                    text_body += f"- {item['name']}: {item['quantitySold']} sold (€{item['revenue']:.2f})\n"

            text_body += f"\nGenerated at: {datetime.now(timezone.utc).isoformat()}"

            # HTML body was already constructed above

            # Send email
            return self.send_email(recipients, subject, html_body, text_body)

        except Exception as e:
            logger.error(f"Failed to generate daily sales summary email: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to generate email: {str(e)}',
                'error': str(e)
            }

    def send_password_reset_email(self, recipient, reset_token, reset_url):
        """
        Send password reset email with secure token
        
        Args:
            recipient (str): Email address
            reset_token (str): Password reset token
            reset_url (str): Base URL for password reset
            
        Returns:
            dict: Result with success status and message
        """
        try:
            subject = "CafePOS - Password Reset Request"
            reset_link = f"{reset_url}?token={reset_token}"
            
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Password Reset</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #8B4513; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #8B4513; color: white; text-decoration: none; border-radius: 5px; }}
        .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #666; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>☕ CafePOS</h1>
            <p>Password Reset Request</p>
        </div>
        
        <div class="content">
            <h2>Reset Your Password</h2>
            <p>You have requested to reset your password for your CafePOS account.</p>
            <p>Click the button below to reset your password:</p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </p>
            
            <div class="warning">
                <strong>Security Notice:</strong>
                <ul>
                    <li>This link will expire in 1 hour</li>
                    <li>If you didn't request this reset, please ignore this email</li>
                    <li>Never share this link with anyone</li>
                </ul>
            </div>
            
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #fff; padding: 10px; border: 1px solid #ddd;">{reset_link}</p>
        </div>
        
        <div class="footer">
            <p>This is an automated email - please do not reply</p>
            <p>CafePOS Security Team</p>
        </div>
    </div>
</body>
</html>"""

            text_body = f"""
CafePOS - Password Reset Request

You have requested to reset your password for your CafePOS account.

Reset your password by visiting this link:
{reset_link}

SECURITY NOTICE:
- This link will expire in 1 hour
- If you didn't request this reset, please ignore this email
- Never share this link with anyone

This is an automated email - please do not reply.
            """

            return self.send_email([recipient], subject, html_body, text_body)

        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send password reset email: {str(e)}',
                'error': str(e)
            }


# Global email service instance
email_service = EmailService()