from flask import Flask, abort, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'app.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class AuthorModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(32), unique=False)
   surname = db.Column(db.String(32), unique=False)
   quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic',  cascade="all, delete-orphan")

   def __init__(self, name, surname):
       self.name = name
       self.surname = surname

   def auth_to_dict(self):
       d = dict()
       for column in self.__table__.columns:
           d[column.name] = str(getattr(self, column.name))
       return d


class QuoteModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
   quote = db.Column(db.String(255), unique=False)

   def __init__(self, author, quote):
       self.author_id = author.id
       self.quote = quote

   def to_dict(self):
       d = dict()
       for column in self.__table__.columns:
           d[column.name] = str(getattr(self, column.name))
       d['author'] = self.author.auth_to_dict()# author берется по ключу из 21й строчки(backref)
       return d

@app.route("/quotes_db")
def get_quotes():
    quotes = AuthorModel.query.all()
    return [q.to_dict() for q in quotes], 200

@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id):
    quotes = QuoteModel.query.get(quote_id)
    if quotes is None:
        return f"Quote with id={quote_id} not found", 404
    return quotes.to_dict(), 200

@app.route("/authors", methods=["POST"])
def create_author():
       author_data = request.json
       author = AuthorModel(author_data["name"], author_data["surname"])
       db.session.add(author)
       db.session.commit()
       return author.auth_to_dict(), 201

@app.route("/authors/<int:auth_id>/quote", methods=["POST"])
def add_quote(auth_id):
       quote_data = request.json
       author = AuthorModel.query.get(auth_id)
       quote = QuoteModel(author, quote_data["book"])
       db.session.add(quote)
       db.session.commit()
       return quote.to_dict(), 201

if __name__ == "__main__":
   app.run(debug=True)