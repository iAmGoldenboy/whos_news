__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / lib_common.py'
__datum__ = '15/02/17'

import string
from lib_nlp import scrubString
from time import sleep
import dbconfig
import requests
import json



# sorting stuff out :)
def getKey1st(item): return item[0]

def getKey2nd(item):  return item[1]

def getKey3rd(item):  return item[2]

def getKey4th(item): return item[3]

def getKey5th(item):  return item[4]



def extractTagContent(tagContent, htmltag):

    tagOutput = []

    for item in tagContent:
        try:
            if htmltag == 'billedtekstTag':
                imgtext = extractImageText(item, htmltag)

                if imgtext not in tagOutput:
                    tagOutput.append(imgtext.replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", "").replace("  ", ""))

            elif htmltag == "overskriftTag":
                headerText = extractHeaderText(item.replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", "").replace("  ", ""))

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
            print("Error with tag ", item, "due to ", e)

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
        print("Couldn't get img text -> {} <- due to : {}".format(imgtext, e))

    if "Foto:" in imagetext:

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
