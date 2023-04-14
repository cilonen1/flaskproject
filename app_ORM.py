from flask import Flask, abort, request
from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()

db = SQLAlchemy(app)

class QuoteModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   author = db.Column(db.String(32), unique=False)
   text = db.Column(db.String(255), unique=False)

   def __init__(self, author, text):
       self.author = author
       self.text  = text

   def __repr__(self):
       return f"author: {self.author} q: {self.text[:10]}"

   def to_dict(self):
       d = dict()
       for column in self.__table__.columns:
           d[column.name] = str(getattr(self, column.name))
       return d

#db.create_all() запускается 1 раз

@app.route("/quotes_db")
def get_quotes():
    quotes = QuoteModel.query.all()
    return [q.to_dict() for q in quotes], 200

@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id):
    quotes = QuoteModel.query.get(quote_id)
    if quotes is None:
        return f"Quote with id={quote_id} not found", 404
    return quotes.to_dict(), 200

@app.route("/filter/<name>")
def filter_query(name):
    quotes = QuoteModel.query.filter_by(author=name).all()
    if quotes is None:
        return f"Quote with id={quote_id} not found", 404
    return [q.to_dict() for q in quotes], 200

@app.route("/quotes", methods=['POST'])
def create_quote():
    data = request.json
    q = QuoteModel(*tuple(data.values()))
    db.session.add(q)
    db.session.commit()
    saved_q = QuoteModel.query.get(q.id)
    return saved_q.to_dict(), 200

@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def change_quote(quote_id):
    data = request.json
    q = QuoteModel.query.get(quote_id)
    q.author = data['author']
    q.text = data['text']
    db.session.add(q)
    db.session.commit()
    q = QuoteModel.query.get(quote_id)
    return q.to_dict(), 200

@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    q = QuoteModel.query.get(quote_id)
    if q:
        db.session.delete(q)
        db.session.commit()
        return f"Quote with id {quote_id} is deleted.", 200
    return f"Quote with id={quote_id} not found", 404

if __name__ == "__main__":
   app.run(debug=True)