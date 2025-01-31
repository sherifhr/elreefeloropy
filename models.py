from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'owner'
    password_hash = db.Column(db.String(300), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, name, phone, email, role):
        self.name = name
        self.phone = phone        
        self.email = email
        self.role = role

    def __repr__(self):
        return f'<Users {self.email}, Role: {self.role}>'

class Farms(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  farm_name = db.Column(db.String(100))
  product_type= db.Column(db.String(20))
  user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
  phone = db.Column(db.String(20))
  email = db.Column(db.String(50)) 
  address1 = db.Column(db.String(100))
  address2 = db.Column(db.String(100))
  products = db.relationship('Products', backref='farm', lazy='dynamic')

  def __init__(self, farm_name, product_type, user_id, phone, email, address1, address2):
      self.farm_name = farm_name
      self.product_type = product_type
      self.user_id = user_id
      self.phone = phone
      self.email = email
      self.address1 = address1
      self.address2 = address2


class Products(db.Model): #products are related to farm
  id = db.Column(db.Integer, primary_key = True)
  farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
  prod_category = db.Column(db.String(100))
  prod_name = db.Column(db.String(100))
  package = db.Column(db.String(10))
  unit_price = db.Column(db.Integer) 
  filename = db.Column(db.String(30))
  stock = db.Column(db.Integer)
  event_datetime = db.Column(db.String(30))
  
  def __init__(self, farm_id, prod_category,prod_name, package, unit_price,filename, stock, event_datetime):
      self.farm_id = farm_id
      self.prod_category = prod_category
      self.prod_name = prod_name
      self.package = package
      self.unit_price = unit_price
      self.filename = filename
      self.stock = stock
      self.event_datetime = event_datetime
 
class Cart_items(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
  quantity = db.Column(db.Integer) 
  package = db.Column(db.String(10))
  unit_price = db.Column(db.Integer)
  filename = db.Column(db.String(30))
  event_datetime = db.Column(db.String(50))
  ordered=db.Column(db.Boolean,  default='False')

  users = db.relationship("Users", backref="cart_items")
  products = db.relationship("Products", backref="cart_items")
  farms = db.relationship("Farms", backref="cart_items")

  def __init__(self, user_id, farm_id, product_id, quantity, package, unit_price, 
               filename, event_datetime, ordered):
      self.user_id = user_id
      self.farm_id = farm_id
      self.product_id = product_id
      self.quantity = quantity
      self.package = package
      self.unit_price = unit_price
      self.filename = filename
      self.event_datetime = event_datetime
      self.ordered=ordered
      

class Orders(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  order_no = db.Column(db.String(30))
  order_date = db.Column(db.String(50))
  order_farm = db.Column(db.String(50))
  farm_phone = db.Column(db.String(20))
  order_user = db.Column(db.String(50))
  user_phone = db.Column(db.String(20))
  user_email = db.Column(db.String(45))
  status = db.Column(db.String(20), default='Pending')
  event_datetime = db.Column(db.String(50))

  items = db.relationship('Order_Items', backref='orders', lazy=True)
   
  def __init__(self, order_no, order_date, order_farm, farm_phone, order_user, user_phone, 
               user_email, status, event_datetime, items):
    self.order_no = order_no
    self.order_date = order_date
    self.order_farm = order_farm
    self.farm_phone = farm_phone
    self.order_user = order_user
    self.user_phone = user_phone
    self.user_email = user_email
    self.status = status
    self.event_datetime = event_datetime

    if items is not None:
            self.items = items

class Order_Items(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  order_no = db.Column(db.String(30))
  item_id = db.Column(db.Integer)
  item_name=db.Column(db.String(100))
  quantity =db.Column(db.Integer)
  unit_price =db.Column(db.Float)
  total_price=db.Column(db.Float)
  order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

  def __init__(self, order_no, item_id, item_name, quantity, unit_price, total_price, order_id):
        self.order_no = order_no
        self.item_id= item_id
        self.item_name = item_name
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price
        self.order_id = order_id


class Stores(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  user_id=db.Column(db.Integer)
  store_name = db.Column(db.String(50))
  activity = db.Column(db.String(50))
  phone1 = db.Column(db.String(50))
  phone2 = db.Column(db.String(50))
  address = db.Column(db.String(150))
  filename = db.Column(db.String(50))
  adv_class=db.Column(db.String(10))

  def __init__(self, user_id, store_name, activity, phone1, phone2, address, filename, adv_class):
    self.user_id = user_id
    self.store_name = store_name
    self.activity = activity
    self.phone1 = phone1
    self.phone2 = phone2
    self.address = address
    self.filename = filename
    self.adv_class = adv_class


class House(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  daily_rent= db.Column(db.Integer)
  ad_no = db.Column(db.Integer)
  ad_date =db.Column(db.String(20))
  house_type = db.Column(db.String(20))
  area = db.Column(db.String(50))
  address = db.Column(db.String(100))
  rooms =db.Column(db.Integer)
  bathrooms =db.Column(db.Integer)
  kitchen =db.Column(db.Boolean,  default='False')
  pool =db.Column(db.Boolean,  default='False')
  pool_kids =db.Column(db.Boolean,  default='False')
  aircon= db.Column(db.Boolean,  default='False')
  grill=db.Column(db.Boolean,  default='False')
  owner = db.Column(db.String(50))
  phone = db.Column(db.String(20))
  filename = db.Column(db.String(30))

  def __init__(self, daily_rent,               
               ad_no, 
               ad_date, 
               house_type, 
               area,
               address,
               rooms,
               bathrooms, 
               kitchen, 
               pool, 
               pool_kids, 
               aircon,
               grill, 
               owner, 
               phone, 
               filename):

    self.daily_rent =daily_rent
    self.ad_no = ad_no
    self.ad_date = ad_date
    self.house_type = house_type
    self.area = area
    self.address = address
    self.rooms = rooms
    self.bathrooms = bathrooms
    self.kitchen = kitchen
    self.pool = pool
    self.pool_kids = pool_kids    
    self.aircon= aircon
    self.grill = grill
    self.owner = owner
    self.phone = phone
    self.filename= filename

