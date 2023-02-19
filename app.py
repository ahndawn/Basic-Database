from flask import Flask, request, render_template,  redirect, flash, session, url_for, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Call, Email, Customer, PhoneNumber, Address, Crew, Job, Community, SubCommunity, Employee, Department, User
from forms import EmployeeForm, CallForm, UserAddForm, UserEditForm, LoginForm, CustomerSearchForm, NewCustomerForm
# CustomerSearchForm, NewCustomerForm, EditCustomerInfoForm, EditContactInfoForm, EditAddressInfoForm, JobEntryForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func, or_
import parsing

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mwc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "chickenzarecool21837"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

with app.test_request_context():    
    connect_db(app)
    db.create_all()

@app.route('/')
def home():
    """Shows Home page"""
    
    return render_template("base.html")
# Customers routes
@app.route('/customers')
def list_customers():
    """Shows list of all customers in db"""
    customers = Customer.query.all()
    return render_template("customers.html", customers=customers)

# Search customers
@app.route('/search', methods=['GET', 'POST'])
def search():
    form = CustomerSearchForm()
    if form.validate_on_submit():
        searchResults = []
        search_terms = {
            'name': form.customer_name.data,
            'number': form.customer_number.data,
            'address': form.customer_address.data
        }
        search_term = ''
        if search_terms['name'] is not None and search_terms['name'] != '':
            search_term += search_terms['name']
        if search_terms['number'] is not None and search_terms['number'] != '':
            if len(search_term) > 0:
                search_term += ', '
            search_term += search_terms['number']
        if search_terms['address'] is not None and search_terms['address'] != '':
            if len(search_term) > 0:
                search_term += ', '
            search_term += search_terms['address']
        searchResults = customer_query(search_terms)
        flash('{} Results for: {}'.format(len(searchResults), search_term))
        #return redirect('/')
        return render_template('search.html', title='Search Results - MWC-DB', form=form, search_results=searchResults)
    return render_template('search.html', title='Customer Search - MWC-DB', form=form)

#############################################################
#Communities functions
def get_sub_communities(community_id):
    community = db.session.query(Community).get(community_id)
    sub_communities = community.subcommunities.order_by(SubCommunity.name)

    return sub_communities


def get_sub_communities_by_name(community_name):
    community = db.session.query(Community).filter(Community.name == community_name).first()
    if community is not None:
        sub_communities = community.subcommunities.order_by(SubCommunity.name)
        return sub_communities
    else:
        return None

def get_all_communities():
    communities = db.session.query(Community).order_by(Community.name).all()

    return communities
def get_community_by_name(community_name):
    community = db.session.query(Community).filter(Community.name == community_name).first()

    return community

def get_new_customer_id():
    customer_id = db.session.query(func.max(Customer.id)).first()[0]
    return customer_id

#####################################################
def number_cleanup(phone_number):
    search_number = phone_number
    search_number = search_number.replace('-', '')
    search_number = search_number.replace('+', '')



    if len(search_number) == 7:
        search_number = search_number[:3] + '-' + search_number[3:]
    elif len(search_number) == 4:
        pass
    elif len(search_number) > 4:
        if len(search_number) == 11:
            search_number = search_number[1:]
        search_number = search_number[:3] + '-' + search_number[3:6] + '-' + search_number[6:]

    return search_number

def customer_query(search_terms):

    db.create_all()

    filters = []
    joins = [Customer.addresses]

    if search_terms['name'] is not None and search_terms['name'] != '':
        filters.append(or_(Customer.last_name.like('%' + search_terms['name'] + '%'), Customer.last_name2.like(
            '%' + search_terms['name'] + '%')))

    if search_terms['number'] is not None and search_terms['number'] != '':
        search_number = number_cleanup(search_terms['number'])
        joins.append(Customer.numbers)
        filters.append(and_(
                PhoneNumber.number.contains(search_number)))  # , Customer.id == PhoneNumber.customer_id

    if search_terms['address'] is not None and search_terms['address'] != '':
        # joins.append(Customer.addresses)
        filters.append(and_(Address.address_ln1.like(
             '%' + search_terms['address'] + '%')))  # , Customer.id == Address.customer_id

    print('---------------')
    print('Customer Query For: ')
    print(search_terms)
    print('---------------')

    matches = db.session.query(Customer).join(*joins).filter(and_(*filters)).order_by(Customer.last_name)

    customers = []
    for customer in matches:

        customer_info = parsing.customer_parse(customer)

        customer_info['addresses'] = []
        for address in customer.addresses:
            address_info = parsing.address_parse(address)
            customer_info['addresses'].append(address_info)

        customers.append(customer_info)

    return customers
################################################################
def submit_new_customer(new_customer_form):
    form = new_customer_form

    new_customer = Customer()

    # ---------- Customer Info ----------

    # last name
    new_customer.last_name = form.customer_info.last_name.data

    # last name 2
    # if form has a second last name
    if form.customer_info.last_name2.data:
        # store it
        new_customer.last_name2 = form.customer_info.last_name2.data
    else:
        # if form does not have a second last name, duplicate first last name (they have the same last name)
        new_customer.last_name2 = form.customer_info.last_name.data

    # first name
    if form.customer_info.first_name.data:
        new_customer.first_name = form.customer_info.first_name.data

    # first name 2
    if form.customer_info.first_name2.data:
        new_customer.first_name2 = form.customer_info.first_name2.data

    # referral
    if form.customer_info.referral.data:
        new_customer.referral = form.customer_info.referral.data

    # customer since
    if form.customer_info.customer_since.data:
        new_customer.customer_since = form.customer_info.customer_since.data

    db.session.add(new_customer)
    db.session.flush()

    # ---------- Phone Numbers ----------
    for number in form.phone_numbers.entries:
        if number.form.number.data:
            new_number = PhoneNumber()
            new_number.number = number.form.number.data
            if number.form.number_type.data:
                new_number.number_type = number.form.number_type.data
            new_number.customer_id = new_customer.id
            # new_customer.numbers.append(new_number)
            db.session.add(new_number)
            db.session.flush()

    # ---------- Emails ----------
    for email in form.emails.entries:
        if email.form.email.data:
            new_email = Email()
            new_email.email = email.form.email.data
            new_email.customer_id = new_customer.id
            # new_customer.emails.append(new_email)
            db.session.add(new_email)
            db.session.flush()

    # ---------- Addresses ----------
    for address in form.addresses.entries:
        new_address = Address()

        # street address
        new_address.address_ln1 = address.form.address_ln1.data

        # suite / apt #
        if address.form.address_ln2.data:
            new_address.address_ln2 = address.form.address_ln2.data

        # city
        city_shortcuts = [('wpb', 'West Palm Beach'), ('pbg', 'Palm Beach Gardens'), ('rpb', 'Royal Palm Beach'),
                          ('br', 'Boca Raton'), ('bb', 'Boynton Beach'), ('db', 'Delray Beach'), ('pb', 'Palm Beach'),
                          ('npb', 'North Palm Beach'), ('lw', 'Lake Worth'), ('ga', 'Greenacres'), ('j', 'Jupiter'), ('rb', 'Riviera Beach'), ('lox', 'Loxahatchee')]
        shortcut_flag = False
        for shortcut in city_shortcuts:
            if address.form.city.data.lower() == shortcut[0]:
                new_address.city = shortcut[1]
                shortcut_flag = True
                break
        if shortcut_flag is False:
            new_address.city = address.form.city.data

        # zip
        new_address.zip = address.form.zip.data

        # community
        if address.form.community.data != '---':
            # existing community
            if address.form.community.data != 'New Community':
                community = get_community_by_name(address.form.community.data)
                new_address.community_id = community.id
            # new community
            elif address.form.community.data == 'New Community' and address.form.new_community.data != '' and address.form.new_community.data is not None:
                print('----- New Community Detected -----')
                community = Community()
                community.name = address.form.new_community.data
                print('----- New Community Made -----')
                db.session.add(community)
                print('----- New Community Added -----')
                db.session.flush()
                print('----- New Community DB Flushed -----')
                new_address.community_id = community.id
                print('----- New Community Attached to New Address -----')

            # sub community
            if address.form.sub_community.data != '---':
                # existing sub-community
                if address.form.sub_community.data != 'New Sub Community':
                    sub_community = community.subcommunities.filter(
                        SubCommunity.name == address.form.sub_community.data).first()
                    new_address.sub_community_id = sub_community.id
                # new sub-community
                elif address.form.sub_community.data == 'New Sub Community' and address.form.new_sub_community.data != '' and address.form.new_sub_community.data is not None:
                    print('----- New Sub Community Detected -----')
                    sub_community = SubCommunity()
                    sub_community.name = address.form.new_sub_community.data
                    sub_community.community_id = community.id
                    print('----- New Sub Community Made -----')
                    db.session.add(sub_community)
                    print('----- New Sub Community Added -----')
                    db.session.flush()
                    print('----- New Sub Community DB Flush -----')
                    new_address.sub_community_id = sub_community.id
                    print('----- New Sub Community Attached to New Address -----')

        # billing preference
        if address.form.billing.data != 'Leave Bill':
            new_address.billing = address.form.billing.data

        # billing type
        new_address.billing_type = address.form.billing_type.data

        new_address.customer_id = new_customer.id
        # new_customer.addresses.append(new_address)
        db.session.add(new_address)
        db.session.flush()

    db.session.flush()
    db.session.commit()

    return new_customer


def commit_db_session():
    db.session.commit()

@app.route("/customers/add", methods = ["GET", "POST"])
def add_customer():
    """Add Customer Form; handle adding"""
    form = NewCustomerForm()
    for address in form.addresses.entries:
        communities = get_all_communities()

        community_choices = ['---', 'New Community', '---']
        sub_community_choices = ['---']

        for comm in communities:
            community_choices.append(comm.name)
        address.form.community.choices = community_choices

        if address.form.community.data != '---':
            sub_community_choices.append('New Sub Community')
            sub_community_choices.append('---')
            if address.form.community.data != 'New Community':
                community = address.form.community.data
                sub_communities = get_sub_communities_by_name(community)
                if sub_communities:
                    for subcomm in sub_communities:
                        sub_community_choices.append(subcomm.name)

        address.form.sub_community.choices = sub_community_choices

    if form.submit_new_customer.data and form.validate():
        print('success')
        submit_new_customer(form)
        print('new id: {}'.format(get_new_customer_id()))
        return redirect(f'/customers')
    elif not form.validate_on_submit():
        print(form.errors)
        print('comm: {}'.format(form.addresses.entries[0].community.data))
        print('subcomm: {}'.format(form.addresses.entries[0].sub_community.data))
        print(form.addresses.entries[0].community.choices)

    return render_template(
                "add_customer_form.html", title='New Customer - MWC-DB', form=form)

#################################################################
@app.route('/<int:customer_id>')
def show_cust(customer_id):
    """Show Details about a customer"""
    customer = Customer.query.get_or_404(customer_id)
    return render_template("details.html", customer=customer)
##################################################################################


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


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


##########
#User Profile page
@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "/static/images/default-pic.png"
            user.header_image_url = form.header_image_url.data or "/static/images/warbler-hero.jpg"
            user.bio = form.bio.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

#################################
#Call log
@app.route('/calls/add', methods=["GET", "POST"])
def add_call():
    form = CallForm()
    if form.validate_on_submit():
        date = form.date.data
        time = form.time.data
        customer_name = form.customer_name.data
        phone_number = form.phone_number.data
        community = form.community.data
        area = form.area.data
        address = form.address.data
        customer_type = form.customer_type.data
        call_type = form.call_type.data
        comments = form.comments.data
        received_type = form.received_type.data
        response = form.response.data
        card = form.card.data
        database = form.database.data
        resolved = form.resolved.data
        booked = form.booked.data
        call = Call(date=date, time=time, customer_name=customer_name, phone_number=phone_number, community=community, area=area, address=address, customer_type=customer_type, call_type=call_type, comments=comments, received_type=received_type, response=response, card=card, database=database, resolved=resolved, booked=booked)
        db.session.add(call)
        db.session.commit()
        flash(f"Added {customer_name}")
        return redirect('/calls')
    else:
        return render_template("calls.html", form=form)

@app.route('/calls', methods=['GET'])
def show_calls():
    calls = Call.query.all()
    form = CallForm()
    return render_template('calls.html', calls=calls, form=form)

@app.route('/calls/edit', methods=['GET', 'POST'])
def edit_calls(call_id):
    call_id= Call.query.get(id)
    form = CallForm()
    if form.validate_on_submit():
        date = form.date.data
        time = form.time.data
        customer_name = form.customer_name.data
        phone_number = form.phone_number.data
        community = form.community.data
        area = form.area.data
        address = form.address.data
        customer_type = form.customer_type.data
        call_type = form.call_type.data
        comments = form.comments.data
        received_type = form.received_type.data
        response = form.response.data
        card = form.card.data
        database = form.database.data
        resolved = form.resolved.data
        booked = form.booked.data
        call = Call(date=date, time=time, customer_name=customer_name, phone_number=phone_number, community=community, area=area, address=address, customer_type=customer_type, call_type=call_type, comments=comments, received_type=received_type, response=response, card=card, database=database, resolved=resolved, booked=booked)
        db.session.add(call)
        db.session.commit()
        flash(f"Added {customer_name}")
        return redirect('/calls')
    else:
        return render_template("calls.html", form=form, call_id=call_id)

@app.route("/calls/<int:call_id>/update", methods=["POST"])
def update_call(id):
    call = Call.query.get(id)
    call.date = request.form['date']
    call.time = request.form['time']
    call.customer_name= request.form['customer_name']
    call.phone_number = request.form['phone_number']
    call.community = request.form['community']
    call.area = request.form['area']
    call.address = request.form['address']
    call.customer_type = request.form['customer_type']
    call.call_type = request.form['call_type']
    call.comments = request.form['comments']
    call.received_type = request.form['received_type']
    call.response = request.form['response']
    call.card = request.form['card']
    call.database = request.form['database']
    call.resolved = request.form['resolved']
    call.booked = request.form['booked']
  # Update other pieces of information here
    db.session.commit()
    flash('Call updated successfully', 'success')
    return redirect(url_for('show_calls'), call=call.id)

    
