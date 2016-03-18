from Base import Base


class User(Base):
    __tablename__ = 'User'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    ID = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    ip_address = Column(String(255), nullable=True)
    

    def __repr__(self):
        return "<User(ID='%s', username='%s', ip_address='%s')>" % (self.ID, self.username, self.ip_address)

