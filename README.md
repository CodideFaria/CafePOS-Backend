# CafePOS Backend

A robust Python-based backend service for the CafePOS Point of Sale system, built with Tornado web framework and PostgreSQL database.

## 🚀 Features

- **RESTful API** with comprehensive endpoints for POS operations
- **JWT Authentication** with role-based access control (RBAC)
- **Real-time Dashboard** with sales analytics and reporting
- **Inventory Management** with automated stock alerts
- **Menu Management** with image upload and bulk CSV import
- **Order Processing** with receipt generation and refund handling
- **User Management** with role assignments and permissions
- **Email Services** for daily reports and password reset
- **Comprehensive Testing** with pytest and asyncio support
- **Docker Support** for containerized deployment

## 🛠 Tech Stack

- **Framework:** Python 3.13 with Tornado Web Server
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Authentication:** JWT with bcrypt password hashing
- **Testing:** pytest with async support
- **Image Processing:** Pillow for thumbnails and uploads
- **Email:** SMTP integration for notifications
- **Deployment:** Docker and Docker Compose

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Docker and Docker Compose (for containerized setup)

## 🔧 Installation

### Option 1: Docker Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd CafePOS/CafePOS-Backend
   ```

2. **Create environment file:**
   Create a `.env` file in the root directory with the following configuration:
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://cafepos_user:your_secure_password@db:5432/cafepos_db
   POSTGRES_DB=cafepos_db
   POSTGRES_USER=cafepos_user
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   
   # JWT Configuration
   JWT_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
   
   # Email Configuration (Optional - for password reset and daily reports)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@example.com
   SMTP_PASSWORD=your_email_app_password
   
   # Application Configuration
   DEBUG=false
   CORS_ORIGINS=http://localhost:3000
   ```

3. **Start the services:**
   ```bash
   # Start database and backend services
   docker-compose up -d
   
   # Check that services are running
   docker-compose ps
   ```

4. **Seed the database with demo data:**
   ```bash
   # Option A: Use test data seeder (comprehensive demo data)
   docker-compose exec backend python seed_test_data.py
   
   # Option B: Use production data seeder (real menu items)
   docker-compose exec backend python seed_production_data.py
   ```

### Option 2: Local Development Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database:**
   ```bash
   # Create database user and database
   sudo -u postgres psql
   CREATE USER cafepos_user WITH PASSWORD 'your_password';
   CREATE DATABASE cafepos_db OWNER cafepos_user;
   GRANT ALL PRIVILEGES ON DATABASE cafepos_db TO cafepos_user;
   \q
   ```

3. **Create environment variables:**
   Create a `.env` file or set environment variables:
   ```bash
   export DATABASE_URL=postgresql://cafepos_user:your_password@localhost:5432/cafepos_db
   ```

4. **Initialize the database:**
   ```bash
   python orm/db_init.py
   ```

5. **Seed with demo data:**
   ```bash
   python seed_test_data.py
   ```

6. **Start the development server:**
   ```bash
   python main.py
   ```

The backend server will be available at `http://localhost:8880`

## 🗄️ Database Schema

The application uses a comprehensive database schema with the following main entities:

- **Users & Roles:** Role-based access control system
- **Menu Items:** Product catalog with categories, pricing, and images
- **Orders & Order Items:** Transaction processing and history
- **Inventory:** Stock management with automated alerts and locations
- **Stock Movements:** Inventory tracking and audit trail
- **Alerts:** System notifications and low-stock warnings
- **Email Tokens:** Password reset functionality

## 📊 Data Seeding

### Test Data Seeder (`seed_test_data.py`)
Provides comprehensive demo data for development and testing:
- **45+ Menu Items:** Coffee, tea, pastries, food with realistic pricing
- **4 Users:** Admin, Manager, Cashier, Trainee with different access levels
- **20+ Inventory Items:** Coffee beans, dairy, syrups, supplies with stock levels
- **Low Stock Items:** For testing alert functionality

**Usage:**
```bash
# Docker environment
docker-compose exec backend python seed_test_data.py

# Local environment
python seed_test_data.py
```

### Production Data Seeder (`seed_production_data.py`)
Real menu items with EUR pricing and image URLs:
- **44+ Menu Items:** Actual cafe menu with professional descriptions
- **32+ Inventory Items:** Real ingredients and supplies with EUR pricing
- **Image URLs:** Pre-configured paths for menu item images
- **EUR Conversion:** Automated USD to EUR price conversion

**Usage:**
```bash
# Docker environment
docker-compose exec backend python seed_production_data.py

# Local environment
python seed_production_data.py
```

**Test Login Credentials:**
- **Admin:** username=`admin`, password=`password123`, pin=`1234`
- **Manager:** username=`manager`, password=`password123`, pin=`2345`
- **Cashier:** username=`cashier` (or `cashier1`), password=`password123`, pin=`3456`
- **Trainee:** username=`trainee`, password=`password123`, pin=`4567`

## 🔌 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/password-reset-request` - Request password reset
- `POST /auth/password-reset-confirm` - Confirm password reset

