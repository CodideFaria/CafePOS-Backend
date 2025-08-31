import json
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from decouple import config
from apis.base_handler import BaseHandler

from orm.controllers.controller_users import UserController
user_controller = UserController()

JWT_SECRET = config('JWT_SECRET_KEY')
JWT_ALGORITHM = config('JWT_ALGORITHM')
JWT_EXPIRE_MINUTES = int(config('JWT_EXPIRE_MINUTES'))


class AuthLoginHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        if data is None:
            return

        username = data.get('username')
        password = data.get('password')
        pin_code = data.get('pinCode')
        remember_me = data.get('rememberMe', False)

        # Validate input
        if not pin_code and (not username or not password):
            self.write_error_response(
                ["Username and password, or PIN code is required"], 
                400, 
                "INVALID_CREDENTIALS"
            )
            return

        try:
            if pin_code:
                # PIN-based authentication
                user = user_controller.authenticate_by_pin(pin_code)
            else:
                # Username/password authentication
                user = user_controller.authenticate_by_credentials(username, password)

            if not user:
                self.write_error_response(
                    ["Invalid credentials"], 
                    401, 
                    "INVALID_CREDENTIALS"
                )
                return

            if not user.get('isActive'):
                self.write_error_response(
                    ["Account is deactivated"], 
                    403, 
                    "ACCOUNT_DEACTIVATED"
                )
                return

            # Check if account is locked
            if user.get('lockedUntil') and datetime.fromisoformat(user['lockedUntil'].replace('Z', '+00:00')) > datetime.now(timezone.utc):
                lockout_until = user['lockedUntil']
                self.write_error_response(
                    [f"Account is locked until {lockout_until}"], 
                    423, 
                    "ACCOUNT_LOCKED",
                    {"lockoutInfo": {"lockoutUntil": lockout_until, "attemptsRemaining": 0}}
                )
                return

            # Generate JWT token
            expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
            if remember_me:
                expiration = datetime.now(timezone.utc) + timedelta(days=30)

            payload = {
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'exp': expiration,
                'iat': datetime.now(timezone.utc)
            }

            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            # Update last login
            user_controller.update_last_login(user['id'])

            # Get user permissions
            permissions = user_controller.get_user_permissions(user['id'])

            response_data = {
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "firstName": user['firstName'],
                    "lastName": user['lastName'],
                    "email": user['email'],
                    "role": user['role'],
                    "permissions": permissions,
                    "isActive": user['isActive'],
                    "lastLogin": user.get('lastLogin'),
                    "shiftStartTime": user.get('shiftStartTime'),
                    "shiftEndTime": user.get('shiftEndTime')
                },
                "token": token,
                "sessionExpiry": expiration.isoformat()
            }

            self.write_success(response_data)

        except Exception as e:
            self.write_error_response(
                ["Authentication failed"], 
                500, 
                "INTERNAL_ERROR"
            )


class AuthLogoutHandler(BaseHandler):
    def post(self):
        # In a stateless JWT system, logout is typically handled client-side
        # by removing the token. Here we could add token to a blacklist if needed.
        self.write_success({"message": "Logged out successfully"})


class AuthMeHandler(BaseHandler):
    def get(self):
        # Get current user info from JWT token
        auth_header = self.request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            self.write_error_response(
                ["Authorization token required"], 
                401, 
                "TOKEN_REQUIRED"
            )
            return

        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload['user_id']
            
            user = user_controller.get_users_by_filters(id=user_id)
            if not user:
                self.write_error_response(
                    ["User not found"], 
                    404, 
                    "USER_NOT_FOUND"
                )
                return

            permissions = user_controller.get_user_permissions(user_id)
            
            response_data = {
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "firstName": user['firstName'],
                    "lastName": user['lastName'],
                    "email": user['email'],
                    "role": user['role'],
                    "permissions": permissions,
                    "isActive": user['isActive'],
                    "lastLogin": user.get('lastLogin'),
                    "shiftStartTime": user.get('shiftStartTime'),
                    "shiftEndTime": user.get('shiftEndTime')
                }
            }

            self.write_success(response_data)

        except jwt.ExpiredSignatureError:
            self.write_error_response(
                ["Token has expired"], 
                401, 
                "TOKEN_EXPIRED"
            )
        except jwt.InvalidTokenError:
            self.write_error_response(
                ["Invalid token"], 
                401, 
                "TOKEN_INVALID"
            )
        except Exception as e:
            self.write_error_response(
                ["Authentication failed"], 
                500, 
                "INTERNAL_ERROR"
            )


