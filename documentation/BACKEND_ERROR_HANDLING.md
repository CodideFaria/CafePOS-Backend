# Backend Error Handling Requirements for CafePOS

This document outlines comprehensive error handling, logging, and monitoring requirements that the backend must implement to support the CafePOS frontend application robustly.

## Error Response Standards

### Universal Error Response Format
All API endpoints must return errors in this consistent format:

```json
{
  "data": {},
  "errors": [
    "Human-readable error message 1",
    "Human-readable error message 2"
  ],
  "errorCode": "MACHINE_READABLE_CODE",
  "timestamp": "2024-01-01T10:30:00.000Z",
  "requestId": "uuid-for-tracing",
  "statusCode": 400
}
```

### HTTP Status Code Mapping

| Status Code | Usage | Frontend Handling |
|-------------|-------|------------------|
| `200` | Success | Process data normally |
| `201` | Resource created | Show success message |
| `400` | Bad Request | Show validation errors |
| `401` | Unauthorized | Redirect to login |
| `403` | Forbidden | Show permission error |
| `404` | Not Found | Show resource not found |
| `409` | Conflict | Show conflict resolution options |
| `422` | Validation Error | Show field-specific errors |
| `429` | Rate Limited | Show try again message |
| `500` | Server Error | Show generic error message |
| `503` | Service Unavailable | Show maintenance message |

## 1. Authentication & Authorization Errors

### Authentication Error Codes
```json
{
  "INVALID_CREDENTIALS": {
    "status": 401,
    "message": "Invalid username or password",
    "userMessage": "The username or password you entered is incorrect. Please try again.",
    "action": "SHOW_LOGIN_ERROR"
  },
  "ACCOUNT_LOCKED": {
    "status": 423,
    "message": "Account is temporarily locked due to multiple failed attempts",
    "userMessage": "Your account has been locked for security. Please try again in {minutes} minutes.",
    "action": "SHOW_LOCKOUT_MESSAGE",
    "metadata": {
      "lockoutUntil": "2024-01-01T10:45:00.000Z",
      "attemptsRemaining": 0
    }
  },
  "TOKEN_EXPIRED": {
    "status": 401,
    "message": "Authentication token has expired",
    "userMessage": "Your session has expired. Please log in again.",
    "action": "REDIRECT_TO_LOGIN"
  },
  "TOKEN_INVALID": {
    "status": 401,
    "message": "Authentication token is invalid or malformed",
    "userMessage": "Authentication error. Please log in again.",
    "action": "REDIRECT_TO_LOGIN"
  },
  "INSUFFICIENT_PERMISSIONS": {
    "status": 403,
    "message": "User does not have required permissions for this action",
    "userMessage": "You don't have permission to perform this action.",
    "action": "SHOW_PERMISSION_ERROR",
    "metadata": {
      "requiredPermissions": ["menu.edit"],
      "userPermissions": ["menu.view"]
    }
  }
}
```

### Authorization Error Response Example
```json
{
  "data": {},
  "errors": ["You don't have permission to perform this action."],
  "errorCode": "INSUFFICIENT_PERMISSIONS",
  "timestamp": "2024-01-01T10:30:00.000Z",
  "requestId": "req-uuid-123",
  "statusCode": 403,
  "metadata": {
    "requiredPermissions": ["menu.edit"],
    "userPermissions": ["menu.view", "sales.process"]
  }
}
```

## 2. Validation Errors

### Field-Level Validation Errors
```json
{
  "data": {},
  "errors": [
    "Name is required",
    "Price must be a positive number",
    "Email must be a valid email address"
  ],
  "errorCode": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T10:30:00.000Z",
  "requestId": "req-uuid-123",
  "statusCode": 422,
  "validationErrors": {
    "name": {
      "field": "name",
      "value": "",
      "errors": ["Name is required", "Name must be at least 2 characters"],
      "code": "REQUIRED_FIELD"
    },
    "price": {
      "field": "price",
      "value": -5.00,
      "errors": ["Price must be a positive number"],
      "code": "INVALID_RANGE"
    },
    "email": {
      "field": "email", 
      "value": "invalid-email",
      "errors": ["Email must be a valid email address"],
      "code": "INVALID_FORMAT"
    }
  }
}
```

### Common Validation Error Codes
- `REQUIRED_FIELD`: Field is required but missing
- `INVALID_FORMAT`: Field format is incorrect (email, UUID, etc.)
- `INVALID_RANGE`: Numeric field outside allowed range
- `INVALID_LENGTH`: String field too long or too short
- `INVALID_ENUM`: Field value not in allowed enum values
- `DUPLICATE_VALUE`: Field value already exists (username, email)
- `INVALID_RELATIONSHIP`: Referenced entity doesn't exist
- `BUSINESS_RULE_VIOLATION`: Custom business rule failed

## 3. Business Logic Errors

