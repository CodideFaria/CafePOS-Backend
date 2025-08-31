"""
Printer Service for CafePOS
Handles receipt printing using python-escpos
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from decouple import config

try:
    from escpos.printer import Usb, Network, File, Dummy
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False
    logging.warning("python-escpos not available, printer functionality will be mocked")

class PrinterService:
    def __init__(self):
        self.printer_type = config('PRINTER_TYPE', default='file')
        self.printer_enabled = config('PRINTER_ENABLED', default='true', cast=bool)
        self.test_mode = config('PRINTER_TEST_MODE', default='false', cast=bool)
        
        # Printer configuration
        usb_vendor_hex = config('PRINTER_USB_VENDOR_ID', default='0x04b8')
        usb_product_hex = config('PRINTER_USB_PRODUCT_ID', default='0x0202')
        
        self.printer_config = {
            'usb_vendor_id': int(usb_vendor_hex, 16) if usb_vendor_hex.startswith('0x') else int(usb_vendor_hex),
            'usb_product_id': int(usb_product_hex, 16) if usb_product_hex.startswith('0x') else int(usb_product_hex),
            'network_ip': config('PRINTER_NETWORK_IP', default='192.168.1.100'),
            'network_port': config('PRINTER_NETWORK_PORT', default=9100, cast=int),
            'file_path': config('PRINTER_FILE_PATH', default='./receipts/receipt.txt'),
        }
        
        self.printer = None
        self._initialize_printer()
    
    def _initialize_printer(self):
        """Initialize the printer based on configuration"""
        if not ESCPOS_AVAILABLE or not self.printer_enabled:
            self.printer = None
            return
            
        try:
            if self.test_mode:
                # Use dummy printer for testing
                self.printer = Dummy()
            elif self.printer_type == 'usb':
                self.printer = Usb(
                    self.printer_config['usb_vendor_id'],
                    self.printer_config['usb_product_id']
                )
            elif self.printer_type == 'network':
                self.printer = Network(
                    self.printer_config['network_ip'],
                    self.printer_config['network_port']
                )
            elif self.printer_type == 'file':
                # Ensure directory exists
                file_path = self.printer_config['file_path']
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                self.printer = File(file_path)
            else:
                logging.error(f"Unsupported printer type: {self.printer_type}")
                self.printer = None
                
        except Exception as e:
            logging.error(f"Failed to initialize printer: {e}")
            self.printer = None
    
    def is_printer_available(self) -> bool:
        """Check if printer is available and ready"""
        return self.printer is not None and ESCPOS_AVAILABLE and self.printer_enabled
    
    def print_receipt(self, order_data: Dict[str, Any], reprint: bool = False) -> Dict[str, Any]:
        """
        Print a receipt for an order
        
        Args:
            order_data: Order information
            reprint: Whether this is a reprint
            
        Returns:
            dict: Print result with success status and details
        """
        try:
            if not self.is_printer_available():
                return self._mock_print_result(order_data, reprint)
            
            # Format receipt content
            receipt_content = self._format_receipt(order_data, reprint)
            
            # Print to thermal printer
            self._print_thermal_receipt(receipt_content, order_data)
            
            return {
                'success': True,
                'printed': True,
                'reprint': reprint,
                'printer_type': self.printer_type,
                'timestamp': datetime.now().isoformat(),
                'order_id': order_data.get('id'),
                'mock': False
            }
            
        except Exception as e:
            logging.error(f"Printing failed: {e}")
            return {
                'success': False,
                'printed': False,
                'error': str(e),
                'mock': False
            }
    
    def _format_receipt(self, order_data: Dict[str, Any], reprint: bool = False) -> Dict[str, Any]:
        """Format order data into receipt format"""
        
        # Get business info (could be from settings in the future)
        business_name = config('BUSINESS_NAME', default='Sample Cafe')
        business_address = config('BUSINESS_ADDRESS', default='123 Main Street')
        business_phone = config('BUSINESS_PHONE', default='(555) 123-4567')
        
        # Order items
        items = order_data.get('items', [])
        subtotal = float(order_data.get('subtotal', 0))
        tax_amount = float(order_data.get('tax_amount', 0))
        total_amount = float(order_data.get('total_amount', 0))
        discount_amount = float(order_data.get('discount_amount', 0))
        
        return {
            'business_name': business_name,
            'business_address': business_address,
            'business_phone': business_phone,
            'order_number': order_data.get('order_number', 'N/A'),
            'order_date': order_data.get('created_at', datetime.now().isoformat()),
            'cashier': order_data.get('staff_id', 'Unknown'),
            'items': items,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'discount_amount': discount_amount,
            'total_amount': total_amount,
            'payment_method': order_data.get('payment_method', 'cash'),
            'cash_received': float(order_data.get('cash_received', 0)),
            'change_amount': float(order_data.get('change_amount', 0)),
            'reprint': reprint
        }
    
    def _print_thermal_receipt(self, receipt_data: Dict[str, Any], order_data: Dict[str, Any]):
        """Print formatted receipt to thermal printer"""
        try:
            p = self.printer
            
            # Reset printer
            p.hw("init")
            
            # Header
            p.set("center", "b", "on", 2, 2)
            p.text(f"{receipt_data['business_name']}\n")
            p.set("center", "normal", "off", 1, 1)
            p.text(f"{receipt_data['business_address']}\n")
            p.text(f"{receipt_data['business_phone']}\n")
            p.text("=" * 32 + "\n")
            
            # Order info
            if receipt_data['reprint']:
                p.set("center", "b", "on", 1, 1)
                p.text("*** REPRINT ***\n")
                p.set("left", "normal", "off", 1, 1)
            
            p.text(f"Order: {receipt_data['order_number']}\n")
            order_date = datetime.fromisoformat(receipt_data['order_date'].replace('Z', '+00:00'))
            p.text(f"Date: {order_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
            p.text(f"Cashier: {receipt_data['cashier']}\n")
            p.text("-" * 32 + "\n")
            
            # Items
            for item in receipt_data['items']:
                name = item.get('product_name', 'Unknown Item')
                size = item.get('size', '')
                quantity = item.get('quantity', 1)
                price = float(item.get('price', 0))
                line_total = quantity * price
                
                # Item line
                item_line = f"{name}"
                if size and size != 'Regular':
                    item_line += f" ({size})"
                p.text(f"{item_line}\n")
                
                # Quantity and price line
                qty_price_line = f"  {quantity}x ${price:.2f}"
                total_str = f"${line_total:.2f}"
                spaces = 32 - len(qty_price_line) - len(total_str)
                p.text(f"{qty_price_line}{' ' * spaces}{total_str}\n")
            
            p.text("-" * 32 + "\n")
            
            # Totals
            def print_total_line(label: str, amount: float):
                amount_str = f"${amount:.2f}"
                spaces = 32 - len(label) - len(amount_str)
                p.text(f"{label}{' ' * spaces}{amount_str}\n")
            
            print_total_line("Subtotal:", receipt_data['subtotal'])
            
            if receipt_data['discount_amount'] > 0:
                print_total_line("Discount:", -receipt_data['discount_amount'])
            
            print_total_line("Tax:", receipt_data['tax_amount'])
            
            p.set("left", "b", "on", 1, 1)
            print_total_line("TOTAL:", receipt_data['total_amount'])
            p.set("left", "normal", "off", 1, 1)
            
            p.text("=" * 32 + "\n")
            
            # Payment info
            payment_method = receipt_data['payment_method'].upper()
            print_total_line(f"{payment_method}:", receipt_data['total_amount'])
            
            if payment_method == 'CASH' and receipt_data['cash_received'] > 0:
                print_total_line("Cash Received:", receipt_data['cash_received'])
                if receipt_data['change_amount'] > 0:
                    print_total_line("Change:", receipt_data['change_amount'])
            
            # Footer
            p.text("\n")
            p.set("center", "normal", "off", 1, 1)
            p.text("Thank you for your visit!\n")
            p.text("Please come again\n")
            p.text("\n")
            
            # Cut paper
            p.cut()
            
            # If cash payment, open cash drawer
            if payment_method == 'CASH':
                p.cashdraw(2)
            
        except Exception as e:
            logging.error(f"Thermal printing failed: {e}")
            raise
    
    def _mock_print_result(self, order_data: Dict[str, Any], reprint: bool = False) -> Dict[str, Any]:
        """Return mock print result when printer is not available"""
        return {
            'success': True,
            'printed': True,
            'reprint': reprint,
            'printer_type': 'mock',
            'timestamp': datetime.now().isoformat(),
            'order_id': order_data.get('id'),
            'mock': True,
            'reason': 'Printer not available or disabled'
        }
    
    def test_printer(self) -> Dict[str, Any]:
        """Test printer with a test receipt"""
        test_order = {
            'id': 'test-12345',
            'order_number': 'TEST001',
            'created_at': datetime.now().isoformat(),
            'staff_id': 'test-user',
            'items': [
                {
                    'product_name': 'Test Coffee',
                    'size': 'Medium',
                    'quantity': 1,
                    'price': 4.50
                }
            ],
            'subtotal': 4.50,
            'tax_amount': 0.36,
            'total_amount': 4.86,
            'discount_amount': 0.0,
            'payment_method': 'cash',
            'cash_received': 5.00,
            'change_amount': 0.14
        }
        
        result = self.print_receipt(test_order, reprint=False)
        result['test_mode'] = True
        return result

# Global printer service instance
printer_service = PrinterService()