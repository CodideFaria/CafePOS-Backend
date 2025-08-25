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

- **Framework:** Python 3.x with Tornado Web Server
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
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration:
   ```env
   POSTGRES_DB=cafepos_db
   POSTGRES_USER=cafepos_user
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   JWT_SECRET=your_jwt_secret_key
   SMTP_SERVER=your_smtp_server
   SMTP_PORT=587
   SMTP_USERNAME=your_email
   SMTP_PASSWORD=your_email_password
   ```

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```

4. **Seed the database with demo data:**
   ```bash
   docker-compose up seeder
   ```

### Option 2: Local Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database:**
   - Create a PostgreSQL database
   - Update database connection settings in your environment

3. **Initialize the database:**
   ```bash
   python orm/db_init.py
   ```

4. **Start the development server:**
   ```bash
   python main.py
   ```

The backend server will be available at `http://localhost:8880`

## 🗄️ Database Schema

The application uses a comprehensive database schema with the following main entities:

- **Users & Roles:** Role-based access control system
- **Menu Items:** Product catalog with categories and pricing
- **Orders & Order Items:** Transaction processing and history
- **Inventory:** Stock management with automated alerts
- **Stock Movements:** Inventory tracking and audit trail
- **Alerts:** System notifications and low-stock warnings

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

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_menu_items.py

# Run in Docker
docker-compose up tester
```

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

### Production Deployment

1. **Build and deploy with Docker:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Environment Variables:**
   Ensure all production environment variables are properly configured:
   - Database credentials
   - JWT secrets
   - SMTP configuration
   - CORS settings

3. **Database Migration:**
   ```bash
   docker-compose exec backend python orm/db_init.py
   ```

4. **Seed Production Data:**
   ```bash
   docker-compose exec backend python seed_production_data.py
   ```

## 📝 Development

### Project Structure
```
CafePOS-Backend/
├── apis/              # API handlers and endpoints
├── orm/              # Database models and controllers
│   ├── models/       # SQLAlchemy models
│   └── controllers/  # Database controllers
├── services/         # Business logic services
├── tests/           # Test suite
├── uploads/         # File uploads and images
├── main.py          # Application entry point
├── requirements.txt # Python dependencies
└── docker-compose.yml # Docker configuration
```

### Adding New Features

1. **Create API Handler:** Add new endpoint in `apis/` directory
2. **Database Model:** Define models in `orm/models/`
3. **Controller Logic:** Implement in `orm/controllers/`
4. **Register Routes:** Update route mapping in `main.py`
5. **Write Tests:** Add tests in `tests/` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the [API Documentation](../documentation/API_Documentation.md)
- Review the [troubleshooting guide](../documentation/TROUBLESHOOTING.md)

---

**Built with ❤️ for efficient Point of Sale operations**