### Order Processing Errors
```json
{
  "INSUFFICIENT_STOCK": {
    "status": 422,
    "message": "Insufficient inventory for requested items",
    "userMessage": "Some items in your order are out of stock. Please adjust quantities or remove items.",
    "action": "UPDATE_CART",
    "metadata": {
      "unavailableItems": [
        {
          "menuItemId": "item-uuid-123",
          "requestedQuantity": 5,
          "availableStock": 2
        }
      ]
    }
  },
  "INVALID_DISCOUNT": {
    "status": 422,
    "message": "Discount value exceeds maximum allowed",
    "userMessage": "The discount amount is too high. Maximum discount is 50%.",
    "action": "ADJUST_DISCOUNT"
  },
  "PAYMENT_INSUFFICIENT": {
    "status": 422,
    "message": "Cash received is less than total amount",
    "userMessage": "Payment amount is insufficient. Please provide at least ${total}.",
    "action": "UPDATE_PAYMENT",
    "metadata": {
      "totalAmount": 25.50,
      "cashReceived": 20.00,
      "shortfall": 5.50
    }
  }
}
```

### Inventory Management Errors
```json
{
  "NEGATIVE_STOCK": {
    "status": 422,
    "message": "Stock adjustment would result in negative inventory",
    "userMessage": "This adjustment would create negative stock. Current stock: {current}, adjustment: {adjustment}",
    "action": "ADJUST_QUANTITY"
  },
  "EXPIRED_ITEM": {
    "status": 422,
    "message": "Cannot use expired inventory item",
    "userMessage": "This item has expired and cannot be used in orders.",
    "action": "SELECT_DIFFERENT_ITEM"
  }
}
```

## 4. System Errors

### Database Errors
```json
{
  "DATABASE_CONNECTION": {
    "status": 503,
    "message": "Database connection failed",
    "userMessage": "Service temporarily unavailable. Please try again in a few moments.",
    "action": "SHOW_RETRY_MESSAGE",
    "retryAfter": 30
  },
  "DATABASE_TIMEOUT": {
    "status": 504,
    "message": "Database query timeout",
    "userMessage": "Request is taking longer than expected. Please try again.",
    "action": "SHOW_TIMEOUT_MESSAGE"
  },
  "CONSTRAINT_VIOLATION": {
    "status": 409,
    "message": "Database constraint violation",
    "userMessage": "This action conflicts with existing data. Please check and try again.",
    "action": "REFRESH_DATA"
  }
}
```

### External Service Errors
```json
{
  "PAYMENT_GATEWAY_ERROR": {
    "status": 502,
    "message": "Payment gateway is unavailable",
    "userMessage": "Payment processing is temporarily unavailable. Please try cash payment or try again later.",
    "action": "SUGGEST_ALTERNATIVE"
  },
  "EMAIL_SERVICE_ERROR": {
    "status": 502,
    "message": "Email service is unavailable", 
    "userMessage": "Receipt email could not be sent, but your order was successful.",
    "action": "SHOW_WARNING"
  }
}
```

## 5. Rate Limiting Errors

### Rate Limit Response
```json
{
  "data": {},
  "errors": ["Rate limit exceeded. Please try again later."],
  "errorCode": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2024-01-01T10:30:00.000Z",
  "requestId": "req-uuid-123",
  "statusCode": 429,
  "rateLimitInfo": {
    "limit": 100,
    "remaining": 0,
    "resetTime": "2024-01-01T10:31:00.000Z",
    "retryAfter": 60
  }
}
```

## 6. Security Errors

### Security Violation Responses
```json
{
  "SUSPICIOUS_ACTIVITY": {
    "status": 403,
    "message": "Suspicious activity detected",
    "userMessage": "Unusual activity detected on your account. Please contact support if this wasn't you.",
    "action": "LOG_SECURITY_EVENT",
    "metadata": {
      "violationType": "MULTIPLE_FAILED_LOGINS",
      "incidentId": "incident-uuid-123"
    }
  },
  "IP_BLOCKED": {
    "status": 403,
    "message": "IP address has been blocked",
    "userMessage": "Access denied. Please contact support if you believe this is an error.",
    "action": "SHOW_CONTACT_SUPPORT"
  }
}
```

## 7. Error Logging Requirements

### Log Level Standards
- **ERROR**: System errors, exceptions, security violations
- **WARN**: Business rule violations, deprecated API usage, performance issues
- **INFO**: Successful operations, user actions, system events
- **DEBUG**: Detailed execution flow (development/testing only)

### Error Log Format
```json
{
  "timestamp": "2024-01-01T10:30:00.000Z",
  "level": "ERROR",
  "message": "Database connection failed",
  "errorCode": "DATABASE_CONNECTION",
  "requestId": "req-uuid-123",
  "userId": "user-uuid-456",
  "endpoint": "POST /orders",
  "method": "POST",
  "url": "/orders",
  "userAgent": "Mozilla/5.0...",
  "ipAddress": "192.168.1.100",
  "responseTime": 1500,
  "statusCode": 503,
  "stackTrace": "Error: Connection timeout\n    at Database.connect...",
  "metadata": {
    "orderId": "order-uuid-789",
    "customData": "additional context"
  }
}
```

