"""
Printer API for CafePOS
Handles printer testing and configuration
"""

from apis.base_handler import BaseHandler
from services.printer_service import printer_service


class PrinterTestHandler(BaseHandler):
    """Handle printer testing requests"""
    
    def post(self):
        """Test the printer with a test receipt"""
        try:
            test_result = printer_service.test_printer()
            
            if test_result.get('success', False):
                self.write_success(test_result, message="Printer test completed successfully")
            else:
                self.write_error_response([f"Printer test failed: {test_result.get('error', 'Unknown error')}"], 500, "PRINTER_TEST_FAILED")
                
        except Exception as e:
            self.write_error_response([f"Printer test error: {str(e)}"], 500, "INTERNAL_ERROR")


class PrinterStatusHandler(BaseHandler):
    """Handle printer status requests"""
    
    def get(self):
        """Get current printer status and configuration"""
        try:
            status_data = {
                "available": printer_service.is_printer_available(),
                "type": printer_service.printer_type,
                "enabled": printer_service.printer_enabled,
                "testMode": printer_service.test_mode,
                "configuration": {
                    "printerType": printer_service.printer_type,
                    "enabled": printer_service.printer_enabled,
                    "testMode": printer_service.test_mode
                }
            }
            
            self.write_success(status_data, message="Printer status retrieved successfully")
            
        except Exception as e:
            self.write_error_response([f"Failed to get printer status: {str(e)}"], 500, "INTERNAL_ERROR")