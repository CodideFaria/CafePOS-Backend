import uuid
import bcrypt
from datetime import datetime, timezone, timedelta
from sqlalchemy import and_, or_

from orm.db_init import session_scope
from orm.models.model_users import User, UserRole
from orm.models.model_permissions import Permission
from orm.models.model_role_permissions import RolePermission
from orm.models.model_user_permissions import UserPermission


class UserController:
    def create_user(self, username, password, first_name, last_name, email, role=UserRole.cashier, pin_code=None, is_active=True):
        with session_scope() as session:
            user_id = str(uuid.uuid4())
            
            # Hash password and PIN
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            pin_hash = None
            if pin_code:
                pin_hash = bcrypt.hashpw(pin_code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            new_user = User(
                id=user_id,
                username=username,
                password_hash=password_hash,
                pin_code=pin_hash,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
                is_active=is_active
            )
            session.add(new_user)
        return self.get_users_by_filters(id=user_id)

    def get_users_by_filters(self, id=None, username=None, role=None, is_active=None, all=False, start_and_end=None):
        with session_scope() as session:
            query = session.query(User)
            query = query.order_by(User.username.asc())

            if id:
                query = query.filter(User.id == id)
            if username:
                query = query.filter(User.username.ilike(f'%{username}%'))
            if role:
                query = query.filter(User.role == role)
            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            if all:
                total = query.count()
                if start_and_end:
                    start, end = start_and_end
                    query = query.slice(start, end)
                users = query.all()
                user_list = [self.user_format(user) for user in users]
                return {'amount': total, 'users': user_list} if user_list else None
            else:
                user = query.first()
                return None if user is None else self.user_format(user)

    def update_user(self, user_id, **fields):
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            for key, value in fields.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            return self.user_format(user)

    def delete_user(self, user_id):
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            session.delete(user)
        return True
    
    def authenticate_by_credentials(self, username, password):
        """Authenticate user by username and password"""
        with session_scope() as session:
            user = session.query(User).filter(
                and_(
                    User.username == username,
                    User.is_active == True
                )
            ).first()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return self.user_format(user)
            return None
    
    def authenticate_by_pin(self, pin_code):
        """Authenticate user by PIN code"""
        with session_scope() as session:
            users = session.query(User).filter(
                and_(
                    User.pin_code.isnot(None),
                    User.is_active == True
                )
            ).all()
            
            for user in users:
                if bcrypt.checkpw(pin_code.encode('utf-8'), user.pin_code.encode('utf-8')):
                    return self.user_format(user)
            return None
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.now(timezone.utc)
                user.failed_login_attempts = 0  # Reset failed attempts on successful login
                user.locked_until = None  # Clear any lockout
    
    def get_user_permissions(self, user_id):
        """Get all permissions for a user (role + individual permissions)"""
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            permissions = set()
            
            # Get role-based permissions (simplified - in real implementation would query role_permissions table)
            role_permissions = {
                UserRole.admin: ['*'],  # All permissions
                UserRole.manager: ['menu.view', 'menu.create', 'menu.edit', 'inventory.view', 'inventory.edit', 'sales.process', 'sales.refund', 'reports.view', 'users.view'],
                UserRole.cashier: ['menu.view', 'sales.process', 'receipts.print'],
                UserRole.trainee: ['menu.view']
            }
            
            if user.role in role_permissions:
                permissions.update(role_permissions[user.role])
            
            return list(permissions)
    
    def increment_failed_login(self, username):
        """Increment failed login attempts and lock account if necessary"""
        with session_scope() as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 3:
                    user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                return user.failed_login_attempts
            return 0

    def user_format(self, user):
        return {
            'id': str(user.id),
            'username': user.username,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'email': user.email,
            'role': user.role.value if user.role else None,
            'isActive': user.is_active,
            'failedLoginAttempts': user.failed_login_attempts,
            'lockedUntil': user.locked_until.isoformat() if user.locked_until else None,
            'lastLogin': user.last_login.isoformat() if user.last_login else None,
            'shiftStartTime': user.shift_start_time.isoformat() if user.shift_start_time else None,
            'shiftEndTime': user.shift_end_time.isoformat() if user.shift_end_time else None,
            'createdAt': user.created_at.isoformat(),
            'updatedAt': user.updated_at.isoformat()
        }
