# Backend Data Models and Payload Structures for CafePOS

This document defines all data models, validation rules, and payload structures that the backend must implement to support the CafePOS frontend application.

## Data Types and Formats

### Standard Field Types
- **UUID**: 36-character string (e.g., `"550e8400-e29b-41d4-a716-446655440000"`)
- **Timestamp**: ISO 8601 format (e.g., `"2024-01-01T10:30:00.000Z"`)
- **Decimal**: String or number with 2 decimal places for currency (e.g., `"12.99"` or `12.99`)
- **Email**: Valid email format with RFC 5322 compliance
- **Phone**: Optional international format (e.g., `"+1-555-123-4567"`)

### Validation Constants
```json
{
  "MAX_NAME_LENGTH": 100,
  "MAX_DESCRIPTION_LENGTH": 1000,
  "MAX_USERNAME_LENGTH": 50,
  "MIN_PASSWORD_LENGTH": 8,
  "PIN_CODE_LENGTH": 4,
  "MAX_PRICE": 9999.99,
  "MIN_PRICE": 0.01,
  "MAX_QUANTITY": 999,
  "TAX_RATE": 0.08
}
```

## 1. User Management Models

### User Model
```json
{
  "id": "string (UUID)",
  "username": "string (3-50 chars, alphanumeric + underscore)",
  "firstName": "string (1-50 chars)",
  "lastName": "string (1-50 chars)", 
  "email": "string (valid email format)",
  "role": "admin|manager|cashier|trainee",
  "permissions": ["string[]"] ,
  "isActive": "boolean",
  "pinCode": "string (4 digits, nullable)",
  "failedLoginAttempts": "number (0-10)",
  "lockedUntil": "string (ISO timestamp, nullable)",
  "lastLogin": "string (ISO timestamp, nullable)",
  "shiftStartTime": "string (ISO timestamp, nullable)",
  "shiftEndTime": "string (ISO timestamp, nullable)",
  "createdAt": "string (ISO timestamp)",
  "updatedAt": "string (ISO timestamp)"
}
```

**Validation Rules:**
- `username`: Required, 3-50 characters, alphanumeric + underscore, case-insensitive unique
- `firstName`: Required, 1-50 characters, letters and spaces only
- `lastName`: Required, 1-50 characters, letters and spaces only
- `email`: Required, valid email format, case-insensitive unique
- `role`: Required, must be one of the defined enum values
- `pinCode`: Optional, exactly 4 digits, hashed when stored
- `permissions`: Array of valid permission strings

### Authentication Payloads

#### Login Request
```json
{
  "username": "string (required if password provided)",
  "password": "string (required if username provided)",
  "pinCode": "string (required if username/password not provided)",
  "rememberMe": "boolean (optional, default false)"
}
```

#### Login Response
```json
{
  "user": {
    "id": "string",
    "username": "string",
    "firstName": "string", 
    "lastName": "string",
    "email": "string",
    "role": "string",
    "permissions": ["string"],
    "isActive": "boolean",
    "lastLogin": "string",
    "shiftStartTime": "string",
    "shiftEndTime": "string"
  },
  "token": "string (JWT)",
  "tokenExpiry": "string (ISO timestamp)",
  "sessionId": "string (UUID)"
}
```

#### User Creation Request
```json
{
  "username": "string (required, 3-50 chars)",
  "firstName": "string (required, 1-50 chars)",
  "lastName": "string (required, 1-50 chars)",
  "email": "string (required, valid email)",
  "role": "string (required, valid role)",
  "password": "string (required, min 8 chars)",
  "pinCode": "string (optional, 4 digits)",
  "isActive": "boolean (optional, default true)"
}
```

## 2. Menu Management Models

### MenuItem Model
```json
{
  "id": "string (UUID)",
  "name": "string (1-100 chars)",
  "size": "string (1-50 chars)",
  "price": "number (0.01-9999.99, 2 decimal places)",
  "category": "string (1-50 chars, optional)",
  "description": "string (max 500 chars, optional)",
  "imageUrl": "string (valid URL, optional)",
  "isActive": "boolean",
  "sortOrder": "number (integer, default 0)",
  "createdAt": "string (ISO timestamp)",
  "updatedAt": "string (ISO timestamp)"
}
```

