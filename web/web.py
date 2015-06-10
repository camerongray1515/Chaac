from flask import Flask, render_template, abort, request, redirect
from api import api

app = Flask(__name__)
app.secret_key = 'changemetemp7qWYsGtL5fDHFMhG'
app.register_blueprint(api)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/clients/")
def clients():
	return render_template("clients.html")

@app.route("/groups/")
def groups():
    return render_template("groups.html")

if __name__ == "__main__":
    app.run(debug=True)
