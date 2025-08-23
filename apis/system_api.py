import json
from datetime import datetime, timezone
from apis.base_handler import BaseHandler


class HealthHandler(BaseHandler):
    def get(self):
        """Health check endpoint - no authentication required"""
        try:
            # In a real implementation, these would check actual service status
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "services": {
                    "database": "connected",
                    "printer": "ready", 
                    "email": "configured"
                },
                "version": "1.0.0"
            }

            self.write_success(health_data)

        except Exception as e:
            # Even health check should not expose internal errors
            error_data = {
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "services": {
                    "database": "error",
                    "printer": "unknown",
                    "email": "unknown"
                },
                "version": "1.0.0"
            }
            
            self.set_status(503)
            self.write(json.dumps(error_data, default=str))


class SettingsHandler(BaseHandler):
    def get(self):
        """Get system settings - requires authentication and permissions"""
        # In a real implementation, check for system.settings permission
        try:
            # Mock system settings
            settings_data = {
                "general": {
                    "storeName": "Sample Cafe",
                    "storeAddress": "123 Main St, City, State",
                    "phoneNumber": "+1-555-0123",
                    "email": "info@samplecafe.com",
                    "currency": "USD",
                    "timezone": "America/New_York",
                    "language": "en-US"
                },
                "pos": {
                    "receiptTemplate": "standard",
                    "printReceiptAutomatically": True,
                    "askForCustomerName": False,
                    "enableTipping": True,
                    "defaultTipPercentages": [15, 18, 20],
                    "roundingMode": "nearest_nickel"
                },
                "inventory": {
                    "enableLowStockAlerts": True,
                    "lowStockThreshold": 10,
                    "enableExpirationAlerts": True,
                    "expirationWarningDays": 7
                },
                "reports": {
                    "enableAutomaticDailyReports": True,
                    "dailyReportTime": "23:59",
                    "emailReportsTo": ["manager@samplecafe.com"]
                },
                "security": {
                    "sessionTimeoutMinutes": 480,
                    "enableTwoFactorAuth": False,
                    "maxLoginAttempts": 3,
                    "lockoutDurationMinutes": 15
                }
            }

            self.write_success(settings_data, message="System settings retrieved successfully")

        except Exception as e:
            self.write_error_response(["Failed to retrieve system settings"], 500, "INTERNAL_ERROR")

    def put(self):
        """Update system settings - requires authentication and permissions"""
        data = self.get_json_body()
        if data is None:
            return

        try:
            # In a real implementation, validate and save settings to database
            # For now, just return success
            self.write_success({"updated": True}, message="System settings updated successfully")

        except Exception as e:
            self.write_error_response(["Failed to update system settings"], 500, "INTERNAL_ERROR")