**Validation Rules:**
- `name`: Required, 1-100 characters, trim whitespace
- `size`: Required, 1-50 characters (e.g., "Small", "Medium", "Large")
- `price`: Required, positive number with exactly 2 decimal places
- `category`: Optional, 1-50 characters, defaults to "General"
- `isActive`: Boolean, defaults to true

### Menu Creation/Update Request
```json
{
  "name": "string (required)",
  "size": "string (required)",
  "price": "number (required)",
  "category": "string (optional)",
  "description": "string (optional)",
  "imageUrl": "string (optional, valid URL)",
  "isActive": "boolean (optional, default true)",
  "sortOrder": "number (optional, default 0)"
}
```

### Menu Items Response
```json
{
  "menu_items": [
    {
      "id": "string",
      "name": "string",
      "size": "string",
      "price": "number",
      "category": "string",
      "description": "string",
      "imageUrl": "string",
      "isActive": "boolean",
      "sortOrder": "number",
      "createdAt": "string",
      "updatedAt": "string"
    }
  ],
  "amount": "number (total count)"
}
```

## 3. Order and Sales Models

### Order Model
```json
{
  "id": "string (UUID)",
  "orderNumber": "string (human-readable, e.g., 'ORD-2024-0001')",
  "items": [
    {
      "id": "string (UUID)",
      "product": {
        "id": "string",
        "name": "string",
        "size": "string", 
        "price": "number"
      },
      "quantity": "number (1-999)",
      "unitPrice": "number",
      "lineTotal": "number",
      "notes": "string (optional, max 200 chars)",
      "addedAt": "string (ISO timestamp)"
    }
  ],
  "discount": {
    "id": "string (UUID)",
    "type": "percentage|fixed",
    "value": "number",
    "discountAmount": "number",
    "reason": "string (required, max 255 chars)",
    "staffId": "string (UUID)",
    "appliedAt": "string (ISO timestamp)"
  },
  "subtotal": "number (2 decimal places)",
  "discountAmount": "number (2 decimal places)",
  "taxAmount": "number (2 decimal places)",
  "total": "number (2 decimal places)",
  "paymentMethod": "cash|card",
  "cashReceived": "number (required if cash payment)",
  "changeAmount": "number",
  "status": "completed|refunded|voided",
  "staffId": "string (UUID)",
  "customerName": "string (optional, max 100 chars)",
  "customerEmail": "string (optional, valid email)",
  "notes": "string (optional, max 500 chars)",
  "reprintCount": "number (default 0)",
  "lastReprint": "string (ISO timestamp, nullable)",
  "timestamp": "string (ISO timestamp)",
  "createdAt": "string (ISO timestamp)",
  "updatedAt": "string (ISO timestamp)"
}
```

### Order Creation Request
```json
{
  "items": [
    {
      "menuItemId": "string (UUID, required)",
      "quantity": "number (required, 1-999)",
      "notes": "string (optional, max 200 chars)"
    }
  ],
  "discount": {
    "type": "percentage|fixed",
    "value": "number (required)",
    "reason": "string (required, max 255 chars)"
  },
  "paymentMethod": "cash|card (required)",
  "cashReceived": "number (required if cash)",
  "customerName": "string (optional)",
  "customerEmail": "string (optional, valid email)",
  "notes": "string (optional)"
}
```

### Order Response
```json
{
  "order": {
    "id": "string",
    "orderNumber": "string",
    "items": [...],
    "discount": {...},
    "subtotal": "number",
    "discountAmount": "number", 
    "taxAmount": "number",
    "total": "number",
    "paymentMethod": "string",
    "cashReceived": "number",
    "changeAmount": "number",
    "timestamp": "string",
    "staffId": "string",
    "status": "string"
  },
  "receipt": {
    "receiptNumber": "string",
    "printData": "string (formatted receipt text)"
  }
}
```

**Business Rules:**
- `subtotal` = sum of all (item.unitPrice × item.quantity)
- `discountAmount` = calculated based on discount type and value
- `taxAmount` = (subtotal - discountAmount) × TAX_RATE
- `total` = subtotal - discountAmount + taxAmount
- `changeAmount` = cashReceived - total (if cash payment)
- Order number format: "ORD-YYYY-NNNN" (auto-generated)

