from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# set db to connect to Flask by:
def connect_db(app):
    db.app = app
    db.init_app(app)

    #MODELS GO BELOW!

class Customer(db.Model):
    __tablename__= 'customers'

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).all()
    
    @classmethod
    def get_by_community(cls, community):
        return cls.query.filter_by(community=community).all()

    def __repr__(self):
        c = self
        return f"<Customer id={c.id} name= {c.name}"

    id = db.Column(db.Integer,
                    primary_key = True,
                    autoincrement=True)
    
    name = db.Column(db.String(20),
                    nullable = False,
                    unique =True)
                    
    address = db.Column(db.String(35),
                        nullable = False)
    
    community = db.Column(db.String,
                        nullable = True)
    

    def select(self):
        return f"Selected {self.name}"
