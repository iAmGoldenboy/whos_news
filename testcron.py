__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / testcron.py'
__datum__ = '15/02/17'

import schedule
import time
from dbhelper import DBHelper
from lib_common import getKey2nd, extractHeaderText, extractImageText, get_social_metrics, extrapolateSocialMetrics, extractTagContent
from lib_nlp import removeStopwordsFromString, extractNE, signal, keepThoseAboveQuartile
import requests
import xmltodict
import random
from bs4 import BeautifulSoup

DB = DBHelper()
rssFeeds = DB.get_all_feeds()
html_tags = DB.getHTMLtags()
# print("you are piethon")


def collectArticleLinks(rssFeedName, sektion, avis, olderArticles, newerArticles):
    feedsDict = fetchFeedsData(rssFeedName)
    older, newer = extractArticles(feedsDict)
    [olderArticles.append([articleLink, sektion, avis]) for articleLink in older if older]
    [newerArticles.append([articleLink, sektion, avis]) for articleLink in newer if newer]

def fetchFeedsData(feedLink):

    try:
        feedR = requests.get(feedLink)
        return xmltodict.parse(feedR.content, process_namespaces=True)
    except Exception as e:
        print("no feedR due to :", e)
        return None


def extractArticles(feedsDict):

    try:
        articles = [rssItem["link"].replace("?referrer=RSS", "") for rssItem in feedsDict["rss"]["channel"]["item"]]
        return articles[:int(len(articles)/2)], articles[int(len(articles)/2):]
    except Exception as e:
        print("No article links due to :", e)
        return None



def getArticleLinksFromFeeds():
    """
    :return:
    """
    # def getArticleLinksFromFeeds():
    # get list of feeds
    # get articleLinks from feeds
    # if article not articles database add articleLink+sektion+name+date to the articleQue database

    olderArticles = []
    newerArticles = []

    sektion = ""
    avis = ""

    try:
        for rssFeed in sorted(rssFeeds, key=getKey2nd):
            # print(rssFeed)
            # hmmm - how do
            if rssFeed[1] != sektion and rssFeed[0] == avis:
                # print("This sektion: {} NOT SAME previous sektion: {} -     {}, so I'll sleep for 3 seconds - {}".format(rssFeed[1], sektion, rssFeed[0], time.time()))
                collectArticleLinks(rssFeed[3], rssFeed[1], rssFeed[0], olderArticles, newerArticles )
                sektion, avis = rssFeed[1], rssFeed[0]
                time.sleep(3)

            elif rssFeed[1] == sektion and rssFeed[0] != avis:
                # print("Else sektion {} ** same {} and sleep for 0.3 ----    {} .-.-.-. {}".format(rssFeed[1], sektion, rssFeed[0], time.time()))
                collectArticleLinks(rssFeed[3], rssFeed[1], rssFeed[0], olderArticles, newerArticles )
                sektion, avis = rssFeed[1], rssFeed[0]
                time.sleep(0.3)

            elif rssFeed[0] != avis:
                # print("This sektion: {} NOT SAME previous sektion: {} -     {}, so I'll sleep for 3 seconds - {}".format(rssFeed[1], sektion, rssFeed[0], time.time()))
                collectArticleLinks(rssFeed[3], rssFeed[1], rssFeed[0], olderArticles, newerArticles )
                sektion, avis = rssFeed[1], rssFeed[0]
                time.sleep(3)

            else:
                # print("Else sektion {} ** same {} and sleep for 0.3 ----    {} .-.-.-. {}".format(rssFeed[1], sektion, rssFeed[0], time.time()))
                collectArticleLinks(rssFeed[3], rssFeed[1], rssFeed[0], olderArticles, newerArticles )
                sektion, avis = rssFeed[1], rssFeed[0]
                time.sleep(3)
    except Exception as e:
        print("Sorry - Couldn't get articles due to ", e)

    return olderArticles + newerArticles

# print("mixed")
# artQue = getArticleLinksFromFeeds()
# for myart in artQue:
#     print(myart)

