# Backend Database Schema Requirements for CafePOS

This document outlines the complete database schema, table structures, relationships, and constraints needed to support the CafePOS frontend application.

## Database Design Overview

**Database Type**: Relational Database (PostgreSQL, MySQL, or SQLite recommended)
**Schema Name**: `cafepos`
**Character Set**: UTF-8
**Timezone**: UTC (convert to local timezone in application layer)

## 1. Users Table

Stores user accounts and authentication information.

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,  -- UUID
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    pin_code VARCHAR(60), -- Hashed 4-digit PIN
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role ENUM('admin', 'manager', 'cashier', 'trainee') NOT NULL DEFAULT 'cashier',
    is_active BOOLEAN DEFAULT TRUE,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP NULL,
    last_login TIMESTAMP NULL,
    shift_start_time TIMESTAMP NULL,
    shift_end_time TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
);
```

## 2. Roles Table

Defines available roles and their descriptions.

```sql
CREATE TABLE roles (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE, -- Cannot be deleted
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Default roles
INSERT INTO roles (id, name, description, is_system_role) VALUES
('admin-role-id', 'admin', 'Full system access', TRUE),
('manager-role-id', 'manager', 'Management level access', TRUE),
('cashier-role-id', 'cashier', 'Standard POS operations', TRUE),
('trainee-role-id', 'trainee', 'Limited training access', TRUE);
```

## 3. Permissions Table

Defines all available system permissions.

```sql
CREATE TABLE permissions (
    id VARCHAR(50) PRIMARY KEY, -- e.g., 'menu.view'
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert all permissions
INSERT INTO permissions (id, name, category, description) VALUES
-- Menu Management
('menu.view', 'View Menu', 'Menu Management', 'Can view menu items'),
('menu.create', 'Create Menu Items', 'Menu Management', 'Can create new menu items'),
('menu.edit', 'Edit Menu Items', 'Menu Management', 'Can modify existing menu items'),
('menu.delete', 'Delete Menu Items', 'Menu Management', 'Can remove menu items'),
('menu.import', 'Import Menu', 'Menu Management', 'Can bulk import menu items'),

-- Inventory Management  
('inventory.view', 'View Inventory', 'Inventory Management', 'Can view inventory items'),
('inventory.edit', 'Edit Inventory', 'Inventory Management', 'Can modify inventory items'),
('inventory.adjust_stock', 'Adjust Stock', 'Inventory Management', 'Can adjust stock levels'),
('inventory.export', 'Export Inventory', 'Inventory Management', 'Can export inventory data'),
('inventory.view_costs', 'View Costs', 'Inventory Management', 'Can view cost information'),

-- Sales & Orders
('sales.process', 'Process Sales', 'Sales & Orders', 'Can process sales transactions'),
('sales.refund', 'Process Refunds', 'Sales & Orders', 'Can process refunds'),
('sales.view_history', 'View Sales History', 'Sales & Orders', 'Can view order history'),
('sales.apply_discount', 'Apply Discounts', 'Sales & Orders', 'Can apply discounts'),
('sales.override_price', 'Override Prices', 'Sales & Orders', 'Can override item prices'),

-- Receipts
('receipts.print', 'Print Receipts', 'Receipts', 'Can print receipts'),
('receipts.reprint', 'Reprint Receipts', 'Receipts', 'Can reprint old receipts'),
('receipts.email', 'Email Receipts', 'Receipts', 'Can email receipts to customers'),

-- Reporting
('reports.view', 'View Reports', 'Reporting', 'Can view sales reports'),
('reports.export', 'Export Reports', 'Reporting', 'Can export report data'),
('reports.financial', 'Financial Reports', 'Reporting', 'Can view financial reports'),

-- User Management
('users.view', 'View Users', 'User Management', 'Can view user accounts'),
('users.create', 'Create Users', 'User Management', 'Can create new user accounts'),
('users.edit', 'Edit Users', 'User Management', 'Can modify user accounts'),
('users.delete', 'Delete Users', 'User Management', 'Can delete user accounts'),
('users.reset_password', 'Reset Passwords', 'User Management', 'Can reset user passwords'),

-- System Administration
('system.settings', 'System Settings', 'System Administration', 'Can modify system settings'),
('system.backup', 'System Backup', 'System Administration', 'Can perform system backups'),
('system.logs', 'System Logs', 'System Administration', 'Can view system logs'),
('system.maintenance', 'System Maintenance', 'System Administration', 'Can perform maintenance tasks');
```

## 4. Role Permissions Table

Links roles to their permissions.

```sql
CREATE TABLE role_permissions (
    role_id VARCHAR(36) NOT NULL,
    permission_id VARCHAR(50) NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by VARCHAR(36),
    
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL
);
```

## 5. User Permissions Table

Additional permissions assigned directly to users (overrides).

```sql
CREATE TABLE user_permissions (
    user_id VARCHAR(36) NOT NULL,
    permission_id VARCHAR(50) NOT NULL,
    granted BOOLEAN DEFAULT TRUE, -- TRUE = grant, FALSE = revoke
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by VARCHAR(36),
    
    PRIMARY KEY (user_id, permission_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL
);
```

## 6. Menu Items Table

Stores all menu items available for sale.

```sql
CREATE TABLE menu_items (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    size VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50) DEFAULT 'General',
    description TEXT,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active),
    INDEX idx_price (price)
);
```

## 7. Orders Table

Stores completed sales transactions.

```sql
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL, -- Human-readable order number
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash', 'card') NOT NULL,
    cash_received DECIMAL(10,2) DEFAULT 0,
    change_amount DECIMAL(10,2) DEFAULT 0,
    status ENUM('completed', 'refunded', 'voided') DEFAULT 'completed',
    staff_id VARCHAR(36) NOT NULL,
    customer_name VARCHAR(100),
    customer_email VARCHAR(255),
    notes TEXT,
    reprint_count INT DEFAULT 0,
    last_reprint TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (staff_id) REFERENCES users(id),
    INDEX idx_order_number (order_number),
    INDEX idx_status (status),
    INDEX idx_staff_id (staff_id),
    INDEX idx_created_at (created_at),
    INDEX idx_payment_method (payment_method)
);
```

## 8. Order Items Table

Stores individual items within each order.

```sql
CREATE TABLE order_items (
    id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    menu_item_id VARCHAR(36) NOT NULL,
    menu_item_name VARCHAR(100) NOT NULL, -- Snapshot at time of sale
    menu_item_size VARCHAR(50) NOT NULL,  -- Snapshot at time of sale
    unit_price DECIMAL(10,2) NOT NULL,    -- Price at time of sale
    quantity INT NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,    -- unit_price * quantity
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id),
    INDEX idx_order_id (order_id),
    INDEX idx_menu_item_id (menu_item_id)
);
```

## 9. Order Discounts Table

Stores discount information applied to orders.

```sql
CREATE TABLE order_discounts (
    id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    type ENUM('percentage', 'fixed') NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    staff_id VARCHAR(36) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES users(id),
    INDEX idx_order_id (order_id)
);
```

## 10. Inventory Items Table

Stores inventory items and stock levels.

```sql
CREATE TABLE inventory_items (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    current_stock DECIMAL(10,3) NOT NULL DEFAULT 0,
    min_stock_level DECIMAL(10,3) NOT NULL DEFAULT 0,
    max_stock_level DECIMAL(10,3) NOT NULL DEFAULT 100,
    unit VARCHAR(20) NOT NULL, -- kg, liters, pieces, boxes, etc.
    cost_per_unit DECIMAL(10,4) NOT NULL DEFAULT 0,
    supplier VARCHAR(100),
    last_restocked TIMESTAMP NULL,
    expiry_date TIMESTAMP NULL,
    barcode VARCHAR(50),
    description TEXT,
    location VARCHAR(100),
    status ENUM('in_stock', 'low_stock', 'out_of_stock', 'expired') GENERATED ALWAYS AS (
        CASE 
            WHEN expiry_date IS NOT NULL AND expiry_date < NOW() THEN 'expired'
            WHEN current_stock <= 0 THEN 'out_of_stock'
            WHEN current_stock <= min_stock_level THEN 'low_stock'
            ELSE 'in_stock'
        END
    ) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_status (status),
    INDEX idx_barcode (barcode),
    INDEX idx_supplier (supplier)
);
```

## 11. Stock Movements Table

Tracks all inventory stock changes.

```sql
CREATE TABLE stock_movements (
    id VARCHAR(36) PRIMARY KEY,
    inventory_item_id VARCHAR(36) NOT NULL,
    type ENUM('restock', 'usage', 'waste', 'adjustment') NOT NULL,
    quantity DECIMAL(10,3) NOT NULL, -- positive for add, negative for remove
    previous_stock DECIMAL(10,3) NOT NULL,
    new_stock DECIMAL(10,3) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    staff_id VARCHAR(36) NOT NULL,
    cost DECIMAL(10,2),
    supplier VARCHAR(100),
    reference_order_id VARCHAR(36), -- If movement relates to an order
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES users(id),
    FOREIGN KEY (reference_order_id) REFERENCES orders(id) ON DELETE SET NULL,
    INDEX idx_inventory_item_id (inventory_item_id),
    INDEX idx_type (type),
    INDEX idx_staff_id (staff_id),
    INDEX idx_created_at (created_at)
);
```

## 12. Stock Alerts Table

Stores inventory alerts and notifications.

```sql
CREATE TABLE stock_alerts (
    id VARCHAR(36) PRIMARY KEY,
    inventory_item_id VARCHAR(36) NOT NULL,
    type ENUM('low_stock', 'out_of_stock', 'expiring_soon', 'expired') NOT NULL,
    message TEXT NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(36),
    acknowledged_at TIMESTAMP NULL,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by VARCHAR(36),
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE,
    FOREIGN KEY (acknowledged_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_inventory_item_id (inventory_item_id),
    INDEX idx_type (type),
    INDEX idx_severity (severity),
    INDEX idx_acknowledged (acknowledged),
    INDEX idx_resolved (resolved)
);
```

## 13. User Sessions Table

Tracks active user sessions and authentication tokens.

```sql
CREATE TABLE user_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    device_info TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash),
    INDEX idx_is_active (is_active),
    INDEX idx_expires_at (expires_at)
);
```

## 14. Audit Log Table

Logs all important system activities.

```sql
CREATE TABLE audit_log (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    username VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- 'user', 'menu_item', 'order', etc.
    entity_id VARCHAR(36),
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_entity_type (entity_type),
    INDEX idx_entity_id (entity_id),
    INDEX idx_created_at (created_at),
    INDEX idx_success (success)
);
```

## 15. Password Reset Tokens Table

Manages password reset tokens.

```sql
CREATE TABLE password_reset_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash),
    INDEX idx_expires_at (expires_at),
    INDEX idx_used (used)
);
```

## 16. System Settings Table

Stores system configuration settings.

```sql
CREATE TABLE system_settings (
    id VARCHAR(36) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    value_text TEXT,
    value_number DECIMAL(15,4),
    value_boolean BOOLEAN,
    value_json JSON,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE, -- Can be exposed to frontend
    updated_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_category_key (category, key_name),
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_category (category),
    INDEX idx_is_public (is_public)
);

