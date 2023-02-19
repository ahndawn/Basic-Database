from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, FloatField, SelectField, PasswordField, SubmitField, EmailField, TextAreaField, FieldList, FormField, IntegerField, DateField, TimeField, BooleanField
from wtforms.validators import InputRequired, length, optional, email, DataRequired

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

##################################
#User Forms
class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    bio = TextAreaField('(Optional) Tell us about yourself')
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

#############################
#Customer forms
class CustomerSearchForm(FlaskForm):
    customer_name = StringField('Name')
    customer_number = StringField('Phone Number')
    customer_address = StringField('Address')
    submit = SubmitField('Search')

class CustomerNameForm(FlaskForm):
    last_name = StringField('Last Name')
    first_name = StringField('First Name')

class NumberEntryForm(FlaskForm):
    number_type = StringField('Number Type')
    number = StringField('Phone Number', validators=[DataRequired(message='Must Have Valid Phone Number'), length(min=7, max=12)])

class EmailEntryForm(FlaskForm):
    email = EmailField('Email', validators=[optional(), email(check_deliverability=True, message='Must Be Valid Email')])

class AddressEntryForm(FlaskForm):
    address_ln1 = StringField('Address Line 1', validators=[DataRequired(message='Must Have Street Address')])
    address_ln2 = StringField('Address Line 2 (Apt, Suite)')
    city = StringField('City', validators=[DataRequired(message='Must Have City')])
    zip = StringField('Zip', validators=[DataRequired(message='Must Have Zip Code')])

    community = SelectField('Community')
    new_community = StringField('New Community')
    # communities = get_all_communities()
    # for comm in communities:
    #     community.choices.append((comm.id, comm.name))

    sub_community = SelectField('Sub Community')
    new_sub_community = StringField('New Sub Community')

    address_notes = TextAreaField('Address Notes')

    billing = SelectField('Billing Preference', choices=['Leave Bill', 'Email Bill', 'Fax Bill', 'Mail Bill'])

    billing_type = SelectField('Billing Type', choices=[('R', 'Residence'), ('B', 'Business'), ('A', 'Antiquer'), ('V', 'Vendor')])

    directions = StringField('Directions')

class EditCustomerInfoForm(FlaskForm):
    last_name = StringField('Last Name', validators=[DataRequired(message='Must Have Primary Last Name')])
    first_name = StringField('First Name')
    last_name2 = StringField('Last Name 2')
    first_name2 = StringField('First Name 2')

    referral = StringField('Referral')
    customer_since = DateField('Customer Since', validators=[optional(), DataRequired(message='Date must be in format m/d/yy')], format='%Y-%m-%d')
    customer_notes = TextAreaField('Customer Notes')
    submit_customer_info = SubmitField('Save Changes', id="info_submit")

class EditAddressInfoForm(FlaskForm):
    addresses = FieldList(FormField(AddressEntryForm))

    submit_address_info = SubmitField('Save Changes', id="address_submit")


class NewCustomerForm(FlaskForm):
    customer_info = FormField(EditCustomerInfoForm)

    phone_numbers = FieldList(FormField(NumberEntryForm), min_entries=1)
    add_number = SubmitField('Add Phone Number', id="add_number")

    emails = FieldList(FormField(EmailEntryForm), min_entries=1)
    add_email = SubmitField('Add Email', id="add_email")

    addresses = FieldList(FormField(AddressEntryForm), min_entries=1)

    submit_new_customer = SubmitField('Save New Customer', id="submit_new_customer")


class NotesEntryField(FlaskForm):
    note = StringField('Note')


class ServiceEntryForm(FlaskForm):
    estimate = BooleanField('Estimate')
    no_charge = BooleanField('No Charge')

    prcl = BooleanField('Pressure Cleaning')
    seal = BooleanField('Sealing')

    service = StringField('Service', validators=[DataRequired()])
    price = StringField('Price')


class JobEntryForm(FlaskForm):
    job_day = DateField('Job Day', validators=[DataRequired(message='Date must be in format m/d/yy')], format='%m/%d/%yy')
    job_time = TimeField('Job Time')
    time_constraint = SelectField('Time Constraint', choices=[(0, '---'), (1, 'No Earlier'), (2, 'No Later')])

    crew = SelectField('Crew')
    schedule_pos = IntegerField('Schedule Position', validators=[DataRequired()])

    job_notes = FieldList(FormField(NotesEntryField), min_entries=1)

    customer_search = StringField('Customer', validators=[DataRequired()])
    address = SelectField('Address', validators=[DataRequired()])

    services = FieldList(FormField(ServiceEntryForm), min_entries=1)

    search_for_customer = SubmitField('Search for Customer')
    submit_new_job = SubmitField('Add New Job')


########################################
#CALL LOG

class CallForm(FlaskForm):
    date = StringField("Date", validators=[DataRequired()])
    time = StringField("Time", validators=[DataRequired()])
    customer_name = StringField("Customer Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    community = StringField("Community", validators=[DataRequired()])
    area = StringField("Area", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    customer_type = StringField("Customer Type", validators=[DataRequired()])
    call_type = StringField("Call Type", validators=[DataRequired()])
    comments = StringField("Comments")
    received_type = StringField("Received Type", validators=[DataRequired()])
    response = BooleanField("Response")
    card = BooleanField("Card")
    database = BooleanField("Database")
    resolved = BooleanField("Resolved")
    booked = BooleanField("Booked")