### Menu Management
- `GET /menu_items` - List all menu items
- `POST /menu_items` - Create new menu item
- `PUT /menu_items/{id}` - Update menu item
- `DELETE /menu_items/{id}` - Delete menu item
- `POST /menu_items/bulk-import` - Bulk import from CSV

### Orders
- `GET /orders` - List orders
- `POST /orders` - Create new order
- `GET /orders/{id}` - Get order details
- `POST /orders/{id}/refund` - Process refund

### Inventory
- `GET /inventory` - List inventory items
- `POST /inventory/{id}/adjust` - Adjust stock levels
- `GET /inventory/export` - Export inventory to CSV

### Reports & Analytics
- `GET /reports/dashboard` - Sales dashboard data
- `GET /reports/daily-sales` - Daily sales report
- `POST /reports/email-summary` - Send daily email summary

## 🧪 Testing

Run the comprehensive test suite:

**Available Tests:**
- `test_main.py` - Main application and routing tests
- `test_menu_items.py` - Menu management functionality
- `test_inventory.py` - Inventory and stock management
- `test_users.py` - User management and authentication
- `test_roles.py` - Role-based access control
- `test_orders.py` - Order processing and management
- `test_daily_email.py` - Email reporting functionality
- `test_email_with_sample_data.py` - Email integration tests

**Running Tests:**

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_menu_items.py -v

# Run tests with detailed output
pytest -v -s

# Run in Docker environment
docker-compose up tester

# Run specific test in Docker
docker-compose exec backend pytest tests/test_menu_items.py -v
```

**Test Configuration:**
- Uses `pytest.ini` with `asyncio_mode = auto` for async test support
- Isolated test database to prevent data contamination
- Comprehensive fixtures for test data setup

## 🔐 Security Features

- **JWT Authentication** with access and refresh tokens
- **Role-Based Access Control** (Admin, Manager, Cashier, Trainee)
- **Password Hashing** using bcrypt
- **Account Lockout** after failed login attempts
- **SQL Injection Prevention** through SQLAlchemy ORM
- **CORS Configuration** for frontend integration

## 📊 Monitoring & Health Checks

- **Health Endpoint:** `GET /health` - Service health status
- **Logging:** Comprehensive logging throughout the application
- **Docker Health Checks:** Automated container health monitoring

## 🚀 Deployment

### Quick Start (Development)

```bash
# Clone the repository
git clone <repository-url>
cd CafePOS/CafePOS-Backend

# Create .env file (see Installation section for full configuration)
cat > .env << 'EOF'
DATABASE_URL=postgresql://cafepos_user:password123@db:5432/cafepos_db
POSTGRES_DB=cafepos_db
POSTGRES_USER=cafepos_user
POSTGRES_PASSWORD=password123
JWT_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
EOF

# Start services
docker-compose up -d

# Wait for services to start, then seed data
sleep 10
docker-compose exec backend python seed_test_data.py

# Your backend is now running at http://localhost:8880
```

### Production Deployment

1. **Prepare production environment:**
   ```bash
   # Create production .env file with secure values
   cat > .env << 'EOF'
   DATABASE_URL=postgresql://cafepos_user:SECURE_PASSWORD@db:5432/cafepos_db
   POSTGRES_DB=cafepos_db
   POSTGRES_USER=cafepos_user
   POSTGRES_PASSWORD=SECURE_PASSWORD
   JWT_SECRET=your-production-jwt-secret-at-least-32-characters-long
   DEBUG=false
   CORS_ORIGINS=https://yourfrontend.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@company.com
   SMTP_PASSWORD=your_app_password
   EOF
   ```

2. **Deploy with Docker:**
   ```bash
   # Build and start production containers
   docker-compose up -d --build
   
   # Verify services are running
   docker-compose ps
   docker-compose logs backend
   ```

3. **Initialize production database:**
   ```bash
   # Database tables are auto-created on startup
   # Seed with production data
   docker-compose exec backend python seed_production_data.py
   ```

4. **Health check:**
   ```bash
   curl http://localhost:8880/health
   ```

## 📝 Development

### Project Structure
```
CafePOS-Backend/
├── apis/                    # API handlers and endpoints
│   ├── auth_api.py         # Authentication endpoints
│   ├── menu_api.py         # Menu management
│   ├── inventory_api.py    # Inventory management
│   ├── orders_api.py       # Order processing
│   ├── users_api.py        # User management
│   ├── reports_api.py      # Analytics and reporting
│   ├── upload_api.py       # Image upload handling
│   └── ...                 # Other API modules
├── orm/                     # Database layer
│   ├── models/             # SQLAlchemy models
│   │   ├── model_users.py  # User model
│   │   ├── model_menu.py   # Menu item model
│   │   └── ...             # Other models
│   ├── controllers/        # Database controllers
│   ├── base.py            # Base SQLAlchemy setup
│   └── db_init.py         # Database initialization
├── services/               # Business logic services
├── tests/                  # Comprehensive test suite
├── uploads/               # File uploads and images
│   ├── menu_items/        # Menu item images
│   └── thumbnails/        # Generated thumbnails
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Container definition
├── seed_test_data.py     # Test data seeder
├── seed_production_data.py # Production data seeder
└── pytest.ini           # Test configuration
```

### Adding New Features

1. **Create API Handler:** Add new endpoint in `apis/` directory
2. **Database Model:** Define models in `orm/models/`
3. **Controller Logic:** Implement in `orm/controllers/`
4. **Register Routes:** Update route mapping in `main.py`
5. **Write Tests:** Add tests in `tests/` directory

### Port Configuration

- **Backend API:** Port `8880` (http://localhost:8880)
- **PostgreSQL:** Port `5432` (internal Docker network + host access)
- **Frontend Integration:** Backend expects frontend at `http://localhost:3000`

