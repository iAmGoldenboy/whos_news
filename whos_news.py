__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / whos_news.py'
__datum__ = '15/02/17'

from flask import Flask, render_template

app = Flask(__name__, static_folder='static')

@app.route("/")
def home():
    salute = "hej there"
    val = "dfdf"
    return render_template("base.html", salute=salute)


if __name__ == "__main__":

    app.run()