-- Default system settings
INSERT INTO system_settings (id, category, key_name, value_number, description, is_public) VALUES
(UUID(), 'pos', 'tax_rate', 0.08, 'Default tax rate (8%)', TRUE),
(UUID(), 'pos', 'receipt_timeout_minutes', 5, 'Minutes after which receipts cannot be reprinted', TRUE),
(UUID(), 'security', 'max_failed_attempts', 3, 'Maximum failed login attempts before lockout', FALSE),
(UUID(), 'security', 'lockout_duration_minutes', 15, 'Account lockout duration in minutes', FALSE),
(UUID(), 'security', 'session_timeout_minutes', 480, 'Session timeout in minutes (8 hours)', TRUE),
(UUID(), 'security', 'pin_length', 4, 'Required PIN code length', TRUE);
```

## Database Relationships

### Key Relationships:
1. **Users → Orders**: One-to-Many (staff member processes multiple orders)
2. **Orders → Order Items**: One-to-Many (order contains multiple items)  
3. **Orders → Order Discounts**: One-to-One (order can have one discount)
4. **Menu Items → Order Items**: One-to-Many (menu item appears in multiple orders)
5. **Users → Stock Movements**: One-to-Many (user makes inventory adjustments)
6. **Inventory Items → Stock Movements**: One-to-Many (item has multiple stock changes)
7. **Roles → Role Permissions**: Many-to-Many via junction table
8. **Users → User Permissions**: Many-to-Many for permission overrides

## Triggers and Constraints

### Triggers:
1. **Update inventory on order creation**: Automatically adjust stock when orders are placed
2. **Generate stock alerts**: Create alerts when stock levels change
3. **Log audit trail**: Auto-log all significant data changes
4. **Update user last_login**: Set timestamp on successful authentication

### Constraints:
1. **Price validation**: Prices must be positive
2. **Stock validation**: Stock levels cannot be negative (with exceptions for backorders)
3. **Email format validation**: Ensure valid email formats
4. **Username uniqueness**: Case-insensitive unique usernames
5. **Order totals**: Calculated fields must match sum of components

## Indexes and Performance

### Primary Indexes:
- All primary keys have clustered indexes
- Foreign key columns have non-clustered indexes
- Frequently queried columns (dates, status, active flags) have indexes

### Composite Indexes:
- `(user_id, created_at)` for user activity queries
- `(status, created_at)` for order status queries  
- `(category, is_active)` for menu item filtering
- `(inventory_item_id, created_at)` for stock movement history

## Data Retention and Archival

### Retention Policies:
- **Audit logs**: Keep for 2 years, then archive
- **User sessions**: Auto-cleanup expired sessions daily
- **Password reset tokens**: Auto-cleanup expired tokens hourly
- **Stock alerts**: Archive resolved alerts after 30 days
- **Orders**: Permanent retention for accounting purposes

### Backup Strategy:
- Daily full backups
- Hourly transaction log backups
- Point-in-time recovery capability
- Encrypted backups stored offsite