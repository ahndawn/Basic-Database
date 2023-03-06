from flask import Flask, flash, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from models import db, connect_db, Call, Crew, Customer, PhoneNumber, Address, Community, SubCommunity, Job
from forms import CallForm, PhoneSearchForm, ResponseSearchForm, ResolvedSearchForm, NameSearchForm, CommunitySearchForm, AreaSearchForm, CustomerSearchForm, NewCustomerForm, EditCustomerInfoForm, EditContactInfoForm, EditAddressInfoForm, JobEntryForm
from sqlalchemy import or_, and_
from sqlalchemy.sql import func
import submit
import parsing
import traceback
from wtforms.validators import DataRequired
from wtforms import SelectField, DateField, SubmitField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = '2mtikn$u'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

with app.test_request_context():    
    connect_db(app)
    db.create_all()

########################
#HOME
@app.route('/')
def home():
    """Shows Home page"""
    
    return render_template("home.html")

#######################
#Call Log routes
@app.route('/calls', methods=["GET", "POST"])
def calls():
    form = CallForm()
    if request.method == "POST" and form.validate():
        call = Call(date=form.date.data, 
                    time=form.time.data,
                    customer_name=form.customer_name.data,
                    phone_number=form.phone_number.data,
                    community=form.community.data,
                    area=form.area.data,
                    address=form.address.data,
                    customer_type=form.customer_type.data,
                    call_type=form.call_type.data,
                    comments=form.comments.data,
                    received_type=form.received_type.data,
                    response=form.response.data,
                    card=form.card.data,
                    database=form.database.data,
                    resolved=form.resolved.data)
        db.session.add(call)
        db.session.commit()
        return redirect(url_for('calls'))
    calls = Call.query.all()
    return render_template('calls.html', form=form, calls=calls)

@app.route('/edit-call/<int:id>', methods=['GET', 'POST'])
def edit_call(id):
    call = Call.query.get_or_404(id)
    form = CallForm(obj=call)
    if form.validate_on_submit():
        form.populate_obj(call)
        db.session.commit()
        flash('Call updated successfully', 'success')
        return redirect(url_for('calls'))
    return render_template('call.html', call=call, form=form)

@app.route('/calls/delete/<int:id>')
def delete_call(id):
    # retrieve the call from the database using the id parameter
    call = Call.query.get_or_404(id)

    # delete the call from the database
    db.session.delete(call)
    db.session.commit()

    # redirect to the calls page
    return redirect('/calls')

######################
# Search routes

@app.route('/response_search', methods=['GET', 'POST'])
def response_search():
    form = ResponseSearchForm(request.form)
    calls = []
    if request.method == 'POST' and form.validate():
        response = form.response.data
        calls = Call.query.filter(Call.response.like(f'%{response}%')).all()
    return render_template('response_search.html', form=form, calls=calls)

@app.route('/phone_search', methods=['GET', 'POST'])
def phone_search():
    form = PhoneSearchForm(request.form)
    calls = []
    if request.method == 'POST' and form.validate():
        phone_number = form.phone_number.data
        calls = Call.query.filter(Call.phone_number.like(f'%{phone_number}%')).all()
    return render_template('phone_search.html', form=form, calls=calls)

@app.route('/resolved_search', methods=['GET', 'POST'])
def resolved_search():
    form = ResolvedSearchForm(request.form)
    calls = []
    if request.method == 'POST' and form.validate():
        resolved = form.resolved.data
        calls = Call.query.filter(Call.resolved.like(f'%{resolved}%')).all()
    return render_template('resolved_search.html', form=form, calls=calls)

@app.route('/name_search', methods=['GET', 'POST'])
def name_search():
    form = NameSearchForm(request.form)
    calls = []
    if request.method == 'POST' and form.validate():
        customer_name = form.customer_name.data
        calls = Call.query.filter(Call.customer_name.like(f'%{customer_name}%')).all()
    return render_template('name_search.html', form=form, calls=calls)

