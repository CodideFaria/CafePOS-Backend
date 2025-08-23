import uuid

from orm.db_init import session_scope
from orm.models.model_roles import Role


class RoleController:
    def create_role(self, name, description=None):
        with session_scope() as session:
            role_id = str(uuid.uuid4())
            new_role = Role(
                id=role_id,
                name=name,
                description=description
            )
            session.add(new_role)
        return self.get_roles_by_filters(id=role_id)

    def get_roles_by_filters(self, id=None, name=None, all=False, start_and_end=None):
        with session_scope() as session:
            query = session.query(Role)
            query = query.order_by(Role.name.asc())

            if id:
                query = query.filter(Role.id == id)
            if name:
                query = query.filter(Role.name.ilike(f'%{name}%'))

            if all:
                total = query.count()
                if start_and_end:
                    start, end = start_and_end
                    query = query.slice(start, end)
                roles = query.all()
                role_list = [self.role_format(role) for role in roles]
                return {'amount': total, 'roles': role_list} if role_list else None
            else:
                role = query.first()
                return None if role is None else self.role_format(role)

    def update_role(self, role_id, **fields):
        with session_scope() as session:
            role = session.query(Role).filter(Role.id == role_id).first()
            if not role:
                return None
            for key, value in fields.items():
                if hasattr(role, key) and value is not None:
                    setattr(role, key, value)
            return self.role_format(role)

    def delete_role(self, role_id):
        with session_scope() as session:
            role = session.query(Role).filter(Role.id == role_id).first()
            if not role:
                return False
            session.delete(role)
        return True

    def role_format(self, role):
        return {
            'id': str(role.id),
            'name': role.name,
            'description': role.description
        }
