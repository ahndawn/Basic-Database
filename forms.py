from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, FloatField, SelectField, PasswordField, SubmitField, EmailField, TextAreaField, FieldList, FormField, IntegerField, DateField, TimeField, BooleanField
from wtforms.validators import InputRequired, length, optional, email, DataRequired, Email
from datetime import date

class CallForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
    customer_name = StringField("Customer Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    community = StringField("Community")
    area = SelectField("Area", choices=[(''), ('north'), ('northwest'), ('northeast'), ('central-west'), ('central'), ('central-east'), ('southeast'), ('south'), ('southwest'), ('ocean')])
    address = StringField("Address", validators=[DataRequired()])
    customer_type = SelectField("Customer Type", choices=[('existing'),('new')], validators=[DataRequired()])
    call_type = SelectField("Call Type", choices=[('schedule'),('complaint'), ('payment'), ('estimate')], validators=[DataRequired()])
    comments = StringField("Comments", validators=[DataRequired()])
    received_type = SelectField("Received Type", choices=[('msg'), ('call'), ('rollover')],validators=[DataRequired()])
    response = SelectField("Response", choices=[('yes'), ('no')])
    card = SelectField("Card", choices=[('yes'), ('no')])
    database = SelectField("Database", choices=[('yes'), ('no')])
    resolved = SelectField("Resolved", choices=[('yes'), ('no')])

class PhoneSearchForm(FlaskForm):
    phone_number = StringField('PHONE NUMBER:', validators=[DataRequired()])

class ResolvedSearchForm(FlaskForm):
    resolved = SelectField('RESOLVED:', choices=[('no'),('yes')], validators=[DataRequired()])

class NameSearchForm(FlaskForm):
    customer_name = StringField('CUSTOMER NAME:', validators=[DataRequired()])

class ResponseSearchForm(FlaskForm):
    response = SelectField('RESPONSE:', choices=[('no'),('yes')], validators=[DataRequired()])

class CommunitySearchForm(FlaskForm):
    community = StringField('COMMUNITY:', validators=[DataRequired()])

class AreaSearchForm(FlaskForm):
    area = StringField('AREA:', validators=[DataRequired()])

class TypeSearchForm(FlaskForm):
    call_type = SelectField('CALL TYPE:', choices=[('schedule'),('complaint'), ('payment'), ('estimate')], validators=[DataRequired()])









####################################
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
 ##########################
    #CUSTOMER NOTES
    customer_notes = TextAreaField('Customer Notes')
    submit_customer_info = SubmitField('Save Changes', id="info_submit")


class EditContactInfoForm(FlaskForm):
    from markupsafe import Markup

    numbers = FieldList(FormField(NumberEntryForm))
    add_number = SubmitField(Markup("&plus;"), id='add_number')

    emails = FieldList(FormField(EmailEntryForm))
    add_email = SubmitField('Add Email')

    submit_contact_info = SubmitField('Save Changes', id="contact_submit")


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