@app.route('/community_search', methods=['GET', 'POST'])
def community_search():
    form = CommunitySearchForm(request.form)
    calls = []
    if request.method == 'POST' and form.validate():
        community = form.community.data
        calls = Call.query.filter(Call.community.like(f'%{community}%')).all()
    return render_template('community_search.html', form=form, calls=calls)

@app.route('/area_search', methods=['GET', 'POST'])
def area_search():
    form = AreaSearchForm(request.form)
    calls = []
    if request.method == 'POST' and form.validate():
        area = form.area.data
        calls = Call.query.filter(Call.area.like(f'%{area}%')).all()
    return render_template('area_search.html', form=form, calls=calls)
##########################

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

# @app.route('/results')
# def results():
#     return render_template('results.html', title='Results', search_results=search_results)


@app.route('/customers/<customer_id>', methods=['GET', 'POST'])
def customer_url(customer_id):

    if customer_id is not None:
        if customer_id == 'add':
            return new_customer()
        elif isinstance(int(customer_id), int):
            return customer_view(customer_id)


@app.route('/customers/<customer_id>/edit', methods=['GET', 'POST'])
def customer_edit(customer_id):

    customer = get_customer(customer_id)  # get customer from DB
    print(customer)

    edit_section = request.args.get('section')  # get section requested to edit

    if edit_section == 'customer_info':
        form = EditCustomerInfoForm()  # initiate customer edit form

        if form.submit.data:  # if submit button was pressed
            submit.submit_customer_info(customer_id, form)
            return redirect(url_for('customer_url', customer_id=customer_id))
        else:
            form = fill_customer_form(customer_id, form)  # fill form with stored values

    elif edit_section == 'contact_info':
        form = EditContactInfoForm(id='edit_contact_info')

        # if request.method == ['post']:
        #     if request.form['name'] == 'add_number_test':
        #         getattr(form, 'numbers').append_entry()
        #         return render_template('customer_edit.html', form=form, section=edit_section)
        print(form.add_number.__html__())
        print(form.add_number_test.__html__())
        if form.add_number.data:
            getattr(form, 'numbers').append_entry()
            return render_template('customer_edit.html', form=form, section=edit_section)
        if form.submit.data:
            # TODO submit contact info
            pass
        else:
            form = fill_contact_form(customer_id, form)

    return render_template('customer_edit.html', form=form, section=edit_section)


@app.route('/customers/new', methods=['GET', 'POST'])
def new_customer():
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
        submit.submit_new_customer(form)
        print('new id: {}'.format(get_new_customer_id()))
        return redirect(url_for('customer_url', customer_id=get_new_customer_id()))
    elif not form.validate_on_submit():
        print(form.errors)
        print('comm: {}'.format(form.addresses.entries[0].community.data))
        print('subcomm: {}'.format(form.addresses.entries[0].sub_community.data))
        print(form.addresses.entries[0].community.choices)



    return render_template('new_customer.html', title='New Customer - MWC-DB', form=form)


def customer_view(customer_id):

    customer = get_customer_view(customer_id)

    info_form = EditCustomerInfoForm(id="edit_info_form")
    contact_form = EditContactInfoForm(id="edit_contact_form")
    address_form = EditAddressInfoForm(id="edit_address_form")
    job_form = JobEntryForm()

    if info_form.submit_customer_info.data:
        submit.submit_customer_info(customer_id, info_form)
        return redirect(url_for('customer_url', customer_id=customer_id))

    if contact_form.submit_contact_info.data:
        submit.submit_contact_info(customer_id, contact_form)
        return redirect(url_for('customer_url', customer_id=customer_id))

    if address_form.submit_address_info.data:
        submit.submit_address_info(customer_id, address_form)
        return redirect(url_for('customer_url', customer_id=customer_id))

    info_form = fill_customer_form(customer_id, info_form)
    contact_form = fill_contact_form(customer_id, contact_form)
    address_form = fill_address_form(customer_id, address_form)

    choices = [(0, '---')]
    crews = get_all_crews()
    for crew in crews:
        choices.append(crew)
    job_form.crew.choices = choices

    return render_template('customers.html', title=f'{customer["last_name"]} - Customer View', customer=customer, info_form=info_form, contact_form=contact_form, address_form=address_form, job_form=job_form)


