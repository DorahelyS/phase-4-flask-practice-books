from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# write your models here!

#independent model 1
class Author(db.Model, SerializerMixin):
    #naming the table
    __tablename__ = 'authors'

    #creating colunmns
    id = db.Column(db.Integer, primary_key=True)
    #cannot be null meaning name has entered has to be valid
    name = db.Column(db.String, nullable=False)
    pen_name = db.Column(db.String)

    ##creating ORM realtionship which is through the model
    #author = db.relationship('Author' , back_populates = 'books')
    books = db.relationship('Book' , back_populates='author')

    #adding serialzation rules, tuple - don't forget trailing comma!
    serialize_rules = ('-books.author', )

    #adding validation
    #NO VALIDATION NEEDED BASED ON README


#independent model 2
class Publisher(db.Model, SerializerMixin):
    #naming the table
    __tablename__ = 'publishers'

    #creating colunmns
    id = db.Column(db.Integer, primary_key=True)
    #cannot be null meaning name has entered has to be valid
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer, nullable=False)

    ##creating ORM realtionship which is through the model
    #publisher = db.relationship('Publisher' , back_populates = 'books')
    books = db.relationship('Book' , back_populates='publisher')

    #adding serialzation rules, tuple - don't forget trailing comma!
    serialize_rules = ('-books.publisher', )

    #adding validation
    #founding_year must be between 1600 and the current year
    @validates('founding_year')
    def validate_founding_year(self, key, founding_year):
        #if founding_year >= 1600 and founding_year <= 2024:
        if 1600 <= founding_year <= 2024:
            return founding_year
        else:
            raise ValueError("year is not correct")
    

#dependent model 3 - meaning it relies on both model 1 & 2 
#don't forget to cascade deletes since it is a dependent model!!
class Book(db.Model, SerializerMixin):
    #naming the table
    __tablename__ = 'books'

    #creating colunmns
    id = db.Column(db.Integer, primary_key=True)
    #cannot be null meaning name has entered has to be valid & must be unique
    title = db.Column(db.String, nullable=False, unique=True)
    page_count = db.Column(db.Integer)

    #creating table relationship - grabbing table name to create relationships
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))

    #creating ORM realtionship which is through the model
    author = db.relationship('Author', back_populates='books')
    publisher = db.relationship('Publisher', back_populates='books')

    #adding serilazation rules to stop recursion
    serialize_rules = ('-author.books', '-publisher.books')

    #adding validation
    #page_count must be greater than 0
    @validates('page_count')
    def validate_page_count(self, key, page_count):
        if page_count <= 0:
            raise ValueError('pages must be greater than zero')
        else:
            return page_count

'''
or
 @validates('page_count')
    def validate_page_count(self, key, page_count):
        if page_count >= 0:
            return page_count
        else:
            raise ValueError('pages must be greater than zero')

'''

