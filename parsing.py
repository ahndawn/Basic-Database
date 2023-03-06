def customer_parse(customers):
    customer_info = {
        'id': customers.id,
        'last_name': customers.last_name,
        'last_name2': customers.last_name2,
        'first_name': customers.first_name,
        'first_name2': customers.first_name2,
    }

    if customers.numbers:
        customer_info['numbers'] = []
        for number in customers.numbers:
            number_info = phone_number_parse(number)
            customer_info['numbers'].append(number_info)

    if customers.emails:
        customer_info['emails'] = []
        for email in customers.emails:
            email_info = email_parse(email)
            customer_info['emails'].append(email_info)

    return customer_info


def address_parse(address):
    address_info = {
        'address_ln1': address.address_ln1,
        'address_ln2': address.address_ln2,
        'city': address.city,
        'zip': address.zip,
        'customer_id': address.customer_id,
        'customer': address.customers.last_name,
        'community_id': address.community_id,
        'sub_community_id': address.sub_community_id,
        'address_note1': address.address_note1,
        'address_note2': address.address_note2,
        'zone': address.zone,
        'billing': address.billing,
        'billing_type': address.billing_type,
        'directions': address.directions,
        'office_notes': address.office_notes,
    }
    if address.community:
        address_info['community'] = address.community.name
        if address.sub_community:
            address_info['sub_community'] = address.sub_community.name

    return address_info


def job_parse(job):
    job_info = {
        'id': job.id,
        'customer_id': job.customer_id,
        'customer': job.customers.last_name,
        'address_id': job.address_id,
        'address': job.address.address_ln1,
        'city': job.address.city,
        'crew_id': job.crew_id,
        'job_date': job.job_date.strftime('%m/%d/%y'),
        'job_status': job.job_status,
        'pay_status': job.pay_status,
        'pay_date': job.pay_date,
        'compl_notes': job.compl_notes,
        'time_constraint': job.time_constraint,
        'schedule_position': job.schedule_position,
        'time_scheduled': job.time_scheduled,
        'job_type': job.job_type
    }

    if job.address.address_ln2:
        job_info['address'] += ' ({})'.format(job.address.address_ln2)
    if job.crew:
        job_info['crew'] = job.crew.name



    job_info['sched_services'] = []
    job_info['sched_types'] = []
    job_info['sched_total'] = 0

    job_info['compl_services'] = []
    job_info['compl_types'] = []
    job_info['compl_total'] = 0

    for service in job.services:
        service_info = service_parse(service)
        if service_info['status'] == 'SCHED':
            job_info['sched_services'].append(service_info)
            if isinstance(service_info['price'], int) and job.job_type != 'EST' and service.svc_type != 'EST' and service.work_type != 'EST' and service.svc_type != 'TIP':
                job_info['sched_total'] += service_info['price']
            if service_info['work_type'] not in job_info['sched_types']:
                job_info['sched_types'].append(service_info['work_type'])
        elif service_info['status'] == 'COMPL':
            job_info['compl_services'].append(service_info)
            if isinstance(service_info['price'], int) and job.job_type != 'EST' and job.job_type != 'NC' and service.svc_type != 'EST' and service.work_type != 'EST' and service.svc_type != 'TIP' and service.svc_type != 'NC' and service.work_type != 'NC':
                job_info['compl_total'] += service_info['price']
            if service_info['work_type'] not in job_info['compl_types']:
                job_info['compl_types'].append(service_info['work_type'])

    if len(job_info['sched_types']) == 1 and (job_info['sched_types'][0] == 'EST' or job_info['sched_types'][0] == 'NC'):
        job_info['sched_job_type'] = job_info['sched_types'][0]
    else:
        job_info['sched_job_type'] = 'WORK'

    if len(job_info['compl_types']) == 1 and (job_info['compl_types'][0] == 'EST' or job_info['compl_types'][0] == 'NC'):
        job_info['compl_job_type'] = job_info['compl_types'][0]
    else:
        job_info['compl_job_type'] = 'WORK'

    return job_info


def service_parse(service):
    service_info = {
        'id': service.id,
        'job_id': service.job_id,
        'work_type': service.work_type,
        'svc_type': service.svc_type,
        'svc': service.svc,
        'price': service.price,
        'status': service.status,
    }

    if service.status == 'SCHED':
        if service.work_type == 'EST':
            service.price = '?'
        elif service.work_type == 'NC':
            service.price = 0

    if service.price != '' and service.price != ' ' and service.price != '?':
        try:
            service_info['price'] = int(service.price)
        except Exception:
            service_info['price'] = '?'
    else:
        service_info['price'] = '?'

    return service_info


def parse_crew(crew):
    crew_info = {
        'id': crew.id,
        'name': crew.name,
        'crew_status': crew.crew_status
    }

    return crew_info


def parse_community(community):
    community_info = {
        'id': community.id,
        'name': community.name,
    }

    return community_info


def parse_sub_community(sub_community):
    sub_community_info = {
        'id': sub_community.id,
        'name': sub_community.name,
        'community_id': sub_community.community_id,
        'community': sub_community.community.name,
    }

    return sub_community_info


def phone_number_parse(phone_number):
    phone_number_info = {
        'id': phone_number.id,
        'customer_id': phone_number.customer_id,
        'customer': phone_number.customers.last_name,
        'number': phone_number.number,
        'number_type': phone_number.number_type,
    }

    return phone_number_info


def email_parse(email):
    email_info = {
        'id': email.id,
        'customer_id': email.customer_id,
        'customer': email.customers.last_name,
        'email': email.email,
    }

    return email_info


def parse_payment(payment):
    payment_info = {
        'id': payment.id,
        'customer_id': payment.customer_id,
        'customer': payment.customers.last_name,
        'date_processed': payment.date_processed,
        'type': payment.type,
        'ref': payment.ref,
        'amount': payment.amount,
    }


def parse_note(note):
    note_info = {
        'id': note.id,
        'note': note.note,
    }