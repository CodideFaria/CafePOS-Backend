import tornado.ioloop
import tornado.web
import asyncio
import logging

from apis.menu_api import MenuItemsHandler, MenuItemHandler, MenuItemsBulkImportHandler
from apis.inventory_api import InventoryItemsHandler, InventoryItemHandler, InventoryAdjustHandler, InventoryExportHandler
from apis.roles_api import RolesHandler, RoleHandler
from apis.users_api import UsersHandler, UserHandler
from apis.orders_api import OrdersHandler, OrderHandler, OrderRefundHandler, OrderReprintReceiptHandler
from apis.order_items_api import OrderItemsHandler, OrderItemHandler
from apis.alerts_api import AlertsHandler, AlertHandler
from apis.auth_api import AuthLoginHandler, AuthLogoutHandler, AuthMeHandler, AuthRefreshHandler, AuthValidateSessionHandler, AuthPasswordResetRequestHandler, AuthValidateResetTokenHandler, AuthPasswordResetConfirmHandler
from apis.reports_api import SalesDashboardHandler, DailySalesHandler, EmailDailySummaryHandler, TestEmailHandler
from apis.system_api import HealthHandler, SettingsHandler
from apis.upload_api import ImageUploadHandler, ImageServeHandler, BulkImageUploadHandler, ImageManagementHandler
from services.scheduler_service import scheduler_service

# Configure logging
logging.basicConfig(level=logging.INFO)


def make_app():
    return tornado.web.Application([
        # Authentication
        (r"/auth/login", AuthLoginHandler),
        (r"/auth/logout", AuthLogoutHandler),
        (r"/auth/me", AuthMeHandler),
        (r"/auth/refresh", AuthRefreshHandler),
        (r"/auth/validate-session", AuthValidateSessionHandler),
        (r"/auth/password-reset-request", AuthPasswordResetRequestHandler),
        (r"/auth/validate-reset-token", AuthValidateResetTokenHandler),
        (r"/auth/password-reset-confirm", AuthPasswordResetConfirmHandler),
        
        # Menu items
        (r"/menu_items", MenuItemsHandler),
        (r"/menu_items/([0-9a-fA-F-]+)", MenuItemHandler),
        (r"/menu_items/bulk-import", MenuItemsBulkImportHandler),

        # Inventory
        (r"/inventory", InventoryItemsHandler),
        (r"/inventory/([0-9a-fA-F-]+)", InventoryItemHandler),
        (r"/inventory/([0-9a-fA-F-]+)/adjust", InventoryAdjustHandler),
        (r"/inventory/export", InventoryExportHandler),

        # Roles
        (r"/roles", RolesHandler),
        (r"/roles/([0-9a-fA-F-]+)", RoleHandler),

        # Users
        (r"/users", UsersHandler),
        (r"/users/([0-9a-fA-F-]+)", UserHandler),

        # Orders and Order Items
        (r"/orders", OrdersHandler),
        (r"/orders/([0-9a-fA-F-]+)", OrderHandler),
        (r"/orders/([0-9a-fA-F-]+)/refund", OrderRefundHandler),
        (r"/orders/([0-9a-fA-F-]+)/reprint-receipt", OrderReprintReceiptHandler),
        (r"/order_items", OrderItemsHandler),
        (r"/order_items/([0-9a-fA-F-]+)", OrderItemHandler),

        # Alerts
        (r"/alerts", AlertsHandler),
        (r"/alerts/([0-9a-fA-F-]+)", AlertHandler),

        # Reports
        (r"/sales/dashboard", SalesDashboardHandler),
        (r"/reports/daily-sales", DailySalesHandler),
        (r"/reports/email-daily-summary", EmailDailySummaryHandler),
        (r"/reports/test-email", TestEmailHandler),

        # Image Upload & Management
        (r"/upload/image", ImageUploadHandler),
        (r"/upload/bulk-images", BulkImageUploadHandler),
        (r"/images/management", ImageManagementHandler),
        (r"/images/management/([0-9a-fA-F-]+)", ImageManagementHandler),
        (r"/uploads/(.*)", ImageServeHandler, {"path": "uploads"}),

        # System
        (r"/health", HealthHandler),
        (r"/settings", SettingsHandler),
    ])


async def start_services():
    # Start the scheduler service for daily email reports
    await scheduler_service.start()
    print("Daily email scheduler started")


if __name__ == "__main__":
    app = make_app()
    app.listen(8880)

    print("Server is running on http://localhost:8880")
    
    # Schedule the scheduler service to start after the event loop is running
    tornado.ioloop.IOLoop.current().add_callback(start_services)
    
    tornado.ioloop.IOLoop.current().start()