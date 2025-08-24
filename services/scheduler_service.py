import asyncio
import logging
from datetime import datetime, time, timedelta
from decouple import config
from services.email_service import email_service
from orm.controllers.controller_orders import OrderController

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.running = False
        self.email_recipients = config('DAILY_EMAIL_RECIPIENTS', default='').split(',')
        self.email_time = config('DAILY_EMAIL_TIME', default='07:00')  # Format: HH:MM
        self.order_controller = OrderController()
        
    def parse_time(self, time_str):
        """Parse time string HH:MM to time object"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        except ValueError:
            logger.warning(f"Invalid time format: {time_str}, defaulting to 07:00")
            return time(7, 0)
    
    async def get_real_daily_sales_data(self, date_str):
        """
        Get actual daily sales data from database
        """
        try:
            # Use the order controller to get real database data
            sales_data = self.order_controller.get_daily_sales_data(date_str)
            
            if sales_data is None:
                logger.warning(f"No sales data found for date: {date_str}")
                # Return empty but valid structure
                return {
                    "date": date_str,
                    "summary": {
                        "totalRevenue": 0.0,
                        "totalTransactions": 0,
                        "averageOrderValue": 0.0,
                        "taxCollected": 0.0,
                        "discountsGiven": 0.0,
                        "refundsProcessed": 0.0,
                        "paymentMethods": {
                            "cash": 0.0,
                            "card": 0.0
                        }
                    },
                    "topSellingItems": [],
                    "staffPerformance": []
                }
            
            return sales_data
            
        except Exception as e:
            logger.error(f"Failed to get daily sales data: {str(e)}")
            return None

    async def send_daily_email_report(self):
        """Send daily sales email report"""
        try:
            if not self.email_recipients or not self.email_recipients[0]:
                logger.info("No email recipients configured for daily reports")
                return
            
            # Get yesterday's data (reports are typically sent the next morning)
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Get sales data
            sales_data = await self.get_real_daily_sales_data(yesterday)
            if not sales_data:
                logger.error("Failed to retrieve sales data for daily email")
                return
            
            # Clean up email recipients (remove empty strings)
            recipients = [email.strip() for email in self.email_recipients if email.strip()]
            
            if not recipients:
                logger.info("No valid email recipients configured")
                return
            
            # Send email
            result = email_service.send_daily_sales_summary(recipients, sales_data, yesterday)
            
            if result['success']:
                logger.info(f"Daily sales email sent successfully to {len(recipients)} recipients")
            else:
                logger.error(f"Failed to send daily sales email: {result['message']}")
                
        except Exception as e:
            logger.error(f"Error in daily email task: {str(e)}")

    async def schedule_daily_emails(self):
        """Main scheduler loop for daily emails"""
        target_time = self.parse_time(self.email_time)
        logger.info(f"Email scheduler started - will send daily reports at {target_time}")
        
        while self.running:
            try:
                now = datetime.now()
                current_time = now.time()
                
                # Check if it's time to send the email (within 1 minute window)
                if (current_time.hour == target_time.hour and 
                    current_time.minute == target_time.minute):
                    
                    logger.info("Sending daily sales email report...")
                    await self.send_daily_email_report()
                    
                    # Sleep for 61 seconds to avoid sending multiple emails in the same minute
                    await asyncio.sleep(61)
                else:
                    # Check every 30 seconds
                    await asyncio.sleep(30)
                    
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def start(self):
        """Start the scheduler service"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        logger.info("Starting scheduler service...")
        
        # Create task for daily email scheduling
        asyncio.create_task(self.schedule_daily_emails())
    
    def stop(self):
        """Stop the scheduler service"""
        logger.info("Stopping scheduler service...")
        self.running = False
    
    async def send_test_email(self, recipients=None):
        """Send a test daily sales email immediately"""
        try:
            if not recipients:
                recipients = [email.strip() for email in self.email_recipients if email.strip()]
            
            if not recipients:
                return {
                    'success': False,
                    'message': 'No recipients provided or configured'
                }
            
            # Get today's data for testing
            today = datetime.now().strftime('%Y-%m-%d')
            sales_data = await self.get_real_daily_sales_data(today)
            
            if not sales_data:
                return {
                    'success': False,
                    'message': 'Failed to retrieve sales data'
                }
            
            # Send test email
            result = email_service.send_daily_sales_summary(recipients, sales_data, today)
            
            if result['success']:
                logger.info(f"Test email sent successfully to {recipients}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending test email: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

# Global scheduler instance
scheduler_service = SchedulerService()