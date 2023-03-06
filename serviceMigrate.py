
from models import db, Job, Service
from sqlalchemy import or_
import datetime

jobs = db.session.query(Job).all()

for job in jobs:
    job_date = str(job.job_date)

    #  01 2 34 5 6789
    #  04/15/2021
    new_date = datetime.datetime.strptime(str(job_date) + ' 00:00', '%Y-%m-%d %H:%M')

    job.job_date = new_date

db.session.commit()
