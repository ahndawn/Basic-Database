"""Seed file to make sample data for customers db"""

from models import Customer, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

# if table isn't empty, empty it
Customer.query.delete()

# add Customers
anderson = Customer(name="Anderson", address = "104 Ham Rd", community = "Orange City")
dexter = Customer(name="Dexter", address = "783 Killer Ave", community = "Crimson Gardens")
brown = Customer(name="Brown", address = "300 Golden Dr", community = "Orange City")

# Commit--otherwise, thi never gets saved
db.session.commit()