## 4. Inventory Management Models

### InventoryItem Model
```json
{
  "id": "string (UUID)",
  "name": "string (1-100 chars)",
  "category": "string (1-50 chars)",
  "currentStock": "number (decimal, 3 decimal places)",
  "minStockLevel": "number (decimal, 3 decimal places)",
  "maxStockLevel": "number (decimal, 3 decimal places)",
  "unit": "string (required, e.g., 'kg', 'liters', 'pieces')",
  "costPerUnit": "number (4 decimal places)",
  "supplier": "string (optional, max 100 chars)",
  "lastRestocked": "string (ISO timestamp, nullable)",
  "expiryDate": "string (ISO timestamp, nullable)",
  "barcode": "string (optional, max 50 chars)",
  "description": "string (optional, max 500 chars)",
  "location": "string (optional, max 100 chars)",
  "status": "in_stock|low_stock|out_of_stock|expired",
  "createdAt": "string (ISO timestamp)",
  "updatedAt": "string (ISO timestamp)"
}
```

**Status Calculation Logic:**
- `expired`: expiryDate < current date
- `out_of_stock`: currentStock <= 0
- `low_stock`: currentStock <= minStockLevel
- `in_stock`: currentStock > minStockLevel

### Stock Movement Model
```json
{
  "id": "string (UUID)",
  "inventoryItemId": "string (UUID)",
  "type": "restock|usage|waste|adjustment",
  "quantity": "number (positive for add, negative for remove)",
  "previousStock": "number",
  "newStock": "number", 
  "reason": "string (required, max 255 chars)",
  "staffId": "string (UUID)",
  "cost": "number (optional, total cost of movement)",
  "supplier": "string (optional, for restock movements)",
  "referenceOrderId": "string (UUID, optional)",
  "notes": "string (optional, max 500 chars)",
  "timestamp": "string (ISO timestamp)"
}
```

### Stock Adjustment Request
```json
{
  "inventoryItemId": "string (UUID, required)",
  "type": "restock|usage|waste|adjustment",
  "quantity": "number (required)",
  "reason": "string (required, max 255 chars)",
  "cost": "number (optional)",
  "supplier": "string (optional)",
  "notes": "string (optional)"
}
```

## 5. Dashboard and Analytics Models

### Sales Metrics Model
```json
{
  "totalRevenue": "number (2 decimal places)",
  "dailyRevenue": "number",
  "weeklyRevenue": "number",
  "monthlyRevenue": "number",
  "totalTransactions": "number (integer)",
  "dailyTransactions": "number (integer)",
  "averageOrderValue": "number (2 decimal places)",
  "totalCustomers": "number (integer)",
  "returningCustomers": "number (integer)",
  "newCustomers": "number (integer)",
  "periodStart": "string (ISO timestamp)",
  "periodEnd": "string (ISO timestamp)",
  "lastUpdated": "string (ISO timestamp)"
}
```

### Chart Data Point Model
```json
{
  "date": "string (YYYY-MM-DD)",
  "revenue": "number",
  "transactions": "number",
  "averageOrderValue": "number",
  "hour": "number (0-23, for hourly breakdowns)"
}
```

### Top Selling Product Model
```json
{
  "id": "string",
  "name": "string",
  "category": "string",
  "quantitySold": "number",
  "revenue": "number",
  "profitMargin": "number (percentage)",
  "rankPosition": "number",
  "image": "string (URL, optional)"
}
```

## 6. Permission and Security Models

### Permission Model
```json
{
  "id": "string (dot notation, e.g., 'menu.view')",
  "name": "string (display name)",
  "category": "string (grouping category)",
  "description": "string",
  "isSystemPermission": "boolean (cannot be deleted)"
}
```

### Role Model
```json
{
  "id": "string (UUID)",
  "name": "string (unique, 1-50 chars)",
  "description": "string (optional, max 500 chars)",
  "permissions": ["string (permission IDs)"],
  "isSystemRole": "boolean (cannot be deleted)",
  "userCount": "number (users assigned to this role)",
  "createdAt": "string (ISO timestamp)",
  "updatedAt": "string (ISO timestamp)"
}
```

## 7. Audit and Logging Models

