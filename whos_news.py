__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / whos_news.py'
__datum__ = '15/02/17'

from dbhelper import DBHelper
from flask import Flask, render_template, request
from lib_common import recentArticlesFromCellar
import requests
# from testcron import runHej
import schedule
import time
from threading import Thread
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk.stem import SnowballStemmer, snowball
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import tree, trigrams, word_tokenize, pos_tag, ne_chunk, ne_chunk_sents
import nltk
from nltk.collocations import *

app = Flask(__name__, static_folder='static')
start_time = time.time()
DB = DBHelper()

@app.route("/")
def home():
    salute = "hej there"
    header = """'Who's News' analyses media websites for information about which persons and organisations are mentioned, when, and in which context."""
    subHeader = """The goal is to transparently connect the dots across media, so users can quickly get an overview of who is being mentioned in the media right now
    and in the past, but also let users drill down into the data in a granular manner and subscribe to results via RSS or the API.
    The curious guest is pointed to <a href=''>the FAQ</a>, the verbose guest is pointed to <a href=''>the forum</a>. """

    return render_template("base.html", salute=salute, header=header, subHeader=subHeader)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('base.html', header="Error: {}".format(error)), 404



@app.route("/dash/recent-articles")
def recentArticles():
    """ Overview of recent article by paper/section/1 hour/3 hours/24 hours/week
    :return:
    """
    recentArticlesDict =recentArticlesFromCellar()
    waitingCount = DB.countArticlesQueNotSeen()
    header = """Antal tekster analyseret det seneste døgn/uge"""
    subHeader = """Antal tekster i kø: <span class="badge">{}</span>""".format(waitingCount[0][0])

    return render_template("admin/recent-articles.html", header=header, subHeader=subHeader, recentArticles=sorted(recentArticlesDict.items()))

@app.route("/medium")
@app.route("/medium/<mediaName>")
@app.route("/medium/<mediaName>/<section>")
def mediaNames(mediaName="", section=""):


    try:
        country = request.args.get('country', "DK")
    except Exception as e:
        pass

    if mediaName == "" and section == "":
        mediaName = "Media - main page"
    elif section != "":
        mediaName = "{} - {}".format(mediaName, section)
    else:
        mediaName = mediaName


    return render_template("base.html", header=mediaName)


@app.route("/name")
@app.route("/name/<namedEntity>")
def namedEntities(namedEntity=""):

    fuzzy = ""
    subText = ""
    ne_data = []
    mergedDict = {}
    subHeader = ""
    try:
        country = request.args.get('country', "DK")
        fuzzy = request.args.get('fuzzy', "False", type=str)
    except Exception as e:
        subText = ""
        fuzzyText = ""

    try:
        if fuzzy == "True":
            namedEntity = namedEntity.replace("'", " ").replace('"', " ").replace("%", " ").replace(";", " ").replace("\\", " ")
            ne_data = DB.getNamedEntityFuzzy("%{}%".format(namedEntity) )
            for article in ne_data:
                mergedDict["{}_{}".format(article[10],article[0])] = {"date" : article[9], "ne": article[1], "media" : article[7], "section" : article[6], "link": article[8],
                                           "ToC": article[2], "HeC": article[3], "TaC": article[4], "shape": article[5],
                                           "Facebook_share_count": 0, "Facebook_comment_count": 0, "GooglePlusOne": 0, "Twitter" : 0,
                                           'LinkedIn' : 0, 'Pinterest' : 0, 'StumbleUpon': 0, "Facebook_like_count" : 0}

                sm_data = DB.getSocialMediaDataForArticleID(article[10])

                for item in sorted(sm_data, reverse=True):
                    # print(item)
                    if item[0] == sorted(sm_data, reverse=True)[0][0]:
                        mergedDict["{}_{}".format(article[10],article[0])].update( {item[1] : item[2]} )

            # get dif type of names found
            names = [ne[1] for ne in sorted(ne_data)]
            subText = " (via <em>udvidet</em> søgning)."
            subHeader = "Variationer: <em>{}</em>".format(", ".join(set(names)) ) # add anchor text

        else:
            if namedEntity != "":
                ne_data = DB.getNamedEntityExact(namedEntity)
                for article in ne_data:
                    mergedDict["{}_{}".format(article[10],article[0])] = {"date" : article[9],  "ne": article[1], "media" : article[7], "section" : article[6], "link": article[8],
                                               "ToC": article[2], "HeC": article[3], "TaC": article[4], "shape": article[5],
                                               "Facebook_share_count": 0, "Facebook_comment_count": 0, "GooglePlusOne": 0, "Twitter" : 0,
                                               'LinkedIn' : 0, 'Pinterest' : 0, 'StumbleUpon': 0, "Facebook_like_count" : 0}

                    sm_data = DB.getSocialMediaDataForArticleID(article[10])

                    for item in sorted(sm_data, reverse=True):
                        if item[0] == sorted(sm_data, reverse=True)[0][0]:
                            mergedDict["{}_{}".format(article[10],article[0])].update( {item[1] : item[2]} )
            # else get a list of most seen names.

    except Exception as e:
        pass

    header = """{} artikler fundet for: <span class="label label-success">{}</span>""".format(len(ne_data), namedEntity)

    return render_template("namedEntity.html", header=header, ne_data=mergedDict, namedEntity=namedEntity, subHeader=subHeader, subText=subText)

    # try:
    #     intervalTime = request.args.get('tidsInterval', 24)

@app.route("/om-projektet")
def omProjektet():

    title = "Om projektet"

    overviewTitle = "Om projektet Hotte Navne"

    return render_template("om-projektet.html", header=title, overviewTitle=overviewTitle)


@app.template_filter()
def truncateLinks(externallink): # date = datetime object.
    exlink = str(externallink.replace("http://", "").replace("https://", "").replace("www.", ""))
    name = exlink.split("/")[0]
    back = exlink[len(exlink) - (30 - len(name)):]
    return "{}...{}".format(name, back)


# Mission statement
# donate
# get rss
# forum
# data og sporing - GA
# try it yourself - indsæt link og vi henter data + sammenligning med andre.
# how to use

# def mySchedule():
#     schedule.every(10).seconds.do(runHej)
#
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

if __name__ == "__main__":
    # t = Thread(target=mySchedule)
    # t.start()
    # print("Start time: " + str(start_time))
    app.run()