from flask import Flask, render_template, url_for, redirect, g
import sqlite3

app=Flask(__name__)
db_location='var/test.db'

def get_db():
  db = getattr(g, 'db', None)
  if db is None:
    db=sqlite3.connect(db_location)
    g.db = db
    db.text_factory=str
  return db

@app.teardown_appcontext
def close_db_connection(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

def init_db():
  with app.app_context():
    db=get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

@app.route("/")
def index():
  db=get_db()
  db.cursor().execute('insert into Artists (Name,Bio) values ("5 majeur","Good crew")')
  db.commit()
  sql='SELECT * FROM Artists'
  query=db.cursor().execute(sql)
  artists=[]
  for row in query:
    artists.append(row)
  db.close()
  return render_template('index.html',artists=artists)

@app.route("/browse")
def browse():
  return render_template('index.html')

@app.route("/search")
def search():
  return render_template('index.html')

@app.route("/import")
def importing():
  return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
  return "The page you're trying to reach doesn't exist man.", 404

if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)
