from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import InputRequired

class AddCustomerForm(FlaskForm):

    last_name = StringField("Last Name", validators=[InputRequired(message="Please add Last Name")])
    first_name = StringField("First Name", validators=[InputRequired(message="Please add First Name")])
    phone_number = StringField("Phone Number", validators=[InputRequired(message="Please add Number")])
    email = StringField("Email", validators=[InputRequired()])
    address_line_1 = StringField("Address Line 1", validators=[InputRequired()])
    address_line_2 = StringField("Address Line 2")
    city = StringField("City", validators=[InputRequired()])
    state= StringField("State", validators=[InputRequired()])
    postal= StringField("Postal Code", validators=[InputRequired()])
    community = StringField("Community")
    sub_community = StringField("Sub Community")

class EmployeeForm(FlaskForm):

    name = StringField("Employee Name", validators=[InputRequired(message="Name cannot be blank")])
    state = StringField("State")
    dept_code = SelectField("Department Code")