### Audit Log Entry Model
```json
{
  "id": "string (UUID)",
  "userId": "string (UUID, nullable)",
  "username": "string (for reference)",
  "action": "string (e.g., 'login', 'create_order', 'update_menu')",
  "entityType": "string (e.g., 'user', 'order', 'menu_item')",
  "entityId": "string (UUID, nullable)",
  "oldValues": "object (JSON, previous state)",
  "newValues": "object (JSON, new state)",
  "ipAddress": "string (client IP)",
  "userAgent": "string (client user agent)",
  "success": "boolean",
  "errorMessage": "string (if success = false)",
  "metadata": "object (additional context)",
  "timestamp": "string (ISO timestamp)"
}
```

### Security Incident Model
```json
{
  "id": "string (UUID)",
  "type": "unauthorized_access|data_breach|system_compromise|suspicious_activity",
  "severity": "low|medium|high|critical",
  "description": "string (required, max 1000 chars)",
  "userId": "string (UUID, optional)",
  "ipAddress": "string (optional)",
  "userAgent": "string (optional)",
  "affectedData": "object (optional, what data was involved)",
  "actionsTaken": "string (optional, response actions)",
  "resolved": "boolean (default false)",
  "resolvedBy": "string (UUID, optional)",
  "resolvedAt": "string (ISO timestamp, optional)",
  "timestamp": "string (ISO timestamp)"
}
```

## 8. Error Response Models

### Standard Error Response
```json
{
  "data": {},
  "errors": [
    "string (human-readable error message)"
  ]
}
```

### Validation Error Response
```json
{
  "data": {},
  "errors": [
    "Username is required",
    "Email must be a valid email address",
    "Price must be a positive number"
  ],
  "validationErrors": {
    "username": ["Username is required", "Username must be 3-50 characters"],
    "email": ["Email must be a valid email address"],
    "price": ["Price must be a positive number"]
  }
}
```

### Authentication Error Response
```json
{
  "data": {},
  "errors": ["Invalid credentials"],
  "errorCode": "INVALID_CREDENTIALS|TOKEN_EXPIRED|ACCOUNT_LOCKED|INSUFFICIENT_PERMISSIONS",
  "lockoutInfo": {
    "attemptsRemaining": "number",
    "lockoutUntil": "string (ISO timestamp, if locked)"
  }
}
```

## 9. Pagination and Filtering Models

### Pagination Parameters
```json
{
  "page": "number (default 1)",
  "limit": "number (default 50, max 1000)",
  "sortBy": "string (field name)",
  "sortOrder": "asc|desc",
  "offset": "number (alternative to page)"
}
```

### Paginated Response
```json
{
  "data": ["array of items"],
  "pagination": {
    "currentPage": "number",
    "totalPages": "number",
    "totalItems": "number",
    "itemsPerPage": "number",
    "hasNextPage": "boolean",
    "hasPreviousPage": "boolean"
  }
}
```

### Filter Parameters (for various endpoints)
```json
{
  "dateFrom": "string (ISO date)",
  "dateTo": "string (ISO date)",
  "status": "string (entity status)",
  "category": "string",
  "searchTerm": "string (for name/text searches)",
  "userId": "string (UUID)",
  "isActive": "boolean"
}
```

## Data Validation Requirements

### Field Validation Rules
1. **Required Field Validation**: All required fields must be present and non-empty
2. **Length Validation**: String fields must meet min/max length requirements
3. **Format Validation**: Email, UUID, timestamp formats must be valid
4. **Range Validation**: Numeric fields must be within specified ranges
5. **Enum Validation**: Enumerated fields must match allowed values
6. **Business Rule Validation**: Custom validation for business logic

### Data Sanitization
1. **Input Trimming**: Remove leading/trailing whitespace from strings
2. **HTML Encoding**: Encode special characters to prevent XSS
3. **SQL Injection Prevention**: Use parameterized queries
4. **Case Normalization**: Normalize email addresses and usernames to lowercase

### Response Data Requirements
1. **Consistent Structure**: All responses follow the same format pattern
2. **Null Handling**: Explicit null values for optional fields that are not set
3. **Date Formatting**: All timestamps in ISO 8601 format with UTC timezone
4. **Number Precision**: Currency values always with 2 decimal places
5. **Boolean Values**: Always true/false, never truthy/falsy values