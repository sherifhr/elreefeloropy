from flask import Flask, render_template, request, redirect, url_for , session, send_from_directory
from flask import Flask, redirect, session, url_for, request,render_template, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Farms, Users, Products, Cart_items, Orders, Order_Items, Stores, House
from datetime import datetime
import sqlite3, os, pymysql
from functools import wraps
from flask import Flask, jsonify
#from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import json, requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://elreefeloropy:password#1@elreefeloropy.mysql.pythonanywhere-services.com/elreefeloropy$Market

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sherifhr1:password#1@sherifhr1.mysql.pythonanywhere-services.com/sherifhr1$Market'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sherifhr:password#1@localhost/Market'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sherifhr1:NewLife#1@sherifhr1.mysql.pythonanywhere-services.com/sherifhr1$Market'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sherifhr:NewLife#2@localhost/Market'
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Market.db"

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://salma:password#1@localhost/Market'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sherifhr1:password#1@sherifhr1.mysql.pythonanywhere-services.com/sherifhr1$Market'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"
app.config['UPLOAD_FOLDER'] = '/static/New_images' #test
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit to 16 MB

ALLOWED_EXTENSIONS = {'txt', 'odg', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


#db errors handling test
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_POOL_RECYCLE = 250

db.init_app(app)
     

with app.app_context():
        db.create_all()

app.secret_key = 'f5746747a9b7fa1f5dd11963eaf8b22d45d691315703ff88d443bb0abf075c19'

current_datetime = datetime.now()

formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def index():
    session.clear()
    login_required
    return render_template('index.html')
  #  return render_template('user-guide-1.html')

def login_required(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))  # Redirect to login page if user is not logged in
        return route_function(*args, **kwargs)
    return decorated_function


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            name  = request.form.get('name')
            phone = request.form.get('phone')
            email = request.form.get('email')
            role  = request.form['role']
            password = request.form.get('password')
            # Check if the username already exists
            user = Users.query.filter_by(name=name).first()
            if user:
                flash('Username already exists. Please choose a different one.', 'danger')
                return redirect(url_for('signup'))
            else:
                # Create a new user
                new_user = Users(name=name, phone=phone, email=email, role=role)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
           # flash('You have successfully registered. You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('signup.html')
    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            password = request.form.get('password_hash')
            user = Users.query.filter_by(name=name).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
                
        return render_template('login.html')
    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/dashboard')
def dashboard():
    try:
        if current_user != "":
            user=current_user.name    
            user = db.session.query(Users)\
                .filter(Users.name==current_user.name)\
                .first()

        farm= db.session.query(Farms)\
            .filter(Farms.user_id==user.id)\
            .first()

        if user.role=='admin':
                return render_template('dashboard_admin.html')
                #return render_template('dashboard_customers.html')
        elif user.role=='owner':
            if farm:
                return render_template('dashboard_farm_owners.html', farm=farm )  
            else:
                return render_template('dashboard_new.html')  
        elif user.role=='customer':
                return render_template('dashboard_customers.html')
                #return redirect(url_for('prod_list'))
        elif user.role=='business1':
                return render_template('dashboard_store_owners.html')
                #return redirect(url_for('add_store'))
        else:
            if user.role=='business2':
                return render_template('dashboard_house_owners.html')
               # return (user.role)
              

        return render_template('login.html')

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

#reads all table records
def cart_table_count():
    count= db.session.query(Cart_items).count
    return count
    
#--Add owner/user----------------------------------------------------
@app.route('/check_po/<user_name>')
def check_po(user_name):
    try:
        user = db.session.query(Orders).filter(Orders.order_user==current_user.name).first()
        if user:
            purchase_order=True    
            return ('You are not authorized')
        else:
            return('No purchase orders available for user!') 

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500

@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST']) 
def delete_user(user_id):
    user = db.session.query(Users).filter(Users.id==user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return ('Farm Owner deleted sussfully')  
    else:
        return 'User not found', 404

    #return redirect(url_for('prod_list'))

# #----customers --------
@app.route('/users_list')
def users_list():
    try:
        #user = current_user.name
        title='Users List'
        rows = db.session.query(Users).all()
        if not rows:
            return jsonify({"message": "No data found"}), 404
        return render_template('users_list.html', rows=rows, title=title)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/add_product<int:farm_id>') 
def add_product(farm_id):
    try:
        name = current_user.name
        farm = db.session.query(Farms).filter(Farms.id==farm_id).first()
    
        # rows=db.session.query(Products).filter(Products.)
        # rows = add_product(farm_id)
    
        return render_template('add_product.html' , farm = farm )    

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


#--Add product to products table
@app.route('/submit', methods=['POST'])
def submit():
    try:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
        farm_id        = request.form['farm_id']
        prod_category  = request.form['prod_category']
        prod_name      = request.form['prod_name']
        package        = request.form['package']
        unit_price     = request.form['unit_price']
        stock          = request.form['stock']
        event_datetime = formatted_datetime                
        uploaded_files = request.files.getlist('image_path')
        
        #item_folder = os.path.join("static/images", farm_id)
    #----------------------
    #    if not os.path.exists(item_folder):
    #      os.makedirs(item_folder)
    #      print(f"item folder '{farm}' created successfully.")
    #   else:
    #       print(f"User folder '{farm}'already exists.")
    #   saved_files = [] # emplty list/array to get list of data
        
    #--------------------------------
        uploaded_files = request.files.getlist('image_path')
        item_folder = os.path.join("static/New_images")
        if not os.path.exists(item_folder):
            os.makedirs(item_folder)
        for file in uploaded_files:
            if file and file.filename:  # Check if the file is valid
                file.save(os.path.join(item_folder, file.filename))
        # for file in uploaded_files:
        #          filename = file.filename
        #          if len(filename)>0 :
        #              file.save(os.path.join('static/New_images/'+filename))
        filename =file.filename
        products =Products(farm_id=farm_id, prod_category=prod_category, prod_name=prod_name, package=package, unit_price=unit_price, 
        filename =filename, stock=stock, event_datetime=event_datetime)
        db.session.add(products)
        db.session.commit()
        return "Record saved successfully"

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


#-----------update products data base table
@app.route('/update_product' , methods=['POST']) 
def update_product():  
    try:
        item_id=request.form['id']
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
        product=Products.query.filter_by(id=item_id).first()
        product.farm_id         = request.form['farm_id']
        product.prod_category   = request.form['prod_category']
        product.prod_name       = request.form['prod_name']
        product.package         = request.form['package']
        product.unit_price      = request.form['unit_price']
        #product.filename       = request.form['filename']
        product.stock           = request.form['stock']
        product.event_datetime  = formatted_datetime    
        db.session.commit()
        return 'data updated ok'

    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500


#--------function to edit and update products in products table 
@app.route('/edit_product/<int:item_id>') 
def edit_product(item_id):
    try:
        product=db.session.query(Products)\
        .filter(Products.id==item_id)\
        .first()
        return render_template('edit_product.html', item=product)
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500
 
@app.route('/delete_product/<int:item_id>') 
#@login_required
def delete_product(item_id):
    product = db.session.query(Products).filter_by(id=item_id).first()
    if product:
        db.session.delete(product)
        db.session.commit()
        return ('Product deleted sussfully')  
    else:
        return 'User not found', 404


#------Test prod-y-------List all products on "products page"-------visitors
@app.route('/prod_list')  
def prod_list():
    try:
        farms = db.session.query(Farms).all()
        #products=db.session.query(Products).all()
        
        products = db.session.query(Products.prod_category).distinct().all()

        prods = db.session.query(Products, Farms) \
            .order_by(Products.event_datetime.desc())\
            .join(Farms) \
            .all() 
        
        return render_template('products.html', prods=prods ,farms=farms, products=products )
    
    except Exception as e:
    # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500

    
    #------list all products ---------admin user
@app.route('/prod_list1/')  
def prod_list1():
    try:
        products = db.session.query(Products, Farms) \
            .join(Farms) \
            .all()
        if not products:    
            return jsonify({"message": "No data found"}), 404
        return render_template('prod_list.html', products=products)
        
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500

#------List farm products for owner -----------------
@app.route('/prod_list2/<int:farm_id><name>')  #farm products
def prod_list2(farm_id, name):
    try:
        name1=current_user.name
        products = db.session.query(Products, Farms) \
            .join(Farms) \
            .filter(Products.farm_id == farm_id) \
            .all()
        return render_template('prod_list.html', name=name, products=products)
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


#-------------Products list for selected farm ------------
@app.route('/prod_list_by_farm', methods=['GET', 'POST'])   
def prod_list_by_farm():
    try:
        Fx=request.form['options']
        prods=db.session.query(Products, Farms)\
            .join(Farms) \
            .filter(Products.farm_id==Fx) \
            .all()
        return render_template('prod_list_select.html', Fx=Fx, prods=prods)
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500

#-------------Products list for selected farm ------------
@app.route('/prod_list_by_products', methods=['GET', 'POST'])   
def prod_list_by_products():
    try:
        Fx=request.form['options']
        prods=db.session.query(Products, Farms)\
            .join(Farms) \
            .filter(Products.prod_category==Fx) \
            .all()
        return render_template('prod_list_select.html', Fx=Fx, prods=prods)
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/view_image/<int:item_id>') #Not used
def view_image(item_id):
    try:
        record = db.session.query(Products).filter(Products.id==item_id).first()
        photo = record.filename
        prod_name = record.prod_name
        return render_template('view_image.html', prod_name=prod_name, photo=photo )
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/house_page') #original fun
def house_page():
    return render_template('house_details.html', )


@app.route('/house_list_all') #original fun
def house_list_all():
    user=current_user
    try:    
        house = db.session.query(House).all()
        if not house:
            return jsonify({"message": "No data found"}), 404
        return render_template('view_house_adv.html', house = house)
        
    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/house_list') #original fun
def house_list():
    user=current_user.name
    try:    
        house = db.session.query(House).filter(House.owner==user).all()
        if not house:
            return jsonify({"message": "No data found"}), 404
        return render_template('view_house_adv.html', house = house)
        
    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


def allowed_file(filename): 
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/save_house1', methods=['GET', 'POST'])
def save_house1():
    
        #uploaded_files = request.files.getlist('image_path')
        file = request.files['file']

        # filename = secure_filename(file.filename)
        # filename = file.filename
        
        if file.filename == '':
            flash('No selected file')
            file.filename='default'
            # # return ('No file selected')
        
            # if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/New_images/' , filename))
            return ('file saved')

    
@app.route('/save_house2', methods=['GET', 'POST'])#active
def save_house2():
    
    try:
        daily_rent=request.form['daily_rent']
        ad_no =request.form['ad_no']
        ad_date =request.form['ad_date']
        house_type  =request.form['house_type']
        area =request.form['area']
        address =request.form['address']
        rooms=request.form['rooms']
        bathrooms=request.form['bathrooms']
        kitchen =request.form['kitchen']    =="False"
        pool =request.form['pool']          =="False"
        pool_kids=request.form['pool_kids'] =="False"
        aircon=request.form['aircon']       =="False"
        grill=request.form['grill']         =="False"
        
        owner  =request.form['owner']
        phone  =request.form['phone']
   
        uploaded_files = request.files.getlist('image_path')
    
        file = request.files['file']
        filename = secure_filename(file.filename)
        filename = file.filename
        if file.filename == '':
            flash('No selected file')
            file.filename='house_image'
        else :
            file.save(os.path.join('static/New_images/',filename))
            flash('File uploaded successfully')
            #return 'No file is selected !'
        
        if request.method == 'POST':
                 newHouse = House(daily_rent, ad_no,ad_date, house_type, area,address, rooms,bathrooms,kitchen,pool,pool_kids, 
                                 aircon,grill,owner, phone, filename ) 
                 db.session.add(newHouse)
                 db.session.commit()
        flash("Files uploaded successfully!")  # Flash success message         
        return redirect(url_for('add_house'))
    except Exception as e:
        #Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500
        return('error')


@app.route('/save_house3', methods=['GET', 'POST'])
def save_house3():
    try:
        daily_rent=request.form['daily_rent']
        ad_no =request.form['ad_no']
        ad_date =request.form['ad_date']
        house_type  =request.form['house_type']
        area =request.form['area']
        address =request.form['address']
        rooms=request.form['rooms']
        bathrooms=request.form['bathrooms']
        kitchen =request.form['kitchen']=='False'
        pool =request.form['pool']=="False"
        pool_kids=request.form['pool_kids']=="False"
        #rooms=request.form['rooms']
        aircon=request.form['aircon']=="False"
        grill=request.form['grill']=="False"
        owner  =request.form['owner']
        phone  =request.form['phone']
        
#        uploaded_files = request.files.getlist('image_path')
        files = request.files.getlist('images')

        image_paths = []
        for file in files:
            if file.filename == '':
                return 'No selected file'
            if file:
                filename = file.filename
                file_path = os.path.join('static/New_images/', filename)
                file.save(file_path)
                image_paths.append(file_path)
 
                newHouse = House(daily_rent,ad_no,ad_date,house_type,area,address,rooms,
                                bathrooms,kitchen,pool,pool_kids,aircon,grill,owner,phone, 
                                filename )
                 
            # db.session.add(newHouse)
            # db.session.commit()
            
        return(filename) 
        
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500

@app.route('/add_house')
def add_house():
    try:
        rows = db.session.query(House).count()
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H%M')
        #adv_no ='ADV'+'-'+ str(rows+1)
        adv = 100 + rows +1
        ad_no=adv        
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d ")
        ad_date=current_date
        user = current_user.name
        house=db.session.query(House).filter(House.owner==current_user.name)
        user =db.session.query(Users)\
            .filter(Users.name==user)\
            .first()   
        
        return render_template('add_house.html', house=house, user=user, ad_no=ad_no, ad_date =ad_date )    
    
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/delete_house/<int:house_id>') 
def delete_house(house_id):
    house=db.session.query(House).filter(House.id==house_id).first()
    if house:
        db.session.delete(house)
        db.session.commit()
        return redirect(url_for('house_list'))
       # return ('House delete record successfully')
    else:
        return 'User not found', 404


@app.route('/add_store')
def add_store():
    try:
        user = current_user.name
        store=db.session.query(Stores).filter(Stores.user_id==Users.id)
        user =db.session.query(Users)\
            .filter(Users.name==user)\
            .filter(Users.role=='business1')\
            .first()   
        return render_template('add_store.html', store=store, user=user)    

    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/delete_store/<int:store_id>') 
def delete_store(store_id):
    store=db.session.query(Stores).filter(Stores.id==store_id).first()
    if store:
        db.session.delete(store)
        db.session.commit()
        return ('Delete record successfully')
    else:
        return 'User not found', 404


@app.route('/edit_store/<int:st_id>')
def edit_store(st_id):
    try:
        user = current_user.name
        store=db.session.query(Stores).filter(Stores.id==st_id).first()
        user =db.session.query(Users)\
            .filter(Users.name==user)\
            .filter(Users.role=='business1')\
            .first()   
        return render_template('edit_store.html', store=store, user=user)    
    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500


@app.route('/update_store', methods=['POST'])
def update_store(): 
    try:    
        id=request.form['id']
        store=db.session.query(Stores).filter(Stores.id==id).first()
      
        store.user_id =request.form['user_id']
        store.store_name =request.form['store_name']
        store.activity =request.form['activity']
        store.phone1 =request.form['phone1']
        store.phone2 =request.form['phone2']
        store.address =request.form['address']
       # store.filename =request.form['filename']
        store.adv_class =request.form['adv_class']
        # Check if the post request has the file part
        if 'imageUpload' not in request.files:
            return redirect(request.url)

        file = request.files['imageUpload']

        # If a file is submitted, save it
        if file and file.filename != '':
            file_path = os.path.join('static/New_images/'+file.filename)
            file.save(file_path)  # Save the new image
            # Here you can also implement logic to update the database with the new file name

        filename =file.filename
        store.filename =filename  

        db.session.commit()
        return ('Store record modified ok')

    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500


@app.route('/save_store', methods=['GET', 'POST'])
def save_store():
    try:
        store_name =request.form['store_name']
        user_id =request.form['user_id']
        phone1  =request.form['phone1']
        phone2  =request.form['phone2']
        address =request.form['address']
        activity =request.form['activity']
        adv_class=request.form['adv_class']
        #uploaded_files = request.files.getlist('image_path')

        file = request.files['file']
        filename = secure_filename(file.filename)
        filename = file.filename
        if file.filename == '':
            flash('No selected file')
            file.filename='store_image'
        else :
            file.save(os.path.join('static/New_images/',filename))
            flash('File uploaded successfully')

        # file = request.files['file']
        # if file!="":
        #     filename = file.filename
        #     #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     file.save(os.path.join('static/New_images/'+filename))
        #     flash('File uploaded successfully')


        if request.method == 'POST':
            newStore = Stores( user_id, store_name, activity, phone1, phone2, address, filename, adv_class)
            db.session.add(newStore)
            db.session.commit()
        return 'Store saved successfully'
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/show_store_adv')
def show_store_adv():
    try:
        user = current_user.name
        owner=db.session.query(Users).filter(Users.name==user).first()
        store = db.session.query(Stores)\
            .filter(Stores.user_id==owner.id)\
            .all()
        if not store:
            return jsonify({"message": "No activity selected"}), 404
        return render_template('view_store_adv1.html', store=store, owner=owner)    
    
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/show_store_details/<int:store_id>')
def show_store_details(store_id):
    try: 
        store = db.session.query(Stores)\
        .filter(Stores.id==store_id)\
        .first()
        if not store:
            return jsonify({"message": "No activity selected"}), 404
        return render_template('page-2.html', store=store)    
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/store_list_by_activity' , methods=['GET', 'POST'])
def store_list_by_activity():
    #user = current_user.name
    try:
        activity = request.form['activity']
        if not activity:
            return jsonify({"message": "No activity selected"}), 404
        
        store = db.session.query(Stores)\
            .filter(Stores.activity==activity)\
            .all()
        if not store:
            return jsonify({"message": "No store available "}), 404
        return render_template('page-3.html', store=store)    
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/store_list_all')
def store_list_all():
    try:
        store = db.session.query(Stores, Users)\
        .join(Users, Stores.user_id==Users.id)\
        .all()
    
        if not store:
            return jsonify({"message": "No data found"}), 404
        return render_template('stores_list_all.html', store = store)    

    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500
    

@app.route('/add_farm')
def add_farm():
    try:
        user = current_user.name
        user=db.session.query(Users)\
            .filter(Users.name==user)\
            .filter(Users.role=='owner')\
            .first()   
    
        return render_template('add_farm.html', owner=user)    
        #else: return ('not authorized')

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/edit_farm/<int:farm_id>') 
def edit_farm(farm_id):
    try:
        user=db.session.query(Farms).filter(Farms.id==farm_id).first()
        owner=db.session.query(Users).filter(Users.id==user.user_id).first()
        return render_template('edit_farm.html', user=user, owner=owner)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/delete_farm/<int:farm_id>') 
@login_required
def delete_farm(farm_id):
    farm=db.session.query(Farms).filter(Farms.id==farm_id).first()
    if farm:
        db.session.delete(farm)
        db.session.commit()
        return ('Delete record successfully')
    else:
        return 'User not found', 404


@app.route('/farm_list_all') #original fun
def farm_list_all():
    try:    
        farms = db.session.query(Farms).all()
        if not farms:
            return jsonify({"message": "No data found"}), 404
        return render_template('farms_list_all.html', farms = farms)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/farm_list_admin') #original fun
def farm_list_admin():
    try:
        #farms = db.session.query(table1, table2).join(table2).all()
        farms = db.session.query(Farms, Users) \
            .join(Users) \
            .filter(Users.role=='owner')\
            .all()
        if not farms :
               return jsonify({"message": "No data found"}), 404
        return render_template('farm_list.html', farms = farms)
    
    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500

  #-------------------Edit/add Farm Record------------------------   
@app.route('/add_new_farm', methods=['POST'])
def add_new_farm():
    try:
        farm_name   =request.form['farm_name']
        product_type=request.form['product_type']
        owner_id    =request.form['owner_id']
        phone       =request.form['phone']
        email       =request.form['email']
        address1    =request.form['address1']
        address2    =request.form['address2']
        
        newFarm= Farms( farm_name, product_type, owner_id, phone, email, address1, address2)
        
        COUNT=db.session.query(Farms)\
            .filter(Farms.farm_name=='%'+farm_name+'%')\
            .count()
        db.session.add(newFarm)
        db.session.commit()
        
        if COUNT >0 :
            return ('farm name exists! please select another name ') 
        else:
            db.session.add(newFarm)
            db.session.commit()
        return 'Farm saved successfully'
    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500
              
@app.route('/update_farm', methods=['POST'])
#@login_required
def update_farm():
    try:    
        id=request.form['id']
        farm=db.session.query(Farms).filter(Farms.id==id).first()
        farm.id      =request.form['id']
        farm.name    =request.form['name']
        farm.user_id =request.form['user_id']
        farm.phone   =request.form['phone']
        farm.email   =request.form['email']
        farm.address1 =request.form['address1']
        farm.address2 =request.form['address2']
    
        db.session.commit()
        return ('Farm record modified ok')
    
    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500


#--list for all cart items - admin
@app.route('/cart_items_list') #---ok
def cart_items_list():
    try:
        rows = db.session.query(Cart_items, Products, Farms, Users) \
            .join(Products, Cart_items.product_id==Products.id) \
            .join(Farms, Cart_items.farm_id==Farms.id) \
            .join(Users, Cart_items.user_id==Users.id) \
            .all()
        if not rows:
            return jsonify({"message": "Cart is empty"}), 404
        
        return render_template('cart_items_list.html', rows=rows)
        #return('ok')
    
    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


#--list for cart items - buyer - to be cleared after PO is creation
@app.route('/cart_items_list1') #-- ok
def cart_items_list1():
    try:
        username=current_user.name

        po_ava=db.session.query(Orders)\
            .filter(Orders.order_user==username)\
            .first()

        user=db.session.query(Users)\
            .filter(Users.name== username)\
            .first() 

        farms = db.session.query(Farms).all()
        
        items = db.session.query(Cart_items, Farms, Products) \
            .join(Farms, Cart_items.farm_id==Farms.id ) \
            .join(Products, Cart_items.product_id==Products.id) \
            .filter(Cart_items.user_id == user.id)\
            .filter(Cart_items.ordered == False)\
            .all()
        if not items:
            return jsonify({"message": "Cart is empty"}), 404
            
        return render_template('cart_items_list1.html',  po_ava=po_ava, items=items, farms=farms, user=user)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500
                       
           
#---cart items for farm owners in customers cart
@app.route('/cart_items_list2/<farm_id>') #-- ok
def cart_items_list2(farm_id):
    try:
        buyers = db.session.query(Users)\
            .filter(Users.role=='customer').all()

        farms = db.session.query(Farms)\
            .filter(Farms.id==farm_id)\
            .first()
        
        items = db.session.query(Cart_items, Products, Users) \
                .join( Products) \
                .join( Users) \
                .filter(Cart_items.farm_id==Farms.id)\
                .all()
        if not items:
            return jsonify({"message": "Cart empty ... No data found"}), 404
        
        return render_template('cart_items_list2.html', items=items, buyers=buyers , farms=farms)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500
    
#???
@app.route('/add_to_cart/<int:item_id>', methods=['GET', 'POST'])
def add_to_cart(item_id):
    try:
        products = db.session.query(Products) \
            .join(Farms, Products.farm_id==Farms.id)\
            .filter(Products.id==item_id)\
            .first()
        
        farms=db.session.query(Farms)\
            .filter(Farms.id==products.farm_id)\
            .first()
        
        buyers=db.session.query(Users).filter(Users.name == current_user.name).first()

        return render_template('add_to_cart.html', products=products, buyers=buyers, farms=farms)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


#--------add new items to cart table ?
@app.route('/add_to_cartY' , methods=['GET', 'POST']) #OK
def add_to_cartY():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
    try:
        buyer_id      = request.form['buyer_id']
        farm_id       = request.form['farm_id']
        product_id    = request.form['id']
        quantity      = request.form['quantity']
        package       = request.form['package']
        unit_price    = request.form['unit_price']
        filename1     = request.form['filename']
        ordered  = False
        event_datetime =formatted_datetime
        
        cart_item = Cart_items(buyer_id, farm_id, product_id, quantity,  package, 
                               unit_price, filename1, event_datetime, ordered)
        db.session.add(cart_item)
        db.session.commit()
 
        return ('item saved successfully ')
    
    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500


@app.route('/edit_cart/<int:item_id>')
#@login_required
def edit_cart(item_id):
    try:    
        # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
        # event_datetime=formatted_datetime
        items = db.session.query(Cart_items)\
            .filter(Cart_items.id == item_id)\
            .first()

        buyers=db.session.query(Users).filter(Users.id==items.user_id).first()      

        products = db.session.query(Products)\
            .filter(Products.id == items.product_id)\
            .first()

        farms = db.session.query(Farms)\
            .filter(Farms.id==items.farm_id)\
            .first()
        
        owners = db.session.query(Users)\
            .filter(Users.id==farms.user_id)\
            .first()
        
        return render_template('edit_cart.html', owners=owners, items=items, products=products, users=buyers, farms=farms)
    
    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


#---update existing items in table
@app.route('/update_cart' , methods=['GET', 'POST']) 
def update_cart():  
    try:
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
        # event_datetime=formatted_datetime
        
        id=request.form['id']
        items=db.session.query(Cart_items).filter(Cart_items.id==id).first()
        
        items.buyer_id        = request.form['buyer_id']
        items.farm_id         = request.form['farm_id']
        items.product_id      = request.form['product_id']
        items.quantity        = request.form['quantity']
        items.package         = request.form['package']
        items.unit_price      = request.form['unit_price']
        items.filename        = request.form['filename']
        items.event_datetime  = formatted_datetime    

        db.session.commit()
        return ('Cart items updated successfully ')
    
    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500


@app.route('/delete_item_from_cart/<int:item_id>') 
def delete_item_from_cart(item_id):
    item = db.session.query(Cart_items).filter_by(id=item_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return ('item deleted sussfully')  # Redirect to a list of users
    else:
        return 'User not found', 404


def clear_cart(item_id):
    try:
        item = db.session.query(Cart_items).filter_by(id=item_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return ('item deleted sussfully')  # Redirect to a list of users
        else:
            return 'User not found', 404

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


#create hard copy of PO
@app.route('/create_purchase_order', methods =['GET', 'POST']) 
def create_purchase_order():
    try:
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
        event_datetime=formatted_datetime
        farm = request.form['item-dropdown'] #selected farm
        buyer= request.form['user']
        if farm:
            rows = db.session.query(Orders).count()
            current_date = datetime.now().strftime('%Y%m%d')
            current_time = datetime.now().strftime('%H%M')
            order_no ='PO'+'-'+ current_time +'-'+ str(rows+1)
            order_date = formatted_datetime

            buyers = db.session.query(Users)\
                .filter(Users.name==buyer)\
                .first() 
                
            farms = db.session.query(Farms)\
                .filter(Farms.farm_name==farm)\
                .first() 
            
            products = db.session.query(Products)\
                .all() 
            
            items = db.session.query(Cart_items, Products) \
                .join(Products, Cart_items.product_id==Products.id) \
                .filter(Cart_items.farm_id==farms.id)\
                .filter(Cart_items.user_id==buyers.id)\
                .all()
#create orders table
        new_order = Orders(
            order_no   = order_no,
            order_date = order_date,
            order_farm = farms.farm_name,
            farm_phone = farms.phone,
            order_user = buyers.name,
            user_phone = buyers.phone,
            user_email = buyers.email,
            status='Pending',
            event_datetime=current_datetime,
            items=[]  # Pass an empty list or the actual items here
    )
        db.session.add(new_order)
        db.session.commit()  # Commit to get the order ID

# creates order items table
        for item, product in items:
            # total_price = item['quantity'] * item['unit_price']
            new_order_item = Order_Items(
                order_id = new_order.id, 
                order_no = order_no,
                item_id = product.id,
                item_name = product.prod_category+'-'+product.prod_name,
                quantity= item.quantity,
                unit_price= item.unit_price,
                total_price= item.unit_price * item.quantity
                )
            db.session.add(new_order_item)
            clear_cart(item.id) #remove items from cart
        db.session.commit()
        print(f"Order {order_no} created with {len(items)} items.")
        return redirect(url_for('prod_list'))

        #return render_template('purchase_order.html', farms=farms, buyers=buyers, new_order=new_order, items=items)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


#---update status for existing order update_order_status
@app.route('/update_order_status' , methods=['GET', 'POST']) 
def update_order_status():  
    try:
        # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
        # event_datetime=formatted_datetime
        id=request.form['id']
        orders=db.session.query(Orders).filter(Orders.id==id).first()
        
        orders.order_no    = request.form['order_no']
        orders.order_date  = request.form['order_date']
        orders.order_farm  = request.form['order_farm']
        orders.farm_phone =  request.form['farm_phone']
        orders.order_user  = request.form['order_user']
        orders.user_phone  = request.form['user_phone']
        orders.user_email  = request.form['user_email']
        orders.status  = request.form['status']
        #event_datetime = current_datetime
        
        db.session.commit()

        if orders.status =="closed":
            event_datetime = current_datetime
            return redirect(url_for('update_stock', order_id=id))
        else:
            return('Status update successfully')
        
    except SQLAlchemyError as e:
        db.session.rollback()  # Roll back the session on error
        return jsonify({"error": str(e)}), 500


@app.route('/update_stock/<int:order_id>')
def update_stock(order_id):  
    try:    
        items = db.session.query(Order_Items).filter(Order_Items.order_id==order_id).all()
        
        for item in items:
            product = Products.query.get_or_404(item.item_id)
            if product.stock >= item.quantity:    
                # Update the stock
                product.stock -= item.quantity
            else:
                return f"Insufficient stock for product ", 400
        db.session.commit()
        return "Purchase order closed and stock updated"
    
    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/edit_order/<int:order_id>')
def edit_order(order_id):
    try:
        order = db.session.query(Orders)\
        .filter(Orders.id == order_id)\
        .first()
        if order:        
            return render_template('edit_purchase_order_status.html', order=order)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500
    

@app.route('/view_order/<int:order_id>') #saved PO in database
def view_order(order_id):
    try:
        order = db.session.query(Orders)\
            .filter(Orders.id == order_id)\
            .first() 
        
        owner=db.session.query(Users)\
            .filter(Users.name==current_user.name)\
            .first()

        buyers=db.session.query(Users)\
            .filter(Users.name ==order.order_user)\
            .first()

        items = db.session.query(Order_Items, Products) \
            .join(Products, Order_Items.item_id==Products.id) \
            .filter(Order_Items.order_id==order_id) \
            .all()
        
        return render_template('purchase_order_new.html', row=order, items=items , owner=owner, buyers=buyers)
        #return('ok')

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/view_orders_list/<user_name>' )
def view_orders_list(user_name):
    try:
        order=db.session.query(Orders)\
            .filter(Orders.order_user==user_name)\
            .filter(Orders.status !='closed')\
            .all()
        if not order:
            return jsonify({"message": "No data found"}), 404
        
        return render_template('orders_list.html', s=order)

    except Exception as e:
       # Handle any exceptions that occur
       return jsonify({"error": str(e)}), 500


@app.route('/view_orders_list_F/<int:farm_id>') #for farm owners
def view_orders_list_F(farm_id):
    farm_id='2'
    try:
        farm=db.session.query(Farms).filter(Farms.id==farm_id).first()
        order=db.session.query(Orders)\
            .filter(Orders.order_farm == farm.farm_name)\
            .filter(Orders.status !='closed')\
            .all()

        if not order:
            return jsonify({"message": "No data found"}), 404

        return render_template('orders_list.html', s=order)

    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500


@app.route('/delete_order/<int:order_id>', methods=['GET', 'POST']) 
def delete_order(order_id):
    order=db.session.query(Orders).filter(Orders.id==order_id).first()
    db.session.delete(order)
    db.session.commit()
    return 'order deleted'


#----------------Galary -------
@app.route('/image_area')
def image_area():
    return render_template('image_area.html')
  
@app.route('/view_gallery_images')
def view_gallery_images():
    image_folder = 'static/images' 
    image_files = os.listdir(image_folder)
    return render_template('view_gallery.html', image_files=image_files)

@app.route('/images/<path:filename>')
def get_image(filename):
    image_folder ='static/images-prod/'  
    return send_from_directory(image_folder, filename)

@app.route('/map-page')
def map():
    return render_template('map-page.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/support')
def support():
    return render_template ('support.html')

@app.route('/user_guide_1')
def user_guide_1():
    return render_template ('user-guide-1a.html')

@app.route('/user_guide_2')
def user_guide_2():
    return render_template ('user-guide-2a.html')

@app.route('/user_guide_3')
def user_guide_3():
    return render_template ('user-guide-3a.html')

@app.route('/user_guide_4')
def user_guide_4():
    return render_template ('user-guide-4a.html')

@app.route('/user_guide_5')
def user_guide_5():
    return render_template ('user-guide-5a.html')

@app.route('/user_guide_6')
def user_guide_6():
    return render_template ('user-guide-6aa.html')


@app.route('/user_guide_7')
def user_guide_7():
    return render_template ('user-guide-7.html')

@app.route('/user_guide_8')
def user_guide_8():
    return render_template ('user-guide-8.html')

@app.route('/user_guide_9')
def user_guide_9():
    return render_template ('user-guide-9.html')

# if __name__ == '__main__':
#         app.run(debug=True)

#  if name == "__main__":
#       app.run(debug=true)

if __name__ == "__main__":
      app.run(host="127.0.0.1", port=5000, debug=True)