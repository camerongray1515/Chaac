from flask import Flask, render_template, abort, request, redirect
from api import api

app = Flask(__name__)
app.secret_key = 'changemetemp7qWYsGtL5fDHFMhG'
app.register_blueprint(api)
app.config["PLUGIN_REPOSITORY"] = "../plugin_repo/"

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/clients/")
def clients():
	return render_template("clients.html")

@app.route("/groups/")
def groups():
    return render_template("groups.html")

@app.route("/plugins/")
def plugins():
    return render_template("plugins.html")

@app.route("/schedule/")
def schedule():
    return render_template("schedule.html")

if __name__ == "__main__":
    app.run(debug=True)
