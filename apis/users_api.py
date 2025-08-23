import json
from apis.base_handler import BaseHandler
from orm.controllers.controller_users import UserController
from orm.models.model_users import UserRole


class UsersHandler(BaseHandler):
    def initialize(self):
        self.user_controller = UserController()

    def get(self):
        users = self.user_controller.get_users_by_filters(all=True)
        if users:
            self.write_success(users)
        else:
            self.write_success({"users": [], "amount": 0})

    def post(self):
        data = self.get_json_body()
        if data is None:
            return
            
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        role = data.get('role', 'cashier')
        pin_code = data.get('pinCode')
        is_active = data.get('isActive', True)

        # Validation
        errors = []
        if not username or len(username.strip()) < 3:
            errors.append("Username must be at least 3 characters")
        elif len(username) > 50:
            errors.append("Username must be 50 characters or less")
            
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters")
            
        if not first_name or len(first_name.strip()) == 0:
            errors.append("First name is required")
        elif len(first_name) > 50:
            errors.append("First name must be 50 characters or less")
            
        if not last_name or len(last_name.strip()) == 0:
            errors.append("Last name is required")
        elif len(last_name) > 50:
            errors.append("Last name must be 50 characters or less")
            
        if not email or '@' not in email:
            errors.append("Valid email address is required")
        elif len(email) > 255:
            errors.append("Email must be 255 characters or less")
            
        if role not in [r.value for r in UserRole]:
            errors.append(f"Role must be one of: {', '.join([r.value for r in UserRole])}")
            
        if pin_code and len(pin_code) != 4:
            errors.append("PIN code must be exactly 4 digits")

        if errors:
            self.write_error_response(errors, 422, "VALIDATION_ERROR")
            return

        try:
            role_enum = UserRole(role)
            new_user = self.user_controller.create_user(
                username=username.strip(),
                password=password,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                email=email.strip().lower(),
                role=role_enum,
                pin_code=pin_code,
                is_active=is_active
            )
            self.write_success(new_user, 201)
        except Exception as e:
            self.write_error_response(["Failed to create user"], 500, "INTERNAL_ERROR")


class UserHandler(BaseHandler):
    def initialize(self):
        self.user_controller = UserController()

    def get(self, id):
        try:
            user = self.user_controller.get_users_by_filters(id=id)
            if user:
                self.write_success(user)
            else:
                self.write_error_response(["User not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to retrieve user"], 500, "INTERNAL_ERROR")

    def put(self, id):
        data = self.get_json_body()
        if data is None:
            return
            
        # Validate and prepare update data
        update_data = {}
        errors = []
        
        if 'username' in data:
            username = data['username']
            if not username or len(username.strip()) < 3:
                errors.append("Username must be at least 3 characters")
            elif len(username) > 50:
                errors.append("Username must be 50 characters or less")
            else:
                update_data['username'] = username.strip()
                
        if 'firstName' in data:
            first_name = data['firstName']
            if not first_name or len(first_name.strip()) == 0:
                errors.append("First name cannot be empty")
            elif len(first_name) > 50:
                errors.append("First name must be 50 characters or less")
            else:
                update_data['first_name'] = first_name.strip()
                
        if 'lastName' in data:
            last_name = data['lastName']
            if not last_name or len(last_name.strip()) == 0:
                errors.append("Last name cannot be empty")
            elif len(last_name) > 50:
                errors.append("Last name must be 50 characters or less")
            else:
                update_data['last_name'] = last_name.strip()
                
        if 'email' in data:
            email = data['email']
            if not email or '@' not in email:
                errors.append("Valid email address is required")
            elif len(email) > 255:
                errors.append("Email must be 255 characters or less")
            else:
                update_data['email'] = email.strip().lower()
                
        if 'role' in data:
            role = data['role']
            if role not in [r.value for r in UserRole]:
                errors.append(f"Role must be one of: {', '.join([r.value for r in UserRole])}")
            else:
                update_data['role'] = UserRole(role)
                
        if 'isActive' in data:
            update_data['is_active'] = bool(data['isActive'])
            
        if errors:
            self.write_error_response(errors, 422, "VALIDATION_ERROR")
            return

        try:
            updated_user = self.user_controller.update_user(id, **update_data)
            if updated_user:
                self.write_success(updated_user)
            else:
                self.write_error_response(["User not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to update user"], 500, "INTERNAL_ERROR")

    def delete(self, id):
        try:
            if self.user_controller.delete_user(id):
                self.set_status(204)
                self.finish()
            else:
                self.write_error_response(["User not found"], 404, "NOT_FOUND")
        except Exception as e:
            self.write_error_response(["Failed to delete user"], 500, "INTERNAL_ERROR")
