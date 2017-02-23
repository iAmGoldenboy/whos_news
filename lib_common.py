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
