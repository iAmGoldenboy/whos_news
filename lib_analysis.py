__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / lib_common.py'
__datum__ = '15/02/17'

import stats
from collections import Counter
import datetime
from lib_common import getKey2nd



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



def compareNumbers(now, then):

    percentChange = 0
    compNumDict = {"change" : "even", "percent" : 0}

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
    lastThree = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) >= threeDays and datetime.datetime.date(data.get("date")) <= oneDay}
    lastWeek = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) >= sevenDays and datetime.datetime.date(data.get("date")) <= oneDay}
    lastMonth = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) >= month and datetime.datetime.date(data.get("date")) <= oneDay}
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


    mainKeys = ['section', 'media', 'shape']
    sectionKeys = [mKey[0] for mKey in tokenDataDict_ALL.get("section")]
    mediaKeys = [mKey[0] for mKey in tokenDataDict_ALL.get("media")]
    shapeKeys = [mKey[0] for mKey in tokenDataDict_ALL.get("shape")]
    print(mediaKeys, shapeKeys, sectionKeys)
    print(tokenDataDict_lastThree)
    print(tokenDataDict_lastWeek.get("section"))
    print(tokenDataDict_lastWeek.get("media"))
    print(tokenDataDict_lastWeek.get("shape"))
    # split data into two halves to see if there is growth or decline

    return tokenDataDict_lastWeek.get("section")
