# Backend API Requirements for CafePOS Frontend

This document outlines all the API endpoints, request/response formats, and backend requirements needed to support the CafePOS frontend application.

## Base Configuration

- **Base URL**: `http://localhost:8880`
- **Authentication**: Bearer token in Authorization header (`Authorization: Bearer {token}`)
- **Content Type**: `application/json`
- **Error Response Format**: `{data: {}, errors: [string]}`

## 1. Menu Management APIs

### GET /menu_items
Fetch all menu items for display in the POS system.

**Response Format:**
```json
{
  "menu_items": [
    {
      "id": "string",
      "name": "string",
      "size": "string",
      "price": 12.99,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "amount": 150
}
```

### POST /menu_items
Create a new menu item.

**Request Payload:**
```json
{
  "name": "string",
  "size": "string", 
  "price": 12.99
}
```

**Response:** Menu item object with generated ID

### PUT /menu_items/{id}
Update an existing menu item.

**Request Payload:**
```json
{
  "name": "string",
  "size": "string",
  "price": 12.99
}
```

**Response:** Updated menu item object

### DELETE /menu_items/{id}
Soft delete a menu item (set is_active to false).

**Response:** Success confirmation

## 2. Authentication & User Management APIs

### POST /auth/login
Authenticate user with username/password or PIN code.

**Request Payload:**
```json
{
  "username": "string",
  "password": "string",
  "pinCode": "string",
  "rememberMe": false
}
```

**Response:**
```json
{
  "user": {
    "id": "string",
    "username": "string",
    "firstName": "string",
    "lastName": "string", 
    "email": "string",
    "role": "admin|manager|cashier|trainee",
    "permissions": ["menu.view", "sales.process", ...],
    "isActive": true,
    "createdAt": "2024-01-01T00:00:00Z",
    "lastLogin": "2024-01-01T00:00:00Z",
    "pinCode": "1234",
    "shiftStartTime": "2024-01-01T09:00:00Z",
    "shiftEndTime": "2024-01-01T17:00:00Z"
  },
  "token": "jwt_token_string",
  "sessionExpiry": "2024-01-01T17:00:00Z"
}
```

### POST /auth/logout
Logout current user session.

**Response:** Success confirmation

### GET /auth/me
Get current authenticated user information.

**Response:** User object (same as login response)

### POST /auth/refresh
Refresh authentication token.

**Response:** New token and expiry

## 3. Password Reset APIs

### POST /auth/password-reset-request
Request password reset for email.

**Request Payload:**
```json
{
  "email": "user@example.com"
}
```

**Response:** Success confirmation

### POST /auth/validate-reset-token
Validate password reset token.

**Request Payload:**
```json
{
  "token": "reset_token_string"
}
```

**Response:** Validation result

### POST /auth/password-reset-confirm  
Confirm password reset with new password.

**Request Payload:**
```json
{
  "token": "reset_token_string",
  "newPassword": "new_password"
}
```

**Response:** Success confirmation

## 4. User Management APIs

### GET /users
Get all users (admin/manager only).

