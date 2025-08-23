import json
from apis.base_handler import BaseHandler
from orm.controllers.controller_roles import RoleController


class RolesHandler(BaseHandler):
    def initialize(self):
        self.role_controller = RoleController()

    def get(self):
        roles = self.role_controller.get_roles_by_filters(all=True)
        self.write(json.dumps(roles))

    def post(self):
        data = json.loads(self.request.body)
        name = data.get('name')
        description = data.get('description')

        if not name:
            self.set_status(400)
            self.write({"error": "Name is required"})
            return

        new_role = self.role_controller.create_role(name, description)
        self.set_status(201)
        self.write(json.dumps(new_role))


class RoleHandler(BaseHandler):
    def initialize(self):
        self.role_controller = RoleController()

    def get(self, id):
        role = self.role_controller.get_roles_by_filters(id=id)
        if role:
            self.write(json.dumps(role))
        else:
            self.set_status(404)
            self.write({"error": "Role not found"})

    def put(self, id):
        data = json.loads(self.request.body)
        updated_role = self.role_controller.update_role(id, **data)
        if updated_role:
            self.write(json.dumps(updated_role))
        else:
            self.set_status(404)
            self.write({"error": "Role not found"})

    def delete(self, id):
        if self.role_controller.delete_role(id):
            self.set_status(204)
        else:
            self.set_status(404)
            self.write({"error": "Role not found"})