def insertArticleLinksFromFeedsIntoArticleQue():
    """ Collects all the articles from all the feeds and adds them to the article que if they are not there.
    :return: VOID
    """


    articleDataList = getArticleLinksFromFeeds()
    print("Current number of article-links in all feeds: ", len(articleDataList))

    for articleData in articleDataList:
        try:
            if articleData[2] == "Berlingske Tidende" or articleData[2] == "BT":

                end = articleLink[len(articleLink)-2:]
                berlList = ["-0", "-1", "-2", "-3", "-4", "-5", "-6"]

                if end in berlList:
                    articleLink = articleData[0][:len(articleData)-2]

        except Exception as e:
            articleLink = articleData[0]

        # print("Inserting ", articleData)
        DB.insertArticleLinksToArticleQue(articleData)


def extractArticleData():
    articleLinks = DB.getArticleQue()
    print("Number of articles in Que: {} - of which we have seen: {} - and need to go through: {}".format( DB.countArticlesQue(), DB.countArticlesQueSeen(), DB.countArticlesQueNotSeen()) )
    if len(articleLinks) > 0:
        for articleLink in articleLinks:
            # print("     ---> ", articleLink)
            articleLink, avis, sektion = articleLink[0], articleLink[2], articleLink[1]

            try:
                # save the article link in the database and get the article_id for future use.
                article_id = DB.insertValuesReturnID('articleLinks', ['articleLink', 'sektion', 'avis'], [str(articleLink), str(sektion), str(avis)], 'articleLink', articleLink, 'article_id', returnID=True, printQuery=False)

                # print("the article link is {} and the id is {}".format(articleLink, article_id))
                getLinkData = requests.get(articleLink)
                if getLinkData.status_code == 200:
                    soup = BeautifulSoup(getLinkData.content, "lxml", from_encoding="utf-8")

                    # print("soup de soup ---> ", soup)

                    try:
                        # tagItem = None
                        NEbag, NEhead, NEtail = [], [], []

                        for htmltag in html_tags:
                            # print("HTMLTAGS", htmltag, htmltag[0])
                            tagItem = DB.getHTMLtagItem(avis, htmltag[0]) # Get the htmltags for this newspaper


                            if tagItem:
                                tagOutput = []

                                try:
                                    for singleTag in tagItem[0]: # xtract text from each tagType.
                                        tagContent = soup.select(singleTag)

                                        tagOutput = extractTagContent(tagContent, htmltag[0])

                                    # OK, now we have a list of sentences to go through. Let's do it!

                                    for lines in tagOutput:
                                        try:
                                            # Remove stopwords and tokenize
                                            tokenizeCleaned = removeStopwordsFromString(lines)

                                            # Extract named entities for the sentences.
                                            sentenceNEs = extractNE(tokenizeCleaned)

                                            # If we have sentences to go through...
                                            if sentenceNEs:
                                                # ... add all to one big bag
                                                [NEbag.append(neToken) for neToken in sentenceNEs]

                                                try:

                                                    # Lets also split between bodycopy and headercopy (inkl. captions)
                                                    # When dealing with bodycopy, inline headlines and quotes add them to the NEtail list.
                                                    if htmltag == "brodtextTag" or htmltag == "mellemrubrikTag" or htmltag == "quoteTag":
                                                        [NEtail.append(neToken) for neToken in sentenceNEs]

                                                    # ... else they must be Header Copy and will be added to NEhead list
                                                    else:
                                                        [NEhead.append(neToken) for neToken in sentenceNEs]
                                                except Exception as e:
                                                    print("Couldn't add -> {} <- to NE tail / head due to ".format(sentenceNEs, e))

                                        except Exception as e:
                                            print("Couldn't tokenize NE data due to : ", e)

                                except Exception as e:
                                    print("Error with tag -> {} <- : tag item -> {} <- | content due to : {} ".format(htmltag[0], tagItem, e) )

                            else:
                                # no tag item for this html tag, so lets move on without crying.
                                pass

                        # OK, good! Now we have three list with NE's. Lets start adding them to the database.

                        # Lets first see what's in them
                        # print("Shebang", NEbag)

                        keepAll = signal(NEbag)
                        keepHead = keepThoseAboveQuartile(NEhead)
                        keepTail = keepThoseAboveQuartile(NEtail)

                        # Go through all items and collect: count, headcount, tailCount, shape and article id.
                        # Create a foaf list.
                        # Insert each named entitiy in the database and get the ne_id, add all of it to a dict.

                        collectNEdict, foafDict = {}, {}

                        fakeCounter = 0

                        for neID, neData in keepAll.items():

                            headCount, tailCount = 0, 0

                            try:
                                headCount = keepHead[neID]
                            except Exception as e:
                                pass
                                # print("Head not found - scary", e, keepHead)

                            try:
                                tailCount = keepTail[neID]
                            except Exception as e:
                                pass
                                # print("Tail not found - not scary, but it sucks", e, keepTail)

                            # Insert named entity into database
                            neValues = [str(neID)]
                            neoutput = DB.insertValuesReturnID('namedEntities', ['ne'], neValues, 'ne', neID, 'ne_id', mode="single", returnID=True, printQuery=False)

                            ne2artFields = ['ne2art_ne_id', 'ne2art_art_id', 'neOccuranceCount', 'neOccuranceHead', 'neOccuranceTail', 'neOccurranceShape']
                            nerartValues = [neoutput, article_id, neData.get("sum"), headCount, tailCount, str(neData.get("shape"))]

                            ne2art_output = DB.insertValuesReturnID('namedEntity2Articles', ne2artFields, nerartValues, ['ne2art_ne_id', 'ne2art_art_id'], [neoutput, article_id], 'ne_id',  mode="ne2art", returnID=True, printQuery=False)

                            # update each ne and get row id, add ne and row_id to dict
                            collectNEdict[neID] = {"ne_id" : neoutput,
                                                   "foaf_art_id": article_id,
                                                   "foaflist": [neT for neT in keepAll.keys() if neID != neT] }

                            # update the fake counter
                            fakeCounter += 1

                        foafFields, foafLookfor = ['foaf_ne_id', 'foaf_knows_id', 'foaf_art_id'], ['foaf_ne_id', 'foaf_art_id']


                        for neID, neData in collectNEdict.items():
                            for foaf in neData.get("foaflist"):
                                foafValues = [neData.get("ne_id"), collectNEdict[foaf].get("ne_id"), neData.get("foaf_art_id")]
                                foaf_id = DB.insertValuesReturnID('foaf', foafFields, foafValues, foafLookfor, [neData.get("ne_id"), neData.get("foaf_art_id")], returnID=True, mode="foaf", printQuery=False)
                                # print("NE_ID: {} NE-DATA: {}, FOAF: {}, FOAF_ID: {}".format( neID, neData, foaf, foaf_id) )

                        # Collect Social Media data
                        smDict = get_social_metrics(articleLink, pause=1)

                        # Add social media data into a list
                        SoMeCounter = extrapolateSocialMetrics(smDict)

                        # if there is data, add it to the database
                        SoMeCount = 0
                        if len(SoMeCounter) > 0:
                            for SoMes in SoMeCounter:
                                # update database with article_id, enum value, SoMe count.
                                DB.insertSocialMedia(article_id, SoMes[0], SoMes[1])
                                SoMeCount += SoMes[1]

                        print("Newspaper: {} / Sektion: {} / URL: {}".format(avis, sektion, articleLink) )
                        print("Article ID: {} / No. of NEs: {} / No. of SoMe Instances: {} / SoMe count: {}".format(article_id, len(keepThoseAboveQuartile(NEbag)), len(SoMeCounter), SoMeCount) )


                        # We got what we needed. Mark the article as seen
                        DB.seenArticle(articleLink)
                        print()

                    except Exception as e:
                        print("Couldn't get html tags for {} / {} due to : {}".format(avis, sektion, e))

            except Exception as e:
                print("Couldn't get articledata for {} / {} / {}  -  due to : {}".format(avis, sektion, articleLink, e))




            time.sleep(3)


    print("NOW THE Number of articles: {} /     Seen {} / Not Seen {}".format( DB.countArticlesQue(), DB.countArticlesQueSeen(), DB.countArticlesQueNotSeen()) )
    # get the oldest articles from the articleQue
    # if articleQue is not empty
    # extract information from articleLink and add to database
    # add articleLink to article database
    # if extraction is successful, remove articlelink from articleQue database


def deleteOldArticles():
    timeNum = 23
    timeType = "hour"
    print("Deleting articles from que: {} / {}".format(timeNum, timeType))
    DB.deleteFromArticleQue(timeNum, timeType)

def mySchedule():
    schedule.every(1).minutes.do(insertArticleLinksFromFeedsIntoArticleQue)
    schedule.every(2).minutes.do(extractArticleData)
    schedule.every(23).hours.do(deleteOldArticles)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    mySchedule()