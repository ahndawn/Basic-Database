from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()
# MODELS GO BELOW!

class Customer(db.Model):
    __tablename__= 'customers'
    id = db.Column(db.Integer, primary_key=True)

    last_name = db.Column(db.String)
    last_name2 = db.Column(db.String)
    first_name = db.Column(db.String)
    first_name2 = db.Column(db.String)
    referral = db.Column(db.String)
    customer_since = db.Column(db.Date)

    addresses = db.relationship('Address', backref='customers', lazy='dynamic')
    numbers = db.relationship('PhoneNumber', backref='customers', lazy='dynamic')

    jobs = db.relationship('Job', backref='customers', lazy='dynamic')
    
    def __repr__(self):
        return f"<Customer {self.last_name} {self.id}>"

class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)

    address_ln1 = db.Column(db.String)
    address_ln2 = db.Column(db.String)
    city = db.Column(db.String)
    zip = db.Column(db.String)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    sub_community_id = db.Column(db.Integer, db.ForeignKey('sub_community.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    address_note1 = db.Column(db.String)
    address_note2 = db.Column(db.String)
    zone = db.Column(db.String)
    billing = db.Column(db.String, default='Self')
    billing_type = db.Column(db.String, default='R')
    directions = db.Column(db.String)
    office_notes = db.Column(db.String)

    jobs = db.relationship('Job', backref='address', lazy='dynamic')
    address_notes = db.relationship('NoteConnector', backref='address', lazy='dynamic')

    def __repr__(self):
        return '<Address {}><Customer {}>'.format(self.address_ln1, self.customer.last_name)


class Job(db.Model):
    __tablename__ = 'job'
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    job_date = db.Column(db.Date)
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'))
    job_status = db.Column(db.String)
    pay_status = db.Column(db.String)
    pay_date = db.Column(db.String)
    compl_notes = db.Column(db.String)
    time_constraint = db.Column(db.String)
    schedule_position = db.Column(db.Integer)
    time_scheduled = db.Column(db.String)
    job_type = db.Column(db.String)

    services = db.relationship('Service', backref='job', lazy='dynamic')
    payments = db.relationship('PaymentConnector', backref='job', lazy='dynamic')
    sched_notes = db.relationship('NoteConnector', backref='job', lazy='dynamic')

    def __repr__(self):
        return '<Job><Address {}><Customer {}>'\
            .format(self.address.address_ln1, self.customer_id)

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)

    svc_type = db.Column(db.String)  # WIN, PRCL, EST, NC, SEAL, DISC
    svc = db.Column(db.String)  # I+O, OO, etc
    price = db.Column(db.Integer)
    status = db.Column(db.String)  # SCHED, COMPL
    work_type = db.Column(db.String)  # WORK, EST, NC

    def __repr__(self):
        return '<Service {} {}:{}-{}><Job {}><Address {}><Customer {}>'\
            .format(self.status, self.svc_type, self.svc, self.price, self.job.job_date,
                    self.job.address.address_ln1, self.job.customer_id)



class Crew(db.Model):
    __tablename__ = 'crew'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)
    crew_status = db.Column(db.String)
    display_num = db.Column(db.Integer)

    jobs = db.relationship('Job', backref='crew', lazy='dynamic')

    def __repr__(self):
        return '<Crew {}><Status {}>'.format(self.name, self.crew_status)



class Community(db.Model):
    __tablename__ = 'community'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)

    addresses = db.relationship('Address', backref='community', lazy='dynamic')
    subcommunities = db.relationship('SubCommunity', backref='community', lazy='dynamic')

    def __repr__(self):
        return '<Community {}><Subcommunities {}>'.format(self.name, self.subcommunities.count())


class SubCommunity(db.Model):
    __tablename__ = 'sub_community'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))

    addresses = db.relationship('Address', backref='sub_community', lazy='dynamic')

    def __repr__(self):
        return '<SubCommunity {}><Community {}>'.format(self.name, self.community.name)


class PhoneNumber(db.Model):
    __tablename__ = 'phone_number'
    id = db.Column(db.Integer, primary_key=True)

    number = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    number_type = db.Column(db.String)  # His C, Her C, Bruce PHW, etc

    def __repr__(self):
        return '<Phone Number {}><Type {}><Customer {}>'.format(self.number, self.number_type, self.customer.last_name)

class Email(db.Model):
    __tablename__ = 'email'
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

    def __repr__(self):
        return '<Email {}><Customer {}>'.format(self.email, self.customer.last_name)

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    date_processed = db.Column(db.Date)
    type = db.Column(db.String, nullable=False)
    ref = db.Column(db.String)
    amount = db.Column(db.Float, nullable=False)

    jobs = db.relationship('PaymentConnector', backref='payment', lazy='dynamic')

    def __repr__(self):
        return '<Customer Payment - Customer: {}, Date: {}, Type: {}, Ref: {}, Amt: {}>'.format(
            self.customer.last_name, self.date_processed, self.type, self.ref, self.amount)

class PaymentConnector(db.Model):
    __tablename__ = 'payment_connector'
    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)

    def __repr__(self):
        return '<Job Payment - Job ID: {}, Payment ID: {}>'.format(self.job_id, self.payment_id)



class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)

    note = db.Column(db.String, unique=True)

    def __repr__(self):
        return '<Note {}>'.format(self.note)


class NoteConnector(db.Model):
    __tablename__ = 'note_connector'
    id = db.Column(db.Integer, primary_key=True)

    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)

    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))

    def __repr__(self):
        return 'NoteConnector - Note: {}, Customer: {}, Address: {}, Job: {}'\
            .format(self.note_id, self.customer_id, self.address_id, self.job_id)



#departments
class Department(db.Model):
    """Department Model"""

    __tablename__ = "departments"

    dept_code = db.Column(db.Text, primary_key=True)
    dept_name = db.Column(db.Text, nullable=False, unique=True)
    phone = db.Column(db.Text)

    def __repr__(self):
        return f"<Department {self.dept_code} {self.dept_name} {self.phone} >"


class Employee(db.Model):
    """Employee Model"""

    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    state = db.Column(db.Text, nullable=False, default='FL')
    dept_code = db.Column(db.Text, db.ForeignKey('departments.dept_code'))

    dept = db.relationship('Department', backref='employees')

    assignments = db.relationship('EmployeeProject', backref='employee')

    projects = db.relationship(
        'Project', secondary="employees_projects", backref="employees")

    def __repr__(self):
        return f"<Employee {self.name} {self.state} {self.dept_code} >"


class Project(db.Model):

    __tablename__ = 'projects'

    proj_code = db.Column(db.Text, primary_key=True)
    proj_name = db.Column(db.Text, nullable=False, unique=True)

    assignments = db.relationship('EmployeeProject', backref="project")


class EmployeeProject(db.Model):

    __tablename__ = 'employees_projects'

    emp_id = db.Column(db.Integer, db.ForeignKey(
        'employees.id'), primary_key=True)

    proj_code = db.Column(db.Text, db.ForeignKey(
        'projects.proj_code'), primary_key=True)

    role = db.Column(db.Text)


def get_directory():
    all_emps = Employee.query.all()

    for emp in all_emps:
        if emp.dept is not None:
            print(emp.name, emp.dept.dept_name, emp.dept.phone)
        else:
            print(emp.name)


def get_directory_join():
    directory = db.session.query(
        Employee.name, Department.dept_name, Department.phone).join(Department).all()

    for name, dept, phone in directory:
        print(name, dept, phone)


def get_directory_join_class():
    directory = db.session.query(Employee, Department).join(Department).all()

    for emp, dept in directory:
        print(emp.name, dept.dept_name, dept.phone)


def get_directory_all_join():
    directory = db.session.query(
        Employee.name, Department.dept_name, Department.phone).outerjoin(Department).all()

    for name, dept, phone in directory:
        print(name, dept, phone)


#User
class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


#CallLog
class Call(db.Model):
    __tablename__ = 'call'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.String(64), nullable=False)
    community = db.Column(db.String(64), nullable=True)
    area = db.Column(db.String(64), nullable=True)
    address = db.Column(db.String(256), nullable=False)
    customer_type = db.Column(db.String(64), nullable=False)
    call_type = db.Column(db.String(64), nullable=False)
    comments = db.Column(db.String(64), nullable=False)
    received_type = db.Column(db.String(64), nullable=True)
    response = db.Column(db.Boolean, nullable=True)
    card = db.Column(db.Boolean, nullable=True)
    database = db.Column(db.Boolean, nullable=True)
    resolved = db.Column(db.Boolean, nullable=True)
    booked = db.Column(db.Boolean, nullable=True)


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)