### Required Log Fields
1. **timestamp**: ISO 8601 timestamp with timezone
2. **level**: Log level (ERROR, WARN, INFO, DEBUG)
3. **message**: Human-readable error description
4. **errorCode**: Machine-readable error code
5. **requestId**: Unique request identifier for tracing
6. **userId**: User who triggered the error (if authenticated)
7. **endpoint**: API endpoint that failed
8. **statusCode**: HTTP response status code
9. **responseTime**: Request processing time in milliseconds
10. **stackTrace**: Full stack trace for debugging
11. **metadata**: Additional context data

## 8. Error Monitoring and Alerting

### Critical Error Alerts
Immediate alerts should be sent for:
- Database connection failures
- Authentication system failures
- Payment processing errors
- Security violations
- High error rates (>5% over 5 minutes)
- Memory or disk space issues

### Error Metrics to Track
1. **Error Rate**: Percentage of requests that result in errors
2. **Error Count**: Total number of errors by type
3. **Response Time**: Average response time including failed requests
4. **Availability**: Uptime percentage
5. **Failed Login Rate**: Authentication failure percentage
6. **Security Incidents**: Number and severity of security violations

### Health Check Endpoints
```json
{
  "GET /health": {
    "response": {
      "status": "healthy|degraded|unhealthy",
      "timestamp": "2024-01-01T10:30:00.000Z",
      "version": "1.0.0",
      "uptime": 86400,
      "checks": {
        "database": "healthy",
        "redis": "healthy", 
        "paymentGateway": "degraded",
        "emailService": "healthy"
      }
    }
  }
}
```

## 9. Frontend Error Handling Integration

### Error Display Patterns
1. **Field Validation**: Show errors inline with form fields
2. **Form Validation**: Show summary of all form errors
3. **API Errors**: Show toast notifications or modal dialogs
4. **Network Errors**: Show retry options with backoff
5. **Permission Errors**: Show clear access denied messages

### Error Recovery Actions
```typescript
interface ErrorAction {
  type: 'RETRY' | 'REDIRECT' | 'REFRESH' | 'DISMISS' | 'CONTACT_SUPPORT';
  target?: string; // URL for redirect
  retryAfter?: number; // seconds to wait before retry
  message?: string; // additional instruction
}
```

### Frontend Error Handling Requirements
1. **Graceful Degradation**: App should remain functional during partial failures
2. **Offline Support**: Handle network connectivity issues
3. **Error Persistence**: Remember critical errors across page reloads
4. **User Guidance**: Provide clear next steps for error resolution
5. **Error Reporting**: Allow users to report unexpected errors

## 10. Development and Testing

### Error Testing Requirements
1. **Unit Tests**: Test all error conditions in business logic
2. **Integration Tests**: Test error responses from API endpoints
3. **Load Tests**: Verify error handling under high load
4. **Security Tests**: Test security error responses
5. **Chaos Engineering**: Test system behavior during failures

### Development Error Responses
In development mode, include additional debugging information:
```json
{
  "data": {},
  "errors": ["Database connection failed"],
  "errorCode": "DATABASE_CONNECTION", 
  "statusCode": 503,
  "debug": {
    "stackTrace": "Full stack trace...",
    "query": "SELECT * FROM users WHERE...",
    "parameters": {"id": "user-123"},
    "environment": "development",
    "buildVersion": "1.0.0-dev"
  }
}
```

## Implementation Checklist

### Required Error Handling Features
- [ ] Consistent error response format across all endpoints
- [ ] Proper HTTP status code mapping
- [ ] Field-level validation error details
- [ ] Authentication and authorization error handling
- [ ] Rate limiting with proper headers
- [ ] Security violation detection and logging
- [ ] Database error handling with retry logic
- [ ] External service failure handling
- [ ] Comprehensive error logging
- [ ] Error monitoring and alerting setup
- [ ] Health check endpoints
- [ ] Development debugging features

### Performance Requirements
- [ ] Error responses must be returned within 500ms
- [ ] Log entries must not impact response time
- [ ] Error monitoring overhead < 5% of total CPU
- [ ] Log rotation and archival policies implemented
- [ ] Error rate monitoring with configurable thresholds

### Security Requirements
- [ ] Never expose sensitive data in error messages
- [ ] Log security violations without revealing system details
- [ ] Sanitize all error messages for XSS prevention
- [ ] Rate limit error-prone endpoints
- [ ] Monitor for error-based attacks (SQL injection, etc.)
- [ ] Encrypt error logs containing sensitive information