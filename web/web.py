from flask import Flask, render_template, abort, request, redirect

app = Flask(__name__)
app.secret_key = 'changemetemp7qWYsGtL5fDHFMhG'

@app.route("/")
def index():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True)
