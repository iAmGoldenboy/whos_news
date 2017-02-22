__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / lib_common.py'
__datum__ = '15/02/17'

import string
from lib_nlp import scrubString
from time import sleep
import dbconfig
import requests
import json
import stats
import statistics
from collections import Counter
from dbhelper import DBHelper
import datetime


DB = DBHelper()


# sorting stuff out :)
def getKey1st(item): return item[0]

def getKey2nd(item):  return item[1]

def getKey3rd(item):  return item[2]

def getKey4th(item): return item[3]

def getKey5th(item):  return item[4]



def extractTagContent(tagContent, htmltag):

    tagOutput = []

    for item in tagContent:
        if item is not None:
            try:
                if htmltag == 'billedtekstTag':
                    imgtext = extractImageText(item, htmltag)

                    if imgtext not in tagOutput:
                        tagOutput.append(imgtext.replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", "").replace("  ", ""))

                elif htmltag == "overskriftTag":
                    headerText = extractHeaderText(item)

                    if headerText not in tagOutput:
                        tagOutput.append(headerText)

                elif htmltag == "brodtextTag":
                    broedText = item.get_text().strip().replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", " ").replace("  ", "")

                    if broedText not in tagOutput:
                        if "Læs også" not in broedText  or "/ritzau/" not in broedText or "Artiklen fortsætter under billedet" not in broedText or "Se også:" not in broedText:
                            tagOutput.append(broedText)

                else:
                    otherText = item.get_text().strip().replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", " ").replace("  ", "")

                    if otherText not in tagOutput:
                        tagOutput.append(otherText)

            except Exception as e:
                print("Error with extractTagContent ", item, "with tag ->", htmltag, "<- due to ", e)

    return tagOutput

def extractHeaderText(item):
    """ Deals with missing periods after headline sentences, where there often is none,
    however sometimes there is a question mark or other character.
    :param item:
    :return: header string with a period after it (if it was missing).
    """

    headerText = ""

    try:
        if item.get_text().strip()[len(item.get_text().strip())-1] not in string.punctuation:
            headerText = "{} . ".format(scrubString(item.get_text().strip()))
        else:
            headerText = "{}  ".format(scrubString(item.get_text().strip()) )
    except Exception as e:
        print("extractHeaderText error due to :", e)

    # print("header", headerText)
    return headerText


def extractImageText(imgtext, htmltag):
    """
    :param imgtext: the image text collected from the html tag
    :param htmltag: the html tag used to find image captions
    :return: a string without the 'Foto: Some Name'
    """
    imagetext = ""

    try:
        imagetext = imgtext.get_text().strip()
    except Exception as e:
        print("IN extractImageText - Couldn't get img text -> {} <- due to : {}".format(imgtext, e))

    if len(imagetext) > 0:

        if "ARKIVFOTO," in imagetext:

            try:
                imagetext = "{} ".format(imagetext.split("ARKIVFOTO:")[0])
            except Exception as e:
                print("No 'ARKIVFOTO:' data due to :", e)

        elif "Arkivfoto:" in imagetext:

            try:
                imagetext = "{} ".format(imagetext.split("Arkivfoto:")[0])
            except Exception as e:
                print("No 'Arkivfoto:' data due to :", e)

        elif "Foto:" in imagetext:

            try:
                imagetext = imagetext.split("Foto:")[0]

                if htmltag == 'billedtekstTag' and "REUTERS" in imagetext:
                    imagetext = "{} ".format(imagetext.split("REUTERS")[0])

            except Exception as e:
                print("No 'Foto:' data due to :", e)

        elif "Fotos:" in imagetext:

            try:
                imagetext = "{} ".format(imagetext.split("Fotos:")[0])
            except Exception as e:
                print("No 'Fotos:' data due to :", e)


        elif "PHOTO:" in imagetext:

            try:
                imagetext = "{} ".format(imagetext.split("PHOTO:")[0])
            except Exception as e:
                print("No 'PHOTO:' data due to :", e)

        elif "PHOTOS:" in imagetext:

            try:
                imagetext = "{} ".format(imagetext.split("PHOTOS:")[0])
            except Exception as e:
                print("No 'PHOTOS:' data due to :", e)

    return imagetext




def get_social_metrics(url, pause=3):
    """ Collect the Social Media Metrics from sharedcount.com.
    :param url: the URL the we want to see how many Social Media encounters has.
    :param pause: time before continuing.
    :return: a dict with the various key/values.
    """
    api_key = dbconfig.apiKEY
    formalcall = "{}{}{}{}".format( 'https://free.sharedcount.com/?url=', url , '&apikey=' , api_key )

    dataDict = {}
    try:
        sharedcount_response = requests.get(formalcall)

        sleep(pause)

        if sharedcount_response.status_code == 200:
            data = sharedcount_response.text
            dataDict = dict(json.loads(data))
            return dataDict

    except Exception as e:
        print("Moving onwards due to", e)
        return dataDict

def extrapolateSocialMetrics(sharedCountDict):

    forDataBase = []
    for SoMeID, SoMeData in sharedCountDict.items():
        if isinstance(SoMeData, dict):
            # then we are in facebook
            for fbID, fbData in SoMeData.items():
                if fbData > 0 and fbID != "total_count":
                    forDataBase.append(["Facebook_{}".format(fbID), fbData])
        else:
            if SoMeData > 0:
                forDataBase.append([SoMeID, SoMeData])

    return forDataBase


def getSocialCount(socialDict, spread=True):

    accumCount = 0
    if spread and socialDict is not None:
        # print(socialDict)

        try:
            for key, data in socialDict.items():
                if isinstance(data, int):
                    accumCount += data

                elif key == "Facebook":
                    accumCount += data.get("total_count")
        except Exception as e:
            print("Social Counter died:", e)

    # print(accumCount)
    return accumCount


def recentArticlesFromCellar():

    mergeDict = {}
    lastHour = DB.countRecentArticles(0,1)
    threeHours = DB.countRecentArticles(0,3)
    twentyFourHours = DB.countRecentArticles(0,24)
    week = DB.countRecentArticles(0,1,"week", "week")

    for itemW in week:
        try:
            mergeDict[str("{}-{}".format(itemW[2].replace(" ", "-"),itemW[1]))].update({"week": itemW[0]})
        except KeyError:
            mergeDict[str("{}-{}".format(itemW[2].replace(" ", "-"),itemW[1]))] = {"avis": itemW[2], "sektion": itemW[1], "week": itemW[0], "three": 0, "twenty" : 0, "last":0}


    for itemTw in twentyFourHours:
        try:
            mergeDict[str("{}-{}".format(itemTw[2].replace(" ", "-"),itemTw[1]))].update({"twenty": itemTw[0]})
        except KeyError:
            mergeDict[str("{}-{}".format(itemTw[2].replace(" ", "-"),itemTw[1]))] = {"avis": itemTw[2], "sektion": itemTw[1], "twenty": itemTw[0], "three": 0, "week" : 0, "last":0}

    for itemTh in threeHours:
        try:
            mergeDict[str("{}-{}".format(itemTh[2].replace(" ", "-"),itemTh[1]))].update({"three": itemTh[0]})
        except KeyError:
            mergeDict[str("{}-{}".format(itemTh[2].replace(" ", "-"),itemTh[1]))] = {"avis": itemTh[2], "sektion": itemTh[1], "twenty" : 0, "three": itemTh[0], "week" : 0,  "last" : 0}

    for itemLa in lastHour:
        try:
            mergeDict[str("{}-{}".format(itemLa[2].replace(" ", "-"),itemLa[1]))].update({"last": itemLa[0]})
        except KeyError:
            mergeDict[str("{}-{}".format(itemLa[2].replace(" ", "-"),itemLa[1]))] = {"avis": itemLa[2], "sektion": itemLa[1], "twenty" : 0, "three" : 0, "week" : 0, "last": itemLa[0]}

    return mergeDict

def countValuesInQuartiles(numbersList):
        q1Count, q2Count, q3Count = [], [], []

        try:
            q1, q2, q3 = stats.quartiles(numbersList)

            for number in numbersList:
                if float(number) >= q3:
                    q3Count.append(number)
                elif float(number) <= q1:
                    q1Count.append(number)
                else: # it must be in between, right?
                    q2Count.append(number)
        except Exception as e:
            pass # silently in to the night!

        return len(q1Count), len(q2Count), len(q3Count)


def calculatePercentage(quartileCount, allCount):

    try:
        return (quartileCount/allCount)*100
    except ZeroDivisionError:
        return 0

def getQuartilesData(numbersList):
    mean = 0
    median = 0
    inQuarts = countValuesInQuartiles(numbersList)
    q1, q2, q3 = inQuarts
    q1percent = calculatePercentage(inQuarts[0], len(numbersList))
    q2percent = calculatePercentage(inQuarts[1], len(numbersList))
    q3percent = calculatePercentage(inQuarts[2], len(numbersList))
    try:
        median = stats.median(numbersList)
    except Exception as e:
        pass

    try:
        mean = stats.mean(numbersList)
    except Exception as e:
        pass

    return {"mean": mean, "median": median, "Q1": round(q1,2), "Q2": round(q2,2), "Q3": round(q3,2), "Q1Perc": round(q1percent,2), "Q2Perc": round(q2percent,2), "Q3Perc": round(q3percent,2), "quartiles": inQuarts}


def extractNumberValues(namedEntityMergedDict, itemToLookFor):
    return [datas.get(itemToLookFor) for _, datas in namedEntityMergedDict.items()]

def extractTokenValues(namedEntityMergedDict, itemToLookFor):

    counterDict = dict(Counter([datas.get(itemToLookFor) for _, datas in namedEntityMergedDict.items()]))
    count = sum(counterDict.values())
    # for id, data in counterDict.items():
    #     print(id, data, round(calculatePercentage(data, count),2) )

    return [[id, {"count": data, "perc": round(calculatePercentage(data, count),2)}] for id, data in sorted(counterDict.items(), reverse=True, key=getKey2nd)]


def computeQuartileDataDict(namedEntityMergedDict):
    counterList = ["Facebook_share_count", "Facebook_comment_count", "GooglePlusOne", "LinkedIn", "Pinterest", "ToC", "HeC", "TaC" ]
    return {output: getQuartilesData(extractNumberValues(namedEntityMergedDict, output)) for output in counterList}

def computeTokenDataDict(namedEntityMergedDict):
    tokenList = ["shape", "media", "section"]
    return {output: extractTokenValues(namedEntityMergedDict, output) for output in tokenList}

def getDateXdaysAgo(days=1):
    # http://stackoverflow.com/questions/441147/how-can-i-subtract-a-day-from-a-python-date?rq=1
    return datetime.date.today() - datetime.timedelta(days=days)

def getAnalytics(namedEntityMergedDict):

    dates = [datetime.datetime.date(datas.get("date")) for _, datas in namedEntityMergedDict.items()]
    dates = "Earliest: {} <br>Latest: {}".format( min(dates), max(dates), len(dates) )
    print(dates)

    oneDay = getDateXdaysAgo(1)
    threeDays = getDateXdaysAgo(3)
    sevenDays = getDateXdaysAgo(7)
    month = getDateXdaysAgo(30)
    halfYear = getDateXdaysAgo(182)
    year = getDateXdaysAgo(365)
    today = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) > oneDay}
    lastThree = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) > threeDays and datetime.datetime.date(data.get("date")) <= oneDay}
    lastWeek = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) > sevenDays and datetime.datetime.date(data.get("date")) <= oneDay}
    lastMonth = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) > month and datetime.datetime.date(data.get("date")) <= oneDay}
    # allTime = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) <= month}


    # print("today", len([data.get("date") for _, data in today.items()]), [datetime.datetime.date(data.get("date")) for _, data in today.items()])
    # print("lastThree", len([data.get("date") for _, data in lastThree.items()]), [datetime.datetime.date(data.get("date")) for _, data in lastThree.items()])
    # print("lastWeek", len([data.get("date") for _, data in lastWeek.items()]), [datetime.datetime.date(data.get("date")) for _, data in lastWeek.items()])
    # print("lastMonth", len([data.get("date") for _, data in lastMonth.items()]), [datetime.datetime.date(data.get("date")) for _, data in lastMonth.items()])
    # print("allTime", len([data.get("date") for _, data in allTime.items()]), [datetime.datetime.date(data.get("date")) for _, data in allTime.items()])

    # print("today", [data.get("date") for _, data in today.items()])
    # for day in dates:
    #     print(type(day))
    #     print(datetime.datetime.strptime(day, dateformat) )

    # get quartile values and percentages for number data
    quartileDataDict_ALL = computeQuartileDataDict(namedEntityMergedDict)
    quartileDataDict_today = computeQuartileDataDict(today)
    quartileDataDict_lastThree = computeQuartileDataDict(lastThree)
    quartileDataDict_lastWeek = computeQuartileDataDict(lastWeek)
    quartileDataDict_lastMonth = computeQuartileDataDict(lastMonth)

    # get token dict with counter values for categorical data
    tokenDataDict_ALL = computeTokenDataDict(namedEntityMergedDict)
    tokenDataDict_today = computeTokenDataDict(today)
    tokenDataDict_lastThree = computeTokenDataDict(lastThree)
    tokenDataDict_lastWeek = computeTokenDataDict(lastWeek)
    tokenDataDict_lastMonth = computeTokenDataDict(lastMonth)

    # when comparing remember to split/average by lastThree/week/month etc??

    print("MON", quartileDataDict_lastMonth.get("Facebook_share_count"), quartileDataDict_lastMonth.get("Facebook_share_count").get("mean")) # ToC, HeC, TaC, Facebook_comment_count
    print("Wek", quartileDataDict_lastWeek.get("Facebook_share_count"), quartileDataDict_lastWeek.get("Facebook_share_count").get("mean")) # ToC, HeC, TaC, Facebook_comment_count
    print("Thr", quartileDataDict_lastThree.get("Facebook_share_count"), quartileDataDict_lastThree.get("Facebook_share_count").get("mean"))
    print("tod", quartileDataDict_today.get("Facebook_share_count"), quartileDataDict_today.get("Facebook_share_count").get("mean"))
    print("com 3-> w", compareNumbers(quartileDataDict_lastThree.get("Facebook_share_count").get("mean"), quartileDataDict_lastWeek.get("Facebook_share_count").get("mean")))
    print("com 3 -> m", compareNumbers(quartileDataDict_lastThree.get("Facebook_share_count").get("mean"), quartileDataDict_lastMonth.get("Facebook_share_count").get("mean")))

    # split data into two halves to see if there is growth or decline





def compareNumbers(now, then):

    percentChange = 0
    comNum = {"change" : "even", "percent" : 0}

    if now > then:
        change = "increase"
        try:
            percentChange = round(((now-then)/now)*100,2)
        except ZeroDivisionError as e:
            percentChange = 0
        except Exception as e:
            pass
        compNumDict =  {"change" : change, "percent" : percentChange}

    elif now < then:
        change = "decrease"
        try:
            percentChange = round(((then-now)/then)*100,2)
        except ZeroDivisionError as e:
            percentChange = 0
        except Exception as e:
            pass

        compNumDict =  {"change" : change, "percent" : percentChange}

    return compNumDict


