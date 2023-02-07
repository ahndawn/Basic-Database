
from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db,  connect_db, Customer, Department, Employee, get_directory, get_directory_join, get_directory_join_class, get_directory_all_join, Project, EmployeeProject
from forms import AddCustomerForm, EmployeeForm, UserForm 
# CustomerSearchForm, NewCustomerForm, EditCustomerInfoForm, EditContactInfoForm, EditAddressInfoForm, JobEntryForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///employees_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "chickenzarecool21837"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def home():
    """Shows Home page"""
    
    return render_template("home.html")
# Customers routes
@app.route('/customers')
def list_customers():
    """Shows list of all customers in db"""
    customers = Customer.query.all()
    return render_template("customers.html", customers=customers)

@app.route("/customers/add", methods = ["GET", "POST"])
def add_customer():
    """Add Customer Form; handle adding"""
    form = AddCustomerForm()
    if form.validate_on_submit():
        last_name = form.last_name.data
        first_name = form.first_name.data
        phone_number = form.phone_number.data
        email = form.email.data
        address_line_1 = form.address_line_1.data
        address_line_2 = form.address_line_2.data
        city = form.city.data
        state= form.state.data
        postal= form.postal.data
        community = form.community.data
        sub_community = form.sub_community
        customer = Customer(last_name=last_name, first_name=first_name, phone_number=phone_number, email=email, address_line_1=address_line_1, address_line_2=address_line_2, city=city, state=state, postal=postal, community=community, sub_community=sub_community)
        db.session.add(customer)
        db.session.commit()
        flash(f"Added {last_name}")
        return redirect("/customers")
    else:
        return render_template(
            "add_customer_form.html", form=form)

@app.route('/<int:customer_id>')
def show_cust(customer_id):
    """Show Details about a customer"""
    customer = Customer.query.get_or_404(customer_id)
    return render_template("details.html", customer=customer)


# Phones route
@app.route('/phones')
def list_phones():
    """Renders directory of employees and phone numbers  (from dept)"""
    emps = Employee.query.all()
    return render_template('phones.html', emps=emps)


# communities
@app.route("/communities/<community_id>")
def show_communities(community_id):
    Customer.get_by_community(community_id)
    return render_template("community.html", customers=customers, community=community_id)

# employees routes
@app.route('/employees/new', methods = ["GET", "POST"])
def add_employee():
    form = EmployeeForm()
    depts = db.session.query(Department.dept_code, Department.dept_name)
    form.dept_code.choices = depts
    if form.validate_on_submit():
        name = form.name.data
        state = form.state.data
        dept_code = form.dept_code.data
        emp = Employee(name="name", state="state", dept_code="dept_code")
        db.session.add(emp)
        db.session.commit()
        return redirect('/phones')
    else:
        return render_template('add_employee_form.html', form = form)

# edit employees
@app.route('/employees/<int:id>/edit', methods=["GET", "POST"])
def edit_employee(id):
    emp = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=emp)
    depts = db.session.query(Department.dept_code, Department.dept_name)
    form.dept_code.choices = depts

    if form.validate_on_submit():
        emp.name = form.name.data
        emp.state = form.state.data
        emp.dept_code = form.dept_code.data
        db.session.commit()
        return redirect('/phones')
    else:
        return render_template("edit_employee_form.html", form=form)

###########################################
# User information
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect('/tweets')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['user_id'] = user.id
            return redirect('/tweets')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')

####################
# SCHEDULE


