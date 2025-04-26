from datetime import datetime
from config import db

class Service:
    def __init__(self, name, description, price, duration):
        self.name = name
        self.description = description
        self.price = float(price)
        self.duration = int(duration)  # duration in minutes

    @staticmethod
    def from_dict(source):
        return Service(
            source['name'],
            source['description'],
            source['price'],
            source['duration']
        )

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'duration': self.duration
        }

class Product:
    def __init__(self, name, quantity, price, unit_cost):
        self.name = name
        self.quantity = float(quantity)
        self.price = float(price)
        self.unit_cost = float(unit_cost)

    @staticmethod
    def from_dict(source):
        return Product(
            source['name'],
            source['quantity'],
            source['price'],
            source['unit_cost']
        )

    def to_dict(self):
        return {
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price,
            'unit_cost': self.unit_cost
        }

class Appointment:
    def __init__(self, client_name, client_phone, service_name, datetime, status='scheduled'):
        self.client_name = client_name
        self.client_phone = client_phone
        self.service_name = service_name
        self.datetime = datetime
        self.status = status  # scheduled, confirmed, completed, cancelled

    @staticmethod
    def from_dict(source):
        return Appointment(
            source['client_name'],
            source['client_phone'],
            source['service_name'],
            source['datetime'],
            source.get('status', 'scheduled')
        )

    def to_dict(self):
        return {
            'client_name': self.client_name,
            'client_phone': self.client_phone,
            'service_name': self.service_name,
            'datetime': self.datetime,
            'status': self.status
        }

class ServiceExecution:
    def __init__(self, appointment_id, products_used, total_cost, total_price, execution_date=None):
        self.appointment_id = appointment_id
        self.products_used = products_used  # List of {product_name, quantity_used}
        self.total_cost = float(total_cost)
        self.total_price = float(total_price)
        self.execution_date = execution_date or datetime.now()

    @staticmethod
    def from_dict(source):
        return ServiceExecution(
            source['appointment_id'],
            source['products_used'],
            source['total_cost'],
            source['total_price'],
            source.get('execution_date')
        )

    def to_dict(self):
        return {
            'appointment_id': self.appointment_id,
            'products_used': self.products_used,
            'total_cost': self.total_cost,
            'total_price': self.total_price,
            'execution_date': self.execution_date
        } 