## 🛠️ Troubleshooting

### Common Issues

**1. Docker Container Won't Start**
```bash
# Check container logs
docker-compose logs backend
docker-compose logs db

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

**2. Database Connection Issues**
```bash
# Test database connection
docker-compose exec backend python -c "from orm.db_init import engine; print('DB Connected!' if engine else 'Failed')"

# Reset database
docker-compose down -v
docker-compose up -d
```

**3. Seeder Script Fails**
```bash
# Check if database is initialized
docker-compose exec backend python -c "from orm.db_init import Base, engine; print('Tables exist'); Base.metadata.create_all(engine)"

# Run seeder with verbose output
docker-compose exec backend python seed_test_data.py
```

**4. Permission Issues with Uploads**
```bash
# Fix upload directory permissions
docker-compose exec backend chmod -R 755 uploads/
mkdir -p uploads/menu_items uploads/thumbnails
```

**5. Port Already in Use**
```bash
# Check what's using the port
lsof -i :8880
netstat -tulpn | grep :8880

# Kill process or change port in docker-compose.yml
```

**6. Environment Variables Not Loading**
```bash
# Verify .env file exists and has correct format
ls -la .env
cat .env

# Check if variables are loaded in container
docker-compose exec backend printenv | grep POSTGRES
```

### Development Tips

- **Hot Reload:** Code changes require container restart: `docker-compose restart backend`
- **Database Reset:** `docker-compose down -v && docker-compose up -d` 
- **View Logs:** `docker-compose logs -f backend`
- **Container Shell:** `docker-compose exec backend bash`
- **Manual Testing:** Use curl or Postman with base URL `http://localhost:8880`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📦 Dependencies

**Core Dependencies:**
- `tornado` - Web framework for handling HTTP requests
- `psycopg2-binary` - PostgreSQL adapter for Python
- `sqlalchemy` - Python SQL toolkit and ORM
- `python-decouple` - Configuration management
- `pyjwt` - JWT token handling
- `bcrypt` - Password hashing
- `pillow` - Image processing for uploads
- `requests` - HTTP library

**Development & Testing:**
- `pytest` - Testing framework
- `pytest-tornado` - Tornado testing support
- `pytest-asyncio` - Async testing support

## 🔄 API Integration

### Frontend Integration
The backend is designed to work with the CafePOS React frontend:
- **Frontend Repository:** `../CafePOS-Frontend/`
- **Expected Frontend URL:** `http://localhost:3000`
- **API Base URL:** `http://localhost:8880`
- **CORS:** Configured to allow frontend requests

### Authentication Flow
1. Login with username/password → Get JWT tokens
2. Use access token for API requests
3. Refresh token when access token expires
4. PIN-based quick authentication for POS operations

### Image Uploads
- **Upload Endpoint:** `POST /upload/image`
- **Serve Endpoint:** `GET /uploads/{filename}`
- **Supported Formats:** JPG, PNG, GIF
- **Auto Thumbnails:** Generated at upload time

## 🌟 Key Features Detail

### Role-Based Access Control (RBAC)
- **Admin:** Full system access, user management, settings
- **Manager:** Reports, inventory, menu management, user oversight
- **Cashier:** POS operations, order management, limited inventory
- **Trainee:** Basic POS operations, view-only access

### Inventory Management
- **Real-time Stock Tracking:** Automatic updates on sales
- **Low Stock Alerts:** Configurable minimum thresholds
- **Stock Movements:** Full audit trail of inventory changes
- **CSV Export/Import:** Bulk operations for inventory data

### Sales Analytics
- **Real-time Dashboard:** Live sales metrics and KPIs
- **Daily Reports:** Automated email summaries
- **Historical Data:** Sales trends and performance analysis
- **Revenue Tracking:** Daily, weekly, monthly comparisons

## 🆘 Support & Documentation

For support and questions:
- **Issues:** Create an issue in the repository
- **API Testing:** Use the health endpoint: `GET /health`
- **Logs:** Check container logs: `docker-compose logs backend`
- **Database:** Access via: `docker-compose exec db psql -U cafepos_user -d cafepos_db`

### Additional Resources
- **Frontend Integration:** Check `../CafePOS-Frontend/README.md`
- **Full Project Documentation:** See `../CLAUDE.md`
- **API Testing:** Import Postman collection (if available)

---

**🎯 CafePOS Backend - Built with ❤️ for efficient Point of Sale operations**

*Ready for production deployment with comprehensive testing, security features, and scalable architecture.*