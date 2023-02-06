from datetime import datetime
import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import raw_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(50))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'Order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id =  db.Column(db.Integer, db.ForeignKey('User.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

class Offer(db.Model):
    __tablename__ = 'Offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id =  db.Column(db.Integer, db.ForeignKey('Order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.create_all()

    for user_data in raw_data.users:
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()

    for order_data in raw_data.orders:
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%m/%d/%Y').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%m/%d/%Y').date()
        new_order = Order(**order_data)
        db.session.add(new_order)
        db.session.commit()

    for offer_data in raw_data.offers:
        new_offer = Offer(**offer_data)
        db.session.add(new_offer)
        db.session.commit()


@app.route('/users', methods=['GET'])
def users():
    if request.method == 'GET':
        users = User.query.all()
        result = [user.to_dict() for user in users]

        return json.dumps(result), {'Content-Type':'application/json; charset=utf-8'}


@app.route('/users/<int:uid>', methods=['GET'])
def user(uid:int):
    if request.method == 'GET':
        user = User.query.get(uid).to_dict()

        return json.dumps(user), {'Content-Type':'application/json; charset=utf-8'}


@app.route('/orders', methods=['GET'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all()
        result = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['start_date'] = str(order_dict['start_date'])
            order_dict['end_date'] = str(order_dict['end_date'])
            result.append(order_dict)

        return json.dumps(result), {'Content-Type':'application/json; charset=utf-8'}


@app.route('/orders/<int:oid>', methods=['GET'])
def order(oid:int):
    if request.method == 'GET':
        order = Order.query.get(oid)
        order_dict = order.to_dict()
        order_dict['start_date'] = str(order_dict['start_date'])
        order_dict['end_date'] = str(order_dict['end_date'])

        return json.dumps(order_dict), {'Content-Type':'application/json; charset=utf-8'}


@app.route('/offers', methods=['GET'])
def offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        result = [offer.to_dict() for offer in offers]

        return json.dumps(result), {'Content-Type':'application/json; charset=utf-8'}


@app.route('/offers/<int:ofid>', methods=['GET'])
def offer(ofid:int):
    if request.method == 'GET':
        offer = Offer.query.get(ofid).to_dict()

        return json.dumps(offer), {'Content-Type':'application/json; charset=utf-8'}


@app.route('/users', methods=['POST'])
def create_user():
    if request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()

        return '', 201


@app.route('/users/<int:uid>', methods=['PUT', 'DELETE'])
def update_user(uid:int):
    user = User.query.get(uid)
    if request.method == 'PUT':
        user_data = json.loads(request.data)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        db.session.commit()

        return '', 202

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()

        return '', 204


@app.route('/orders', methods=['POST'])
def create_order():
    if request.method == 'POST':
        order_data = json.loads(request.data)
        db.session.add(Order(**order_data))
        db.session.commit()

        return '', 201


@app.route('/orders/<int:oid>', methods=['PUT', 'DELETE'])
def update_order(oid:int):
    order = Order.query.get(oid)
    if request.method == 'PUT':
        order_data = json.loads(request.data)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = order_data['start_date']
        order.end_date = order_data['end_date']
        order.address = order_data['address']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.commit()

        return '', 202

    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()

        return '', 204


@app.route('/offers', methods=['POST'])
def create_offer():
    if request.method == 'POST':
        offer_data = json.loads(request.data)
        db.session.add(Offer(**offer_data))
        db.session.commit()

        return '', 201


@app.route('/offers/<int:ofid>', methods=['PUT', 'DELETE'])
def update_offer(ofid:int):

    offer = Offer.query.get(ofid)

    if request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']
        db.session.commit()

        return '', 202

    elif request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        
        return '', 204


if __name__ == '__main__':
    app.run()