class AuthRefreshHandler(BaseHandler):
    def post(self):
        auth_header = self.request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            self.write_error_response(
                ["Authorization token required"], 
                401, 
                "TOKEN_REQUIRED"
            )
            return

        token = auth_header.split(' ')[1]
        
        try:
            # Allow expired tokens for refresh
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
            user_id = payload['user_id']
            
            # Check if user still exists and is active
            user = user_controller.get_users_by_filters(id=user_id)
            if not user or not user.get('isActive'):
                self.write_error_response(
                    ["User not found or inactive"], 
                    401, 
                    "USER_INACTIVE"
                )
                return

            # Generate new token
            expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
            new_payload = {
                'user_id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'exp': expiration,
                'iat': datetime.now(timezone.utc)
            }

            new_token = jwt.encode(new_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            response_data = {
                "token": new_token,
                "sessionExpiry": expiration.isoformat()
            }

            self.write_success(response_data)

        except jwt.InvalidTokenError:
            self.write_error_response(
                ["Invalid token"], 
                401, 
                "TOKEN_INVALID"
            )
        except Exception as e:
            self.write_error_response(
                ["Token refresh failed"], 
                500, 
                "INTERNAL_ERROR"
            )


class AuthValidateSessionHandler(BaseHandler):
    def post(self):
        auth_header = self.request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            self.write_error_response(
                ["Authorization token required"], 
                401, 
                "TOKEN_REQUIRED"
            )
            return

        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload['user_id']
            
            user = user_controller.get_users_by_filters(id=user_id)
            if not user:
                self.write_error_response(
                    ["User not found"], 
                    404, 
                    "USER_NOT_FOUND"
                )
                return

            if not user.get('isActive'):
                self.write_error_response(
                    ["Account is deactivated"], 
                    403, 
                    "ACCOUNT_DEACTIVATED"
                )
                return

            permissions = user_controller.get_user_permissions(user_id)
            
            response_data = {
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "firstName": user['firstName'],
                    "lastName": user['lastName'],
                    "email": user['email'],
                    "role": user['role'],
                    "permissions": permissions,
                    "isActive": user['isActive'],
                    "lastLogin": user.get('lastLogin'),
                    "shiftStartTime": user.get('shiftStartTime'),
                    "shiftEndTime": user.get('shiftEndTime')
                },
                "sessionValid": True,
                "sessionExpiry": datetime.fromtimestamp(payload['exp'], timezone.utc).isoformat()
            }

            self.write_success(response_data, message="Session valid")

        except jwt.ExpiredSignatureError:
            self.write_error_response(
                ["Token has expired"], 
                401, 
                "TOKEN_EXPIRED"
            )
        except jwt.InvalidTokenError:
            self.write_error_response(
                ["Invalid token"], 
                401, 
                "TOKEN_INVALID"
            )
        except Exception as e:
            self.write_error_response(
                ["Session validation failed"], 
                500, 
                "INTERNAL_ERROR"
            )


class AuthPasswordResetRequestHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        if data is None:
            return

        email = data.get('email')
        if not email:
            self.write_error_response(
                ["Email is required"], 
                400, 
                "VALIDATION_ERROR"
            )
            return

        try:
            # Check if user with email exists
            user = user_controller.get_users_by_filters(email=email)
            
            # Always return success for security (don't reveal if email exists)
            response_data = {
                "emailSent": True,
                "expiresIn": 3600  # 1 hour
            }
            
            if user:
                # In a real implementation, generate reset token and send email
                # For now, just return success
                pass
            
            self.write_success(response_data, message="Password reset email sent")

        except Exception as e:
            self.write_error_response(
                ["Failed to process password reset request"], 
                500, 
                "INTERNAL_ERROR"
            )


class AuthValidateResetTokenHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        if data is None:
            return

        token = data.get('token')
        if not token:
            self.write_error_response(
                ["Token is required"], 
                400, 
                "VALIDATION_ERROR"
            )
            return

        try:
            # In a real implementation, validate reset token from database
            # For now, simulate validation
            response_data = {
                "tokenValid": True,
                "expiresAt": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
            }
            
            self.write_success(response_data, message="Token is valid")

        except Exception as e:
            self.write_error_response(
                ["Failed to validate reset token"], 
                500, 
                "INTERNAL_ERROR"
            )


class AuthPasswordResetConfirmHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        if data is None:
            return

        token = data.get('token')
        new_password = data.get('newPassword')
        
        if not token or not new_password:
            self.write_error_response(
                ["Token and new password are required"], 
                400, 
                "VALIDATION_ERROR"
            )
            return

        # Password validation
        if len(new_password) < 8:
            self.write_error_response(
                ["Password must be at least 8 characters long"], 
                400, 
                "VALIDATION_ERROR"
            )
            return

        try:
            # In a real implementation, validate token and update password
            # For now, simulate success
            response_data = {
                "passwordReset": True
            }
            
            self.write_success(response_data, message="Password reset successful")

        except Exception as e:
            self.write_error_response(
                ["Failed to reset password"], 
                500, 
                "INTERNAL_ERROR"
            )