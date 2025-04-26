from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config, db
from models import Service, Product, Appointment, ServiceExecution
from utils import (
    send_appointment_confirmation,
    send_appointment_reminder,
    calculate_fractional_cost,
    check_low_stock
)
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.config.from_object(Config)

# Routes for Services
@app.route('/services', methods=['GET', 'POST'])
def services():
    if request.method == 'POST':
        service = Service(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            duration=int(request.form['duration'])
        )
        db.collection('services').document().set(service.to_dict())
        flash('Serviço cadastrado com sucesso!', 'success')
        return redirect(url_for('services'))
    
    services = [Service.from_dict(doc.to_dict()) for doc in db.collection('services').stream()]
    return render_template('services.html', services=services)

# Routes for Products
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            quantity=float(request.form['quantity']),
            price=float(request.form['price']),
            unit_cost=float(request.form['unit_cost'])
        )
        db.collection('products').document().set(product.to_dict())
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('products'))
    
    products = [Product.from_dict(doc.to_dict()) for doc in db.collection('products').stream()]
    low_stock_products = [p for p in products if check_low_stock(p, Config.LOW_STOCK_THRESHOLD)]
    return render_template('products.html', products=products, low_stock_products=low_stock_products)

# Routes for Appointments
@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    if request.method == 'POST':
        appointment_date = datetime.strptime(
            f"{request.form['date']} {request.form['time']}", 
            '%Y-%m-%d %H:%M'
        )
        
        appointment = Appointment(
            client_name=request.form['client_name'],
            client_phone=request.form['client_phone'],
            service_name=request.form['service_name'],
            datetime=appointment_date
        )
        
        doc_ref = db.collection('appointments').document()
        doc_ref.set(appointment.to_dict())
        
        # Send confirmation message
        success, message = send_appointment_confirmation(appointment)
        if success:
            flash('Agendamento realizado e confirmação enviada!', 'success')
        else:
            flash(f'Agendamento realizado, mas erro ao enviar confirmação: {message}', 'warning')
            
        return redirect(url_for('appointments'))
    
    services = [Service.from_dict(doc.to_dict()) for doc in db.collection('services').stream()]
    appointments = [Appointment.from_dict(doc.to_dict()) 
                   for doc in db.collection('appointments')
                   .where('datetime', '>=', datetime.now())
                   .stream()]
    
    return render_template('appointments.html', services=services, appointments=appointments)

# Routes for Service Execution
@app.route('/execute_service/<appointment_id>', methods=['GET', 'POST'])
def execute_service(appointment_id):
    if request.method == 'POST':
        products_used = []
        total_cost = 0
        
        for product_id, quantity in request.form.items():
            if product_id.startswith('product_') and float(quantity) > 0:
                product_id = product_id.replace('product_', '')
                product_doc = db.collection('products').document(product_id).get()
                product = Product.from_dict(product_doc.to_dict())
                
                quantity_used = float(quantity)
                cost = calculate_fractional_cost(product, quantity_used)
                
                products_used.append({
                    'product_name': product.name,
                    'quantity_used': quantity_used
                })
                total_cost += cost
                
                # Update product quantity
                new_quantity = product.quantity - quantity_used
                db.collection('products').document(product_id).update({
                    'quantity': new_quantity
                })
        
        appointment_doc = db.collection('appointments').document(appointment_id).get()
        appointment = Appointment.from_dict(appointment_doc.to_dict())
        
        service_doc = db.collection('services').document(appointment.service_name).get()
        service = Service.from_dict(service_doc.to_dict())
        
        execution = ServiceExecution(
            appointment_id=appointment_id,
            products_used=products_used,
            total_cost=total_cost,
            total_price=service.price
        )
        
        db.collection('service_executions').document().set(execution.to_dict())
        db.collection('appointments').document(appointment_id).update({'status': 'completed'})
        
        flash('Serviço executado com sucesso!', 'success')
        return redirect(url_for('appointments'))
    
    appointment = db.collection('appointments').document(appointment_id).get()
    products = [Product.from_dict(doc.to_dict()) for doc in db.collection('products').stream()]
    
    return render_template('execute_service.html', 
                         appointment=Appointment.from_dict(appointment.to_dict()),
                         products=products)

# Financial Reports
@app.route('/reports')
def reports():
    executions = [ServiceExecution.from_dict(doc.to_dict()) 
                 for doc in db.collection('service_executions').stream()]
    
    total_revenue = sum(exe.total_price for exe in executions)
    total_cost = sum(exe.total_cost for exe in executions)
    total_profit = total_revenue - total_cost
    
    avg_profit = total_profit / len(executions) if executions else 0
    
    products = [Product.from_dict(doc.to_dict()) for doc in db.collection('products').stream()]
    low_stock = [p for p in products if check_low_stock(p, Config.LOW_STOCK_THRESHOLD)]
    
    return render_template('reports.html',
                         total_revenue=total_revenue,
                         total_cost=total_cost,
                         total_profit=total_profit,
                         avg_profit=avg_profit,
                         low_stock=low_stock)

@app.route('/')
def index():
    return render_template('index.html', config=Config)

if __name__ == '__main__':
    app.run(debug=True)
