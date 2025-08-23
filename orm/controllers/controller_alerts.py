import uuid
from datetime import datetime, timezone

from orm.db_init import session_scope
from orm.models.model_alerts import Alerts


class AlertsController:
    def create_alert(self, object_id, alert_type, notification_sent=False, notification_method=None, alert_time=None):
        with session_scope() as session:
            alert_id = str(uuid.uuid4())
            new_alert = Alerts(
                id=alert_id,
                object_id=object_id,
                alert_time=alert_time or datetime.now(timezone.utc),
                alert_type=alert_type,
                notification_sent=notification_sent,
                notification_method=notification_method
            )
            session.add(new_alert)
        return self.get_alerts_by_filters(id=alert_id)

    def get_alerts_by_filters(self, id=None, object_id=None, alert_type=None, notification_sent=None, all=False, start_and_end=None):
        with session_scope() as session:
            query = session.query(Alerts)
            query = query.order_by(Alerts.alert_time.desc())

            if id:
                query = query.filter(Alerts.id == id)
            if object_id:
                query = query.filter(Alerts.object_id == object_id)
            if alert_type:
                query = query.filter(Alerts.alert_type == alert_type)
            if notification_sent is not None:
                query = query.filter(Alerts.notification_sent == notification_sent)

            if all:
                total = query.count()
                if start_and_end:
                    start, end = start_and_end
                    query = query.slice(start, end)
                alerts = query.all()
                alert_list = [self.alert_format(a) for a in alerts]
                return {'amount': total, 'alerts': alert_list} if alert_list else None
            else:
                alert = query.first()
                return None if alert is None else self.alert_format(alert)

    def update_alert(self, alert_id, **fields):
        with session_scope() as session:
            alert = session.query(Alerts).filter(Alerts.id == alert_id).first()
            if not alert:
                return None
            for key, value in fields.items():
                if hasattr(alert, key) and value is not None:
                    setattr(alert, key, value)
            return self.alert_format(alert)

    def delete_alert(self, alert_id):
        with session_scope() as session:
            alert = session.query(Alerts).filter(Alerts.id == alert_id).first()
            if not alert:
                return False
            session.delete(alert)
        return True

    def alert_format(self, alert):
        return {
            'id': str(alert.id),
            'object_id': str(alert.object_id),
            'alert_time': alert.alert_time.isoformat(),
            'alert_type': alert.alert_type,
            'notification_sent': alert.notification_sent,
            'notification_method': alert.notification_method
        }

