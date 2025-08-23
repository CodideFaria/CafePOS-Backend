import json
from apis.base_handler import BaseHandler
from orm.controllers.controller_alerts import AlertsController


class AlertsHandler(BaseHandler):
    def initialize(self):
        self.alerts_controller = AlertsController()

    def get(self):
        alerts = self.alerts_controller.get_alerts_by_filters(all=True)
        self.write(json.dumps(alerts))

    def post(self):
        data = json.loads(self.request.body)
        inventory_item_id = data.get('inventory_item_id')
        alert_type = data.get('alert_type')
        notification_sent = data.get('notification_sent', False)
        notification_method = data.get('notification_method')

        if not inventory_item_id or not alert_type:
            self.set_status(400)
            self.write({"error": "Missing required alert data"})
            return

        new_alert = self.alerts_controller.create_alert(inventory_item_id, alert_type, notification_sent, notification_method)
        self.set_status(201)
        self.write(json.dumps(new_alert))


class AlertHandler(BaseHandler):
    def initialize(self):
        self.alerts_controller = AlertsController()

    def get(self, id):
        alert = self.alerts_controller.get_alerts_by_filters(id=id)
        if alert:
            self.write(json.dumps(alert))
        else:
            self.set_status(404)
            self.write({"error": "Alert not found"})

    def put(self, id):
        data = json.loads(self.request.body)
        updated_alert = self.alerts_controller.update_alert(id, **data)
        if updated_alert:
            self.write(json.dumps(updated_alert))
        else:
            self.set_status(404)
            self.write({"error": "Alert not found"})

    def delete(self, id):
        if self.alerts_controller.delete_alert(id):
            self.set_status(204)
        else:
            self.set_status(404)
            self.write({"error": "Alert not found"})
