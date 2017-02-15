__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / whos_news.py'
__datum__ = '15/02/17'

from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk.stem import SnowballStemmer, snowball
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import tree, trigrams, word_tokenize, pos_tag, ne_chunk, ne_chunk_sents
import nltk
from nltk.collocations import *

app = Flask(__name__, static_folder='static')

@app.route("/")
def home():
    tagContent = []
    salute = "hej there"
    org_enc = "-"
    soup = "*"
    articleLink = "http://politiken.dk/indland/politik/art5833361/Borgmestre-er-åbne-for-at-rykke-politikere-til-provinsen"
    # getLinkData = requests.get(articleLink)
    # soup = BeautifulSoup(getLinkData.content, "lxml")
    # org_enc = soup.original_encoding
    # print("original encoding", org_enc)
    # tagThing = ".article__title"
    # tagContent = soup.select(tagThing)
    # alltext =
    val = "dfdf"
    return render_template("base.html", salute=salute, articleLink="enconding : {} / Link: {} / Tags: {}".format(org_enc, articleLink, tagContent), soup=soup)


if __name__ == "__main__":

    app.run()