**Response:**
```json
{
  "users": [
    {
      "id": "string",
      "username": "string",
      "firstName": "string",
      "lastName": "string",
      "email": "string", 
      "role": "admin|manager|cashier|trainee",
      "permissions": ["permission1", "permission2"],
      "isActive": true,
      "createdAt": "2024-01-01T00:00:00Z",
      "lastLogin": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### GET /users/{userId}
Get specific user details.

**Response:** User object

### POST /users
Create new user.

**Request Payload:**
```json
{
  "username": "string",
  "firstName": "string", 
  "lastName": "string",
  "email": "string",
  "role": "admin|manager|cashier|trainee",
  "password": "string",
  "pinCode": "1234"
}
```

### PUT /users/{userId}
Update user information.

**Request Payload:** User data to update

### PUT /users/{userId}/role
Update user role.

**Request Payload:**
```json
{
  "role": "admin|manager|cashier|trainee"
}
```

### PUT /users/{userId}/permissions
Update user permissions.

**Request Payload:**
```json
{
  "permissions": ["menu.view", "sales.process", ...]
}
```

### PATCH /users/{userId}/activate
Activate user account.

### PATCH /users/{userId}/deactivate  
Deactivate user account.

## 5. Role & Permission APIs

### GET /roles
Get all available roles.

**Response:**
```json
{
  "roles": [
    {
      "id": "string",
      "name": "admin|manager|cashier|trainee", 
      "description": "string",
      "permissions": ["permission1", "permission2"]
    }
  ]
}
```

### GET /permissions
Get all available permissions.

**Response:**
```json
{
  "permissions": [
    {
      "id": "menu.view",
      "name": "View Menu",
      "category": "Menu Management",
      "description": "Can view menu items"
    }
  ]
}
```

### GET /permissions/role/{role}
Get permissions for specific role.

**Response:** Array of permissions

## 6. Order & Sales APIs

### POST /orders
Create new order/sale.

**Request Payload:**
```json
{
  "items": [
    {
      "id": "string",
      "product": {
        "id": "string",
        "name": "string", 
        "size": "string",
        "price": 12.99
      },
      "quantity": 2,
      "notes": "Extra hot"
    }
  ],
  "discount": {
    "type": "percentage|fixed",
    "value": 10,
    "reason": "Employee discount",
    "staffId": "string"
  },
  "paymentMethod": "cash|card",
  "cashReceived": 25.00,
  "staffId": "string"
}
```

**Response:**
```json
{
  "order": {
    "id": "string",
    "items": [...],
    "discount": {...},
    "subtotal": 24.98,
    "discountAmount": 2.50,
    "tax": 1.80,
    "total": 24.28,
    "paymentMethod": "cash",
    "cashReceived": 25.00, 
    "change": 0.72,
    "timestamp": "2024-01-01T10:30:00Z",
    "staffId": "string",
    "status": "completed",
    "reprintCount": 0
  }
}
```

### GET /orders
Get order history with filters.

**Query Parameters:**
- `startDate`: ISO date string
- `endDate`: ISO date string  
- `staffId`: Filter by staff member
- `status`: Filter by order status
- `limit`: Number of records
- `offset`: Pagination offset

**Response:** Array of order objects

### GET /orders/{orderId}
Get specific order details.

**Response:** Order object

### POST /orders/{orderId}/refund
Process order refund.

**Request Payload:**
```json
{
  "reason": "Customer request",
  "staffId": "string"
}
```

### POST /orders/{orderId}/reprint
Reprint order receipt.

**Response:** Receipt data

## 7. Inventory Management APIs

### GET /inventory
Get all inventory items.

**Response:**
```json
{
  "inventory": [
    {
      "id": "string",
      "name": "string",
      "category": "string",
      "currentStock": 50,
      "minStockLevel": 10,
      "maxStockLevel": 100,
      "unit": "kg",
      "costPerUnit": 5.99,
      "supplier": "ABC Supplies",
      "lastRestocked": "2024-01-01T00:00:00Z",
      "expiryDate": "2024-06-01T00:00:00Z",
      "barcode": "1234567890123",
      "description": "Premium coffee beans",
      "location": "Storage Room A",
      "status": "in_stock|low_stock|out_of_stock|expired"
    }
  ]
}
```

### POST /inventory
Add new inventory item.

### PUT /inventory/{id}
Update inventory item.

### POST /inventory/{id}/adjust-stock
Adjust inventory stock levels.

**Request Payload:**
```json
{
  "type": "restock|usage|waste|adjustment",
  "quantity": 20,
  "reason": "Weekly restock",
  "staffId": "string",
  "cost": 119.80,
  "supplier": "ABC Supplies",
  "notes": "Delivered on schedule"
}
```

### GET /inventory/alerts
Get stock alerts.

**Response:**
```json
{
  "alerts": [
    {
      "id": "string",
      "inventoryItemId": "string",
      "type": "low_stock|out_of_stock|expiring_soon|expired",
      "message": "Coffee beans running low (5 kg remaining)",
      "severity": "low|medium|high|critical",
      "createdAt": "2024-01-01T00:00:00Z",
      "acknowledged": false
    }
  ]
}
```

### POST /inventory/alerts/{id}/acknowledge
Acknowledge stock alert.

## 8. Dashboard & Analytics APIs

### GET /analytics/sales
Get sales analytics data.

**Query Parameters:**
- `period`: "today|week|month|quarter|year|custom"
- `startDate`: For custom period
- `endDate`: For custom period
- `category`: Filter by product category

**Response:**
```json
{
  "metrics": {
    "totalRevenue": 15420.50,
    "dailyRevenue": 890.25,
    "weeklyRevenue": 6234.75,
    "monthlyRevenue": 15420.50,
    "totalTransactions": 456,
    "dailyTransactions": 45,
    "averageOrderValue": 33.82,
    "totalCustomers": 234,
    "returningCustomers": 89,
    "newCustomers": 145
  },
  "chartData": [
    {
      "date": "2024-01-01",
      "revenue": 890.25,
      "transactions": 45,
      "averageOrderValue": 19.78
    }
  ],
  "topProducts": [
    {
      "id": "string",
      "name": "Cappuccino Large",
      "category": "Coffee",
      "quantitySold": 89,
      "revenue": 623.11,
      "profitMargin": 68.5
    }
  ],
  "categoryBreakdown": [
    {
      "category": "Coffee",
      "revenue": 8934.25,
      "percentage": 57.9,
      "transactions": 234,
      "averageOrderValue": 38.16,
      "color": "#8B4513"
    }
  ],
  "hourlyBreakdown": [
    {
      "hour": 9,
      "revenue": 234.50,
      "transactions": 12,
      "label": "9:00 AM"
    }
  ]
}
```

### GET /analytics/inventory-stats
Get inventory statistics.

**Response:**
```json
{
  "stats": {
    "totalItems": 156,
    "lowStockItems": 12,
    "outOfStockItems": 3,
    "expiringItems": 7,
    "totalValue": 12456.78,
    "lastUpdated": "2024-01-01T10:30:00Z"
  }
}
```

## 9. Security & Audit APIs

### GET /audit/access-log
Get user access logs.

**Response:**
```json
{
  "logs": [
    {
      "id": "string", 
      "userId": "string",
      "username": "string",
      "action": "login|logout|menu_access|sale|refund",
      "timestamp": "2024-01-01T10:30:00Z",
      "ipAddress": "192.168.1.100",
      "userAgent": "Mozilla/5.0...",
      "success": true
    }
  ]
}
```

### GET /audit/failed-logins
Get failed login attempts.

### POST /security/incident
Report security incident.

**Request Payload:**
```json
{
  "type": "unauthorized_access|data_breach|system_compromise",
  "description": "Multiple failed login attempts",
  "severity": "low|medium|high|critical",
  "userId": "string",
  "timestamp": "2024-01-01T10:30:00Z"
}
```

## 10. File Upload APIs

### POST /upload/menu-items
Bulk import menu items from CSV.

**Request:** FormData with CSV file
**Response:** Import results and errors

### GET /export/sales
Export sales data to CSV/Excel.

**Query Parameters:**
- `format`: "csv|excel"
- `startDate`: ISO date
- `endDate`: ISO date
- `includeDetails`: boolean

**Response:** File download

### GET /export/inventory
Export inventory data.

**Response:** File download

## Error Handling

All API endpoints should return errors in this format:

```json
{
  "data": {},
  "errors": [
    "Error message 1",
    "Error message 2"
  ]
}
```

### Common HTTP Status Codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized  
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

### Authentication Errors:
- Invalid credentials
- Token expired
- Account locked (after failed attempts)
- Insufficient permissions

### Validation Errors:
- Missing required fields
- Invalid data types
- Business rule violations
- Duplicate entries

## Rate Limiting & Security

- Implement rate limiting (e.g., 100 requests per minute per IP)
- Use secure password hashing (bcrypt, scrypt, or Argon2)
- Implement JWT token expiration and refresh
- Log all authentication attempts and administrative actions
- Validate all input data and sanitize outputs
- Use HTTPS in production
- Implement CORS policies appropriately