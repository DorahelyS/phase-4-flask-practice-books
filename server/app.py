#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Author, Publisher, Book


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

#home page
@app.get('/')
def index():
    return "Hello world"


# write your routes here!
#GET /authors/:id
#Returns an author with the matching id. If there is no author, returns a message that the 
#author could not be found along with a 404.

@app.route('/authors/<int:id>', methods = ['GET'])
def author_by_id(id):
    author = Author.query.filter(Author.id == id).first()
    #have to include a conditional if no author is found
    #first if auther even exist create response that includes the auther in JSON
    if author:
        response = make_response(
            #to_dict turns into a dictionary which is needed for JSON
            #remember to_dict can only be called on a single object which is the case here
             #since only looking for author that matches that id no need to convert
            author.to_dict(),
            200
        )
    else:
        response = make_response(
            #has to be an object
            {"error": "author could not be found"},
            404
        )

    return response


#DELETE /author/:id
#Deletes the author and all associated books from the database. Returns 204 if the author 
#was successfully deleted or 404 and an appropriate message if that author could not be found.
#COULD ADD IT IN THE GET METHOD AND COMBINE BOTH GET & DELETE ??
@app.route('/authors/<int:id>', methods = ['DELETE'])
def delete_author_by_id(id):
    author = Author.query.filter(Author.id == id).first()
    #have to include a conditional if no author is found
    #first if auther even exist create response that includes the auther in JSON
    #if we do find teh author need to cascade delete!
    #need to deleted all the associated books
    if author:
        #before deleted author deleting associated books - but first I need to find
        #the associated books
        associated_books = Book.query.filter(Book.author_id == id).all()
        #can't delete all technically - need to deleted each one
        for associated_book in associated_books:
            db.session.delete(associated_book)

        #now deleting original author
        db.session.delete(author)
        db.session.commit()

        response = make_response(
            {},
            204
        )
    else:
        response = make_response(
            #has to be an object
            {"error": "author could not be found"},
            404
        )

    return response


'''
#IF I DID NOT HAVE A POST & IT WAS JUST A GET
#GET /books
@app.route('/books', methods = ['GET'])
def books():
    #need to hit the db to get list of all the campers
    books = Book.query.all()
    #need to make it a dict so that it can become json 
    #since it it currently a list going to use list comprehension to call on each object
    #since to_dict can only be called on one object not a list
    books_dict = [book.to_dict() for book in books]

    #can write like this too:
    #books_dict = []
    #for book in books:
        #books_dict.append(book.to_dict(rules = ('-author', '-publisher')))
    #creating response
    response = make_response(
        books_dict,
        200
    )
    return response

'''

#GET /books
@app.route('/books', methods = ['GET', 'POST'])
def books():
    #making another if else since if this is a get then do this 
    if request.method == 'GET':
        #need to hit the db to get list of all the campers
        books = Book.query.all()
        #need to make it a dict so that it can become json 
        #since it it currently a list going to use list comprehension to call on each object
        #since to_dict can only be called on one object not a list
        books_dict = [book.to_dict(rules = ('-author', '-publisher')) for book in books]

        #can write like this too:
        #books_dict = []
        #for book in books:
            #books_dict.append(book.to_dict(rules = ('-author', '-publisher')))
        #creating response
        response = make_response(
            books_dict,
            200
        )
    #have to use elif not else!
    elif request.method == 'POST':
        #creat error handlingwith try/except
        try:
            #now to post - line line gets the info from the front end
            form_data = request.get_json()
            #now creating new book object
            new_book = Book(
                title = form_data['title'],
                page_count = form_data['page_count'],
                author_id = form_data['author_id'],
                publisher_id = form_data['publisher_id']
                )
            db.session.add(new_book)
            db.session.commit()

            response = make_response(
                new_book.to_dict(),
                201
            )

        except ValueError:
            response = make_response(
                {"error": "not found"},
                400
            )

    return response

'''
#POST /books
#Creates a new book. The book must belong to an author and a publisher. Return the new book details like so:
#ADDING TO GET BOOKS METHOD 
@app.post('/books')
def post_book():
    try: 
        data = request.get_json() 
        new_book = Book(title=data['title'], 
                        page_count=data['page_count'], 
                        author_id=data['author_id'], 
                        publisher_id=data['publisher_id']
                    )
        db.session.add(new_book)
        db.session.commit()
        return make_response(new_book.to_dict(), 201)
    except Exception:
        return make_response({'error': Exception.with_traceback}, 406)

'''
#GET /publishers/:id
#Returns a publisher with the matching id. If there is no publisher, returns a message that 
#the publisher could not be found along with a 404.
@app.route('/publishers/<int:id>', methods = ['GET'])
def publisher_by_id(id):
    publisher = Publisher.query.filter(Publisher.id == id).first()
    #have to include a conditional if no publisher is found
    #first if auther even exist create response that includes the publisher in JSON
    if publisher:
        response = make_response(
            #to_dict turns into a dictionary which is needed for JSON
            #remember to_dict can only be called on a single object which is the case here
             #since only looking for author that matches that id no need to convert
            publisher.to_dict(),
            200
        )
    else:
        response = make_response(
            #has to be an object
            {"error": "publisher could not be found"},
            404
        )

    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
