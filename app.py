from flask import Flask, request, render_template, redirect, flash, session, g
from models import db, connect_db, Customer

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = connect_db()

    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# important to configure in order to not get an error
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///customers'
app.config['SQLALCHEMY_TRACK_MODIFCATIONS'] = False

# after connfiguration call connect_db from models python file
connect_db(app)

@app.route('/customers')
def list_customers():
    """Shows list of all pets in db"""
    
    customers = Customer.query.all()
    return render_template("customers.html", customers=customers)

@app.route('/customers', methods=["POST"])
def create_customer():
    name = request.form["name"]
    address = request.form["address"]

    new_customer = Customer(name=name, address=address)
    db.session.add(new_customer)
    db.session.commit()

    return redirect(f'/{new_customer.id}')

@app.route('/')
def home():
    """Shows Home page"""
    
    return render_template("base.html")

@app.route('/<int:customer_id>')
def show_cust(customer_id):
    """Show Details about a customer"""
    customer = Customer.query.get_or_404(customer_id)
    return render_template("details.html", customer=customer)

@app.route("/communities/<community_id>")
def show_communities(community_id):
    Customer.get_by_community(community_id)
    return render_template("community.html", customers=customers, community=community_id)
