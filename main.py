from flask import Flask, render_template, url_for, redirect
app=Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html')

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
