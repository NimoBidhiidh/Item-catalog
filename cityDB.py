
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# catagories
class AREA(Base):
    __tablename__ = 'Area'

    area_name = Column(String(120), nullable=False)
    id = Column(Integer, primary_key=True)

    #neighborhood = relationship('neighborhood', backref='Area', lazy='dynamic')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'area_name': self.area_name,
            'id': self.id,
        }


class Neighborhood(Base):
    __tablename__ = 'neighborhood'

    nhood_name = Column(String(120), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(120))

    area_name = Column(String(120),  ForeignKey('Area.id'))
    Area = relationship(AREA)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    user = relationship(User, backref="neighborhood")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'nhood_name': self.nhood_name,
            'description': self.description,
            'area_name': self.area_name,
            'id': self.id,
        }


engine = create_engine('sqlite:///city.db')

Base.metadata.create_all(engine)
