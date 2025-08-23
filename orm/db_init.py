from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from decouple import config
from .base import Base
from contextlib import contextmanager

# DONT REMOVE BELOW IT IS BEING USED TO POINT TO MODELS TO CREATE TABLES!!!
from orm.models.model_alerts import Alerts
from orm.models.model_menu import MenuItem
from orm.models.model_inventory import InventoryItem
from orm.models.model_stock_movements import StockMovement
from orm.models.model_stock_alerts import StockAlert
from orm.models.model_roles import Role
from orm.models.model_permissions import Permission
from orm.models.model_role_permissions import RolePermission
from orm.models.model_user_permissions import UserPermission
from orm.models.model_users import User
from orm.models.model_orders import Order
from orm.models.model_order_items import OrderItem
from orm.models.model_order_discounts import OrderDiscount

DATABASE_URL = config('DATABASE_URL')

Session = sessionmaker()
engine = create_engine(DATABASE_URL)
Session.configure(bind=engine)

def initialize_database():
    Base.metadata.create_all(bind=engine)

initialize_database()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
