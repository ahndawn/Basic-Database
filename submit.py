
from models import db, Customer, PhoneNumber, Email, Address, Community, SubCommunity

def get_community_by_name(community_name):
    community = db.session.query(Community).filter(Community.name == community_name).first()

    return community

def submit_customer_info(customer_id, edit_customer_form):
    customer = db.session.query(Customer).get(customer_id)
    form = edit_customer_form

    # primary last name
    # if form.names.entries[0].last_name.data != customer.last_name:
    if form.last_name.data != customer.last_name:
        customer.last_name = form.last_name.data

    # primary first name
    # if form.names.entries[0].first_name.data and form.names.entries[0].first_name.data != customer.first_name:
    if form.first_name.data and form.first_name.data != customer.first_name:
        customer.first_name = form.first_name.data
    elif not form.first_name.data and customer.first_name is not None:
        customer.first_name = None

    # secondary name
    # if len(form.names.entries) > 1:
    # secondary last name
    if form.last_name2.data and form.last_name2.data != customer.last_name2:
        customer.last_name2 = form.last_name2.data
    elif not form.last_name2.data and customer.last_name2 is not None:
        customer.last_name2 = None

    # secondary first name
    if form.first_name2.data and form.first_name2.data != customer.first_name2:
        customer.first_name2 = form.first_name2.data
    elif not form.first_name2.data and customer.first_name2 is not None:
        customer.first_name2 = None

    # referral
    if form.referral.data and form.referral.data != customer.referral:
        customer.referral = form.referral.data
    elif not form.referral.data and customer.referral is not None:
        customer.referral = None

    # customer since
    if form.customer_since.data and form.customer_since.data != customer.customer_since:
        customer.customer_since = form.customer_since.data
    elif not form.customer_since.data and customer.customer_since is not None:
        customer.customer_since = None

    db.session.commit()


def submit_contact_info(customer_id, edit_contact_form):
    def replace_phone_vals(num_vals):
        x = 0
        while x < num_vals:
            customer.numbers[x].number = form.numbers.entries[x].number.data
            customer.numbers[x].number_type = form.numbers.entries[x].number_type.data
            x += 1

    def replace_email_vals(num_vals):
        x = 0
        while x < num_vals:
            customer.emails[x].email = form.emails.entries[x].email.data
            x += 1

    customer = db.session.query(Customer).get(customer_id)
    form = edit_contact_form

    stored_nums = customer.numbers.count()
    form_nums = len(form.numbers.entries)

    stored_emails = customer.emails.count()
    form_emails = len(form.emails.entries)

    print('Numbers - Stored: {}, Form: {}'.format(stored_nums, form_nums))
    print('Emails - Stored: {}, Form: {}'.format(stored_emails, form_emails))

    # if amount of numbers in form is less than in DB
    # delete excess and replace values
    if stored_nums > form_nums:
        diff = stored_nums - form_nums
        x = 0
        while x < diff:
            number = customer.numbers[-1]
            db.session.delete(number)
            db.session.flush()
            x += 1
    elif form_nums > stored_nums:
        diff = form_nums - stored_nums
        x = 0
        while x < diff:
            new_number = PhoneNumber()
            customer.numbers.append(new_number)
            x += 1
    replace_phone_vals(form_nums)

    if form_emails > stored_emails:
        diff = form_emails - stored_emails
        x = 0
        while x < diff:
            new_email = Email()
            customer.emails.append(new_email)
            x += 1
    replace_email_vals(form_emails)

    db.session.commit()


def submit_address_info(customer_id, edit_address_form):
    customer = db.session.query(Customer).get(customer_id)
    form = edit_address_form

    stored_addresses = customer.addresses.count()
    form_addresses = len(form.addresses.entries)

    # if more addresses in form than in database (new address entered)
    if form_addresses > stored_addresses:
        for x in range(form_addresses-stored_addresses):
            new_address = Address()
            customer.addresses.append(new_address)

    x = 0
    while x < form_addresses:
        customer.addresses[x].address_ln1 = form.addresses.entries[x].address_ln1.data
        customer.addresses[x].address_ln2 = form.addresses.entries[x].address_ln2.data
        customer.addresses[x].city = form.addresses.entries[x].city.data
        customer.addresses[x].zip = form.addresses.entries[x].zip.data

        if form.addresses.entries[x].community.data != '---':
            if form.addresses.entries[x].community.data != 'New Community':
                community = get_community_by_name(form.addresses.entries[x].community.data)
                customer.addresses[x].community_id = community.id
            elif form.addresses.entries[x].community.data == 'New Community' and form.addresses.entries[
                x].new_community.data != '' and form.addresses.entries[x].new_community.data is not None:
                community = Community()
                community.name = form.addresses.entries[x].new_community.data
                db.session.add(community)
                db.session.flush()
                customer.addresses[x].community_id = community.id

            if form.addresses.entries[x].sub_community.data != '---':
                if form.addresses.entries[x].sub_community.data != 'New Sub Community':
                    sub_community = community.subcommunities.filter(
                        SubCommunity.name == form.addresses.entries[x].sub_community.data).first()
                    customer.addresses[x].sub_community_id = sub_community.id
                elif form.addresses.entries[x].sub_community.data == 'New Sub Community' and form.addresses.entries[
                    x].new_sub_community.data != '' and form.addresses.entries[x].new_sub_community.data is not None:
                    sub_community = SubCommunity()
                    sub_community.name = form.addresses.entries[x].new_sub_community.data
                    sub_community.community_id = community.id
                    db.session.add(sub_community)
                    db.session.flush()
                    customer.addresses[x].sub_community_id = sub_community.id

        else:
            customer.addresses[x].community_id = None
        # TODO Community & SubCommunity Edits
        # TODO Address Notes

        if form.addresses.entries[x].billing.data != 'Leave Bill':
            customer.addresses[x].billing = form.addresses.entries[x].billing.data
        else:
            customer.addresses[x].billing = None

        customer.addresses[x].billing_type = form.addresses.entries[x].billing_type.data

        x += 1

    db.session.commit()


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