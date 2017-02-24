__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / whos_news.py'
__datum__ = '15/02/17'

from dbhelper import DBHelper
from flask import Flask, render_template, request, url_for, redirect
from lib_common import recentArticlesFromCellar, getKey2nd
from lib_analysis import getAnalytics
from lib_graphics import pieChart, pieChart2, testpie
from collections import Counter
import stats
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
    # search through the X amount of names we have on stack extracted from X articles since X date
    # add numbers for how many yesterday

    salute = "hej there"
    header = """'Who's News' analyses media websites for information about which persons and organisations are mentioned, when, and in which context."""
    subHeader = """The goal is to transparently connect the dots across media, so users can quickly get an overview of who is being mentioned in the media right now
    and in the past, but also let users drill down into the data in a granular manner and subscribe to results via RSS or the API.
    The curious guest is pointed to <a href=''>the FAQ</a>, the verbose guest is pointed to <a href=''>the forum</a>. """

    # find your pulse (practicality)
    # or grab a scorecard (gamification)

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



@app.route("/jam/", methods=['GET', 'POST'])
@app.route("/jam/<named>")
def jam(named=""):

    if request.method == 'POST':
        namedEnt = request.form['namedEnt']
        return redirect( "{}{}".format(url_for('jam'), namedEnt) )
    else:

        return render_template("jam-test.html", header="Are you looking for - {}".format(named))

@app.route("/name/", methods=['GET', 'POST'])
@app.route("/name/<namedEntity>" )
def namedEntities(namedEntity=""):


    if request.method == 'POST':
        namedEnt = request.form['searchTerm']
        check = ""
        fuzz = ""
        try:
            fuzz = request.form['fuzzy']
            print(fuzz)
            fuzz = "?fuzzy=True"
        except Exception as e:
            pass
        return redirect( "{}{}{}".format(url_for('namedEntities'), namedEnt, fuzz) )

    else:

        fuzzy = ""
        subText = ""
        ne_data = []
        mergedDict = {}
        subHeader = ""
        isFuzzy = False
        analytics = ""
        shortNames = ""
        ne_id = ""
        try:
            fuzzy = request.args.get('fuzzy', "False", type=str)
        except Exception as e:
            pass

        try:
            if fuzzy == "True":
                isFuzzy = True
                namedEntity = namedEntity.replace("'", " ").replace('"', " ").replace("%", " ").replace(";", " ").replace("\\", " ")
                ne_data = DB.getNamedEntityFuzzy("%{}%".format(namedEntity) )
                for article in ne_data:
                    mergedDict["{}_{}".format(article[10],article[0])] = {"ne_id": article[0], "date" : article[9], "ne": article[1], "media" : article[7], "section" : article[6], "link": article[8],
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
                subText = """ (* via <span class="glyphicon glyphicon-magnet" aria-label="Extended 'Magnet' Search" aria-hidden="true"></span> MAGNET search)."""
                # subHeader = """Variationer: {}""".format(", ".join(  {ids: datas for ids, datas in Counter(names).items()}  ) ) # add anchor text
                shortNames = ", ".join(["""<a href="{}" title="{} articles">{}</a>""".format(ids, datas, ids) for ids, datas in sorted(Counter(names).items(), reverse=True, key=getKey2nd)] )
                if len(names) > 5:
                    shortNames = "{} + {} more variations".format(", ".join(["""<a href="{}" title="{} articles">{}</a>""".format(ids, datas, ids) for ids, datas in sorted(Counter(names).items(), reverse=True, key=getKey2nd)[:5]] ), len(set(names))-5 )

                subHeader = " ".join(["""<a href="{}"><span style="display: inline-block;" class="label label-success">{}  <span class="badge">{}</span></span></a>""".format(ids, ids, datas) for ids, datas in sorted(Counter(names).items(), reverse=True, key=getKey2nd)] )
                #      <a href=""><button class="btn btn-primary" type="button">{} <span class="badge">{}</span></button></a>
                subHeader = """<p>Too many results? Try <a href="{}">without extended magnet search</a>.</p> <br>{}""".format(namedEntity, subHeader)
            else:
                if namedEntity != "":
                    ne_data = DB.getNamedEntityExact(namedEntity)
                    for article in ne_data:
                        mergedDict["{}_{}".format(article[10],article[0])] = {"ne_id": article[0], "date" : article[9],  "ne": article[1], "media" : article[7], "section" : article[6], "link": article[8],
                                                   "ToC": article[2], "HeC": article[3], "TaC": article[4], "shape": article[5],
                                                   "Facebook_share_count": 0, "Facebook_comment_count": 0, "GooglePlusOne": 0, "Twitter" : 0,
                                                   'LinkedIn' : 0, 'Pinterest' : 0, 'StumbleUpon': 0, "Facebook_like_count" : 0}

                        sm_data = DB.getSocialMediaDataForArticleID(article[10])

                        for item in sorted(sm_data, reverse=True):
                            if item[0] == sorted(sm_data, reverse=True)[0][0]:
                                mergedDict["{}_{}".format(article[10],article[0])].update( {item[1] : item[2]} )
                # else get a list of most seen names.
                    subHeader = """<p>Too few results? Try <a href="{}?fuzzy=True">the extended magnet search</a>.</p> <br>{}""".format(namedEntity, subHeader)

        except Exception as e:
            pass

        # this should be added to a database and if more than a few hours old, then do new calculation
        # perhaps also do it for time periods on week and month basis
        analytics = getAnalytics(mergedDict)

        # [{"label":"Category A", "value":20},
		 #          {"label":"Category B", "value":50},
		 #          {"label":"Category C", "value":30}];

        pieNames = ["#firstpie"]

        # print("anni", analytics)
        # for data in analytics:
        #     print(data[0], data[1].get("perc"))
        #     print({"label": "{} {}% ({})".format(data[0], data[1].get("perc"), data[1].get("count")), "value" : float("{}".format(data[1].get("perc")))} )
        pieData = [{"label": "{} {}% ({})".format(data[0], data[1].get("perc"), data[1].get("count")), "count" : int("{}".format(int(data[1].get("count"))))}  for data in analytics]

        # print(pieChart("firstpie", analytics, "#firstpie"))
        d3js = [
            # {"id" : "firstpie",
            #      "chart" : pieChart("firstpie", pieData, "#firstpie", width=100, height=100),
            #      "title": "Pr. Section",
            #      "description": "This is desc",
            #      "legend" : " ".join(["<li>{} {}% ({})</li> ".format(data[0], data[1].get("perc"), data[1].get("count"))  for data in analytics]) },

                {"chart" : testpie(pieData),
                 "title" : "title",
                 "description": "description",
                 "id" : "chart"
                }
            ,
                # {"chart" : pieChart2("secondPie", pieData, "#secondPie"),
                # "id" : "secondPie",
                # "title" : "Second Pie",
                # "description" : "Descondos txt"}
                ]

        # se og på om der er vækst  - del puljen i to til at starte med - derefter kan man gå pr. uge eller måned
        asterisk = ""
        if isFuzzy:
            asterisk = "*"

        header = """{} artikler fundet for: <span class="label label-success">{}{}</span>""".format(len(ne_data), namedEntity, " {}".format(asterisk))

        return render_template("namedEntity.html", header=header, ne_data=mergedDict, ne=namedEntity,
                               subHeader="<p style='line-height: 32px;'>{}</p>".format(subHeader),
                               subText=subText, isFuzzy=isFuzzy, analytics=analytics, namesSet=shortNames, d3js=d3js, )




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