@app.route('/schedule', methods=['GET', 'POST'])
@app.route('/schedule/<sched_date>', methods=['GET', 'POST'])
@app.route('/schedule/<sched_date>/<crew_name>', methods=['GET', 'POST'])
def schedule(crew_name=None, sched_date=None):
    import datetime
    from datetime import datetime as dt
    form = FetchScheduleForm()

    if form.is_submitted():
        print('----- Form Submit: {} -----'.format(form.schedule_date.data))
        crew_submit = str(form.crew_name.data)
        if crew_submit == 'All Crews':
            crew_submit = 'all'
        if form.day_before.data:
            print('Schedule - Day Before: ' + str(form.schedule_date.data) + ', ' + crew_submit)
            return redirect('/schedule/' + (form.schedule_date.data - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '/' + crew_submit)
        elif form.day_after.data:
            print('Schedule - Day After: ' + str(form.schedule_date.data) + ', ' + crew_submit)
            return redirect('/schedule/' + (form.schedule_date.data + datetime.timedelta(days=1)).strftime('%Y-%m-%d') + '/' + crew_submit)
        elif form.view_all.data:
            print('Schedule - View All: ' + str(form.schedule_date.data))
            return redirect('/schedule/' + str(form.schedule_date.data) + '/all')
        else:
            print('Schedule - Fetch: ' + str(form.schedule_date.data) + ', ' + crew_submit)
            return redirect('/schedule/' + str(form.schedule_date.data) + '/' + crew_submit)

    if crew_name is not None and sched_date is not None:
        print('----- Crew and Sched Date not None: {} -----'.format(form.schedule_date.data))
        schedule_weekday = str(datetime.datetime.strptime(sched_date, '%Y-%m-%d').strftime('%A'))
        form.schedule_date.default = datetime.datetime.strptime(sched_date[5:7] + '/' + sched_date[8:] + '/' + sched_date[2:4], '%m/%d/%y').date()
        crew_choices = get_crew_on_day(sched_date)
        for crew in crew_choices:
            form.crew_name.choices.append(crew[0])
        form.process()
        schedules = []
        if crew_name == 'all':
            form.crew_name.default = 'All Crews'
            form.process()
            for crew in get_crew_on_day(sched_date):
                schedules.append(schedule_fetch(crew[0], sched_date))
        else:
            form.crew_name.default = crew_name
            form.process()
            schedules.append(schedule_fetch(crew_name, sched_date))
        return render_template('schedule.html', title=f'Schedule - {form.crew_name.default} - {form.schedule_date.data.month}/{form.schedule_date.data.day}', form=form, schedules=schedules, schedule_weekday=schedule_weekday)
    elif sched_date is not None and crew_name is None:
        form.schedule_date.data = datetime.datetime.strptime(sched_date[5:7] + '/' + sched_date[8:] + '/' + sched_date[2:4], '%m/%d/%y')
        form.process()
        return redirect('/schedule/' + sched_date + '/all')
    elif sched_date is None and crew_name is None:
        return redirect('/schedule/' + str(datetime.datetime.today().date()) + '/all')


@app.route('/add_number')
@app.route('/add_email')
def add_contact():
    print('url: ' + request.base_url)

    numbers = 0
    emails = 0
    for arg in request.args:
        if arg[:7] == 'numbers':
            numbers += 1
        elif arg[:6] == 'emails':
            emails += 1

    numbers /= 2
    print('num nums: {}'.format(numbers))

    form = EditContactInfoForm()
    if numbers > 0:
        x = 0
        while x < numbers:
            getattr(form, 'numbers').append_entry()
            form.numbers.entries[x].number_type.data = request.args.get('numbers-{}-number_type'.format(x))
            form.numbers.entries[x].number.data = request.args.get('numbers-{}-number'.format(x))
            x += 1

    if emails > 0:
        x = 0
        while x < emails:
            getattr(form, 'emails').append_entry()
            form.emails.entries[x].email.data = request.args.get('emails-{}-email'.format(x))
            x += 1

    if 'add_number' in request.base_url:
        getattr(form, 'numbers').append_entry()
        return render_template('__customer_contact_phone_field.html', contact_form=form)

    if 'add_email' in request.base_url:
        print('success')
        getattr(form, 'emails').append_entry()
        return render_template('__customer_contact_email_field.html', contact_form=form)


@app.route('/add_address')
@app.route('/change_community')
@app.route('/new_comm_subcomm')
def add_address():
    print('Address AJAX')

    max_address = -1
    for arg in request.args:
        if arg != 'csrf_token':
            print(arg + arg[10:11])
            index = int(arg[10:11])
            if index > max_address:
                max_address = index

    num_adds = max_address + 1

    print('num adds: {}'.format(num_adds))
    form = EditAddressInfoForm()

    communities = get_all_communities()

    if num_adds > 0:
        x = 0
        while x < num_adds:
            getattr(form, 'addresses').append_entry()
            form.addresses.entries[x].address_ln1.data = request.args.get('addresses-{}-address_ln1'.format(x))
            form.addresses.entries[x].address_ln2.data = request.args.get('addresses-{}-address_ln2'.format(x))
            form.addresses.entries[x].city.data = request.args.get('addresses-{}-city'.format(x))
            form.addresses.entries[x].zip.data = request.args.get('addresses-{}-zip'.format(x))

            community_choices = ['---', 'New Community', '---']
            for community in communities:
                community_choices.append(community.name)
            form.addresses.entries[x].community.choices = community_choices

            sub_community_choices = ['---']
            if request.args.get('addresses-{}-community'.format(x)) != '---':
                sub_community_choices.append('New Sub Community')
                sub_community_choices.append('---')
                form.addresses.entries[x].community.data = request.args.get('addresses-{}-community'.format(x))
                subcomms = get_sub_communities_by_name(request.args.get('addresses-{}-community'.format(x)))
                if subcomms is not None:
                    for subcom in subcomms:
                        print(subcom)
                        sub_community_choices.append(subcom.name)

            form.addresses.entries[x].sub_community.choices = sub_community_choices
            if request.args.get('addresses-{}-sub_community'.format(x)):
                form.addresses.entries[x].sub_community.data = request.args.get('addresses-{}-sub_community'.format(x))
            form.addresses.entries[x].billing.data = request.args.get('addresses-{}-billing'.format(x))
            form.addresses.entries[x].billing_type.data = request.args.get('addresses-{}-billing_type'.format(x))
            x += 1

            if form.addresses.entries[-1].community.data == 'New Community':
                form.addresses.entries[-1].new_community.validators = [DataRequired(message='Must Enter New Community')]
                form.addresses.entries[-1].new_community.data = request.args.get('addresses-{}-new_community'.format(x))
            else:
                form.addresses.entries[-1].new_community.validators = None

            if form.addresses.entries[-1].sub_community.data == 'New Sub Community':
                form.addresses.entries[-1].new_sub_community.validators = [
                    DataRequired(message='Must Enter New Sub Community')]
                form.addresses.entries[-1].new_sub_community.data = request.args.get('addresses-{}-new_sub_community'.format(x))
            else:
                form.addresses.entries[-1].new_sub_community.validators = None

    if 'address' in request.base_url:
        getattr(form, 'addresses').append_entry()
        community_choices = ['---']
        for community in communities:
            community_choices.append(community.name)
        form.addresses.entries[-1].community.choices = community_choices

    return render_template('__customer_address_address_field.html', address_form=form)


@app.route('/new_cust_number')
@app.route('/new_cust_email')
@app.route('/new_cust_address')
@app.route('/new_cust_community')
def new_customer_ajax():
    numbers = 0
    emails = 0
    addresses = 0

    for arg in request.args:
        if 'phone_numbers-' in arg and '-number_type' in arg:
            numbers += 1
        elif 'emails-' in arg and '-email' in arg:
            emails += 1
        elif 'addresses-' in arg and '-address_ln1' in arg:
            addresses += 1

    print('Numbers: {}'.format(numbers))
    print('Emails: {}'.format(emails))
    print('Addresses: {}'.format(addresses))
    form = NewCustomerForm()

    if 'number' in request.base_url:
        if numbers > 0:
            x = 1
            while x <= numbers:
                if x > 1:
                    getattr(form, 'phone_numbers').append_entry()
                form.phone_numbers.entries[-1].number.data = request.args.get('phone_numbers-{}-number'.format(x-1))
                form.phone_numbers.entries[-1].number_type.data = request.args.get('phone_numbers-{}-number_type'.format(x-1))
                x += 1
        getattr(form, 'phone_numbers').append_entry()
        return render_template('_new_customer_phone_field.html', form=form)
    elif 'email' in request.base_url:
        if emails > 0:
            x = 1
            while x <= emails:
                if x > 1:
                    getattr(form, 'emails').append_entry()
                form.emails.entries[-1].email.data = request.args.get('emails-{}-email'.format(x-1))
                x += 1
        getattr(form, 'emails').append_entry()
        return render_template('_new_customer_email_field.html', form=form)
    elif 'address' in request.base_url or 'community' in request.base_url:
        if addresses > 0:
            x = 1
            communities = get_all_communities()
            while x <= addresses:
                if x > 1:
                    getattr(form, 'addresses').append_entry()
                form.addresses.entries[-1].address_ln1.data = request.args.get('addresses-{}-address_ln1'.format(x-1))
                form.addresses.entries[-1].address_ln2.data = request.args.get('addresses-{}-address_ln2'.format(x-1))
                form.addresses.entries[-1].city.data = request.args.get('addresses-{}-city'.format(x-1))
                form.addresses.entries[-1].zip.data = request.args.get('addresses-{}-zip'.format(x-1))

                # add all communities to dropdown
                community_choices = ['---', 'New Community', '---']
                for community in communities:
                    community_choices.append(community.name)
                form.addresses.entries[-1].community.choices = community_choices
                form.addresses.entries[-1].community.data = request.args.get('addresses-{}-community'.format(x-1))
                if request.args.get('addresses-{}-new_community'.format(x-1)):
                    form.addresses.entries[-1].new_community.data = request.args.get('addresses-{}-new_community'.format(x-1))


                # if a community was chosen
                sub_community_choices = ['---']
                if request.args.get('addresses-{}-community'.format(x-1)) != '---':
                    sub_community_choices.append('New Sub Community')
                    sub_community_choices.append('---')
                    sub_communities = get_sub_communities_by_name(form.addresses.entries[-1].community.data)
                    # add chosen community's sub communities to dropdown
                    if sub_communities is not None:
                        for sub_community in sub_communities:
                            sub_community_choices.append(sub_community.name)
                form.addresses.entries[-1].sub_community.choices = sub_community_choices
                form.addresses.entries[-1].sub_community.data = request.args.get('addresses-{}-sub_community'.format(x-1))
                if request.args.get('addresses-{}-new_sub_community'.format(x-1)):
                    form.addresses.entries[-1].new_sub_community.data = request.args.get('addresses-{}-new_sub_community'.format(x-1))

                if form.addresses.entries[-1].community.data == 'New Community':
                    form.addresses.entries[-1].new_community.validators = [DataRequired(message='Must Enter New Community')]
                else:
                    form.addresses.entries[-1].new_community.validators = None

                if form.addresses.entries[-1].sub_community.data == 'New Sub Community':
                    form.addresses.entries[-1].new_sub_community.validators = [DataRequired(message='Must Enter New Sub Community')]
                else:
                    form.addresses.entries[-1].new_sub_community.validators = None

                form.addresses.entries[-1].billing.data = request.args.get('addresses-{}-billing'.format(x-1))
                form.addresses.entries[-1].billing_type.data = request.args.get('addresses-{}-billing_type'.format(x-1))



                x += 1

        if 'address' in request.base_url:
            getattr(form, 'addresses').append_entry()
            # add all communities to dropdown
            community_choices = ['---', 'New Community', '---']
            communities = get_all_communities()
            for community in communities:
                community_choices.append(community.name)
            form.addresses.entries[-1].community.choices = community_choices
        return render_template('_new_customer_address_field.html', form=form)


@app.route('/api/excel', methods=['GET'])
def excel_api_call():
    # print('Parsing Args:')
    # parser = argparse.ArgumentParser(description='Push or Pull')
    # parser.add_argument('-func', '--function')
    #
    # parser.add_argument('-row', '--job_row')
    # parser.add_argument('-wkbk', '--workbook')
    #
    # parser.add_argument('-jdt', '--job_date')
    # parser.add_argument('-crw', '--crew')
    # parser.add_argument('-tme', '--job_time')
    # parser.add_argument('-cust', '--customer_name')
    # parser.add_argument('-add1', '--address_ln1')
    # parser.add_argument('-add2', '--address_ln2')
    # parser.add_argument('-comm', '--community')
    # parser.add_argument('-subcomm', '--subcommunity')
    # parser.add_argument('-dire', '--directions')
    # parser.add_argument('-n1', '--note1')
    # parser.add_argument('-n2', '--note2')
    # parser.add_argument('-bill', '--billing')
    # parser.add_argument('-btyp', '--billing_type')
    # parser.add_argument('-jtyp', '--job_type')
    # parser.add_argument('-sch', '--scheduled_svc')
    # parser.add_argument('-compl', '--completed_svc')
    # parser.add_argument('-schpos', '--schedule_pos')
    # parser.add_argument('-sts', '--status')
    #
    # args = parser.parse_args()
    # print('Parsed')

    # push from excel
    if request.args.get('func') == 'push':
        print('Excel Push Detected')
        print('Assembling Vars...', end='')
        job_info = {
            'job_date': datetime.datetime.strptime(request.args.get('jdt'), '%m/%d/%Y'),
            'crew': request.args.get('crw'),
            'job_time': '',
            'customer_name': request.args.get('cust'),
            'address_ln1': request.args.get('add1'),
            'address_ln2': '',
            'community': '',
            'subcommunity': '',
            'directions': '',
            'note1': '',
            'note2': '',
            'billing': '',
            'billing_type': '',
            'scheduled_svc': '',
            'completed_svc': '',
            'schedule_pos': '',
            'job_type': '',
            'job_status': '',
        }

        if request.args.get('tme') is not None:
            job_info['job_time'] = str(request.args.get('tme'))
        if request.args.get('add2') is not None:
            job_info['address_ln2'] = request.args.get('add2')
        if request.args.get('comm') is not None:
            job_info['community'] = request.args.get('comm')
        if request.args.get('subcomm') is not None:
            job_info['subcommunity'] = request.args.get('subcomm')
        if request.args.get('dire') is not None:
            job_info['directions'] = request.args.get('dire')
        if request.args.get('n1') is not None:
            job_info['note1'] = request.args.get('n1')
        if request.args.get('n2') is not None:
            job_info['note2'] = request.args.get('n2')
        if request.args.get('bill') is not None:
            job_info['billing'] = request.args.get('bill')
        if request.args.get('btyp') is not None:
            job_info['billing_type'] = request.args.get('btyp')
        if request.args.get('sch') is not None:
            job_info['scheduled_svc'] = request.args.get('sch')
        if request.args.get('compl') is not None:
            job_info['completed_svc'] = request.args.get('compl')
        if request.args.get('schpos') is not None:
            job_info['schedule_pos'] = request.args.get('schpos')
        if request.args.get('jtyp') is not None:
            job_info['job_type'] = request.args.get('jtyp')
        if request.args.get('sts') is not None:
            job_info['job_status'] = request.args.get('sts')
        print('Vars Assembled')
        try:
            print('Integrating...')
            excel_integrate.excel_push(job_info)
            submit.commit_db_session()
            print('Integrated')
            return 'Push for ' + job_info['customer_name'] + ' at ' + job_info['address_ln1'] + ' successful.'

        except Exception:
            traceback.print_exc()

    return 'Error'


@app.route('/api/not_paids', methods=['GET'])
def not_paid_mailers():
    print('Args:')
    for arg in request.args:
        print(arg)
    customer_id = request.args.get('custID')
    customer = get_customer(customer_id)
    address = customer.addresses[0]

    if customer.first_name:
        name = f'{customer.first_name} {customer.last_name}'
    else:
        name = customer.last_name
    mailing_address = address.address_ln1
    if address.address_ln2:
        mailing_address += ", " + address.address_ln2
    city = address.city
    zip_code = address.zip

    return f'{name};{mailing_address};{city}, FL {zip_code}'
########################
#queries
def customer_query(search_terms):

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


def get_customer_view(customer_id):
    from models import db, Customer, Address, Job, Service
    from sqlalchemy import desc, asc
    db.create_all()

    customer_id = int(customer_id)

    customer = db.session.query(Customer).get(customer_id)
    print('---------------')
    print('Customer View for: ' + str(customer))
    print('---------------')
    if customer is not None:
        customer_info = parsing.customer_parse(customer)

        customer_info['addresses'] = []
        addresses = customer.addresses
        for address in addresses:
            address_info = parsing.address_parse(address)
            if address.jobs:
                address_info['jobs'] = []
                jobs = address.jobs.order_by(desc(Job.job_date))

                for job in jobs:
                    job_info = parsing.job_parse(job)
                    address_info['jobs'].append(job_info)

            customer_info['addresses'].append(address_info)

        return customer_info
    else:
        return None


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


def date_cleanup(full_date):
    return_date = ''
    if str(full_date).find('/') > 0:
        mdy = str(full_date).split('/')
        if 0 < int(mdy[0]) < 10 and len(mdy[0]) == 1:
            return_date += '0'
        return_date += str(mdy[0]) + '/'
        if 0 < int(mdy[1]) < 10 and len(mdy[1]) == 1:
            return_date += '0'
        return_date += str(mdy[1]) + '/'
        if len(mdy[2]) == 2 and 0 <= int(mdy[2]) <= 21:
            return_date += '20'
        elif len(mdy[2]) == 2 and 50 <= int(mdy[2]) <= 99:
            return_date += '19'
        return_date += str(mdy[2])
    else:
        # return_date = str(full_date.month) + '/' + str(full_date.day) + '/' + str(full_date.year)
        ymd = str(full_date).split('-')
        return_date = ymd[1] + '/' + ymd[2] + '/' + ymd[0]

    return return_date


def schedule_fetch(crew_name, schedule_date):
    from models import db, Crew, Job, Customer, Address, Service
    from sqlalchemy import and_

    crew_query = db.session.query(Crew).filter(Crew.name == crew_name).first()
    crew_id = crew_query.id

    date_to_query = schedule_date

    jobs = db.session.query(Job)\
        .join(Crew, Address, Customer, Job.services)\
        .filter(and_(Crew.id == crew_id, Job.job_date == date_to_query))\
        .order_by(Job.schedule_position)

    schedule = {
        'crew': crew_name,
        'sched_date': schedule_date,
        'jobs': [],
        'sched_total': 0,
        'compl_total': 0,
    }

    canceled_jobs = 0

    for job in jobs:
        job_info = parsing.job_parse(job)

        if job.address.community:
            job_info['community'] = job.address.community.name
            if job.address.sub_community:
                job_info['sub_community'] = job.address.sub_community.name

        if isinstance(job_info['sched_total'], (int, float)):
            schedule['sched_total'] += job_info['sched_total']
        if isinstance(job_info['compl_total'], (int, float)):
            schedule['compl_total'] += job_info['compl_total']

        if job.job_status is not None:
            if job.job_status == 'D':
                job_info['job_status'] = 'Done'
            elif job.job_status == 'SCH':
                job_info['job_status'] = 'Scheduled'
            elif job.job_status == 'CNCL':
                job_info['job_status'] = 'Canceled'
                canceled_jobs += 1
            elif job.job_status == 'PARTIAL':
                job_info['job_status'] = 'Unfinished'

        schedule['jobs'].append(job_info)

    if canceled_jobs == len(schedule['jobs']) and len(schedule['jobs']) > 0:
        schedule['sched_status'] = 'Canceled'

    return schedule


def get_crew_on_day(date_of_work):
    crews = db.session.query(func.distinct(Crew.name), Crew.jobs).filter(and_(Job.job_date == date_of_work, Job.crew_id == Crew.id)).order_by(Crew.display_num)

    return crews


def get_all_communities():
    communities = db.session.query(Community).order_by(Community.name).all()

    return communities


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


def get_customer(customer_id):
    customer = db.session.query(Customer).get(int(customer_id))
    return customer


def fill_customer_form(customer_id, form):
    customer = db.session.query(Customer).get(customer_id)

    # insert customer name into form
    form.last_name.data = customer.last_name

    # if customer has a first name
    if customer.first_name:
        form.first_name.data = customer.first_name

    if customer.first_name2:
        form.first_name2.data = customer.first_name2

    if customer.last_name2:
        form.last_name2.data = customer.last_name2

    if customer.referral:
        form.referral.data = customer.referral

    if customer.customer_since:
        form.customer_since.data = customer.customer_since

    if customer.customer_notes:
        pass

    return form


def fill_contact_form(customer_id, form):
    customer = db.session.query(Customer).get(customer_id)
    numbers = customer.numbers
    emails = customer.emails

    for num in numbers:
        getattr(form, 'numbers').append_entry()
        form.numbers.entries[-1].number.data = num.number
        if num.number_type:
            form.numbers.entries[-1].number_type.data = num.number_type

    for add in emails:
        getattr(form, 'emails').append_entry()
        form.emails.entries[-1].email.data = add.email

    return form


def fill_address_form(customer_id, form):
    customer = db.session.query(Customer).get(customer_id)
    addresses = customer.addresses

    communities = get_all_communities()

    for address in addresses:
        getattr(form, 'addresses').append_entry()
        form.addresses.entries[-1].address_ln1.data = address.address_ln1
        if address.address_ln2:
            form.addresses.entries[-1].address_ln2.data = address.address_ln2
        form.addresses.entries[-1].city.data = address.city
        form.addresses.entries[-1].zip.data = address.zip
        community_choices = ['---', 'New Community', '---']
        for community in communities:
            community_choices.append(community.name)
        form.addresses.entries[-1].community.choices = community_choices
        sub_community_choices = ['---']
        if address.community:
            sub_community_choices.append('New Sub Community')
            sub_community_choices.append('---')
            # index = form.addresses.entries[-1].community.choices.index(address.community.id, address.community.name)
            # print('index: {}'.format(index))
            form.addresses.entries[-1].community.data = address.community.name
            # form.addresses.entries[-1].community.data = form.addresses.entries[-1].community.choices[index]

            sub_communities = get_sub_communities(address.community_id)
            for subcomm in sub_communities:
                sub_community_choices.append(subcomm.name)

        form.addresses.entries[-1].sub_community.choices = sub_community_choices

        if address.sub_community:
            form.addresses.entries[-1].sub_community.data = address.sub_community.name

        if address.billing is not None and address.billing.lower() != 'self':
            form.addresses.entries[-1].billing.data = address.billing

        if address.billing_type != 'R':
            form.addresses.entries[-1].billing_type.data = address.billing_type

    return form

def get_new_customer_id():
    customer_id = db.session.query(func.max(Customer.id)).first()[0]
    return customer_id


def get_all_crews():
    crews = db.session.query(Crew).all()
    crew_list = []
    for crew in crews:
        crew_list.append((crew.id, crew.name))

    return crew_list
