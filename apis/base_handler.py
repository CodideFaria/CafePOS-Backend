import tornado.web
import json
import uuid
from datetime import datetime, timezone
from orm.db_init import session_scope


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.set_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", "true")

    def options(self, *args):
        self.set_status(204)
        self.finish()

    def get_session(self):
        return session_scope()
    
    def write_success(self, data=None, status_code=200, message=None):
        """Write successful response in standardized format"""
        self.set_status(status_code)
        if data is None:
            data = {}
        
        response = {
            "data": data,
            "errors": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if message:
            response["message"] = message
            
        self.write(json.dumps(response, default=str))
    
    def write_error_response(self, errors, status_code=400, error_code=None, data=None):
        """Write error response in standardized format"""
        self.set_status(status_code)
        
        if isinstance(errors, str):
            errors = [errors]
        
        response = {
            "data": data or {},
            "errors": errors,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requestId": str(uuid.uuid4()),
            "statusCode": status_code
        }
        
        if error_code:
            response["errorCode"] = error_code
            
        self.write(json.dumps(response, default=str))
    
    def get_json_body(self):
        """Parse JSON body with error handling"""
        try:
            if self.request.body:
                return json.loads(self.request.body)
            return {}
        except json.JSONDecodeError:
            self.write_error_response(["Invalid JSON in request body"], 400, "INVALID_JSON")
            return None