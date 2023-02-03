from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)

# MODELS GO BELOW!

class Customer(db.Model):
    __tablename__= 'customers'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).all()
    
    @classmethod
    def get_by_community(cls, community):
        return cls.query.filter_by(community=community).all()

    id = db.Column(db.Integer,
                    primary_key = True,
                    autoincrement=True)
    last_name = db.Column(db.String(20),
                    nullable = False,
                    unique =True)
    # first name is not needed for customer account to be created
    first_name = db.Column(db.String(20),
                    nullable = True)
    email = db.Column(db.String(30), nullable= True)
    phone_number = db.Column(db.Integer, nullable= False)
    address_line_1 = db.Column(db.String(35),
                    nullable = False)
    address_line_2 = db.Column(db.String(35),
                    nullable = False)
    city = db.Column(db.String(35), 
                    nullable = False)
    state = db.Column(db.String(2),
                    nullable = False)
    postal = db.Column(db.String(5),
                    nullable = False)
    community = db.Column(db.String,
                    nullable = True)
    sub_community = db.Column(db.String,
                    nullable = True)
    
    def __repr__(self):
        return f"<Customer {self.last_name} {self.address_1} {self.phone_number} {self.address} {self.city} {self.state} {self.postal}>"

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
