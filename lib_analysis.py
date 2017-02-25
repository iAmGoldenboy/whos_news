__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / lib_common.py'
__datum__ = '15/02/17'

import stats
from collections import Counter
import datetime, timeit
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
    quartiles = 0.0, 0.0, 0.0
    inQuarts = countValuesInQuartiles(numbersList)
    q1, q2, q3 = inQuarts
    q1percent = calculatePercentage(q1, len(numbersList))
    q2percent = calculatePercentage(q2, len(numbersList))
    q3percent = calculatePercentage(q3, len(numbersList))

    try:
        quartiles = stats.quartiles(numbersList)
    except Exception as e:
        pass

    try:
        median = stats.median(numbersList)
    except Exception as e:
        pass

    try:
        mean = stats.mean(numbersList)
    except Exception as e:
        pass

    return {"mean": mean, "median": median, "Q1": round(q1,2), "Q2": round(q2,2), "Q3": round(q3,2), "Q1Perc": round(q1percent,2), "Q2Perc": round(q2percent,2), "Q3Perc": round(q3percent,2), "quartileCount": inQuarts, "quartiles" : quartiles}


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

def peakDays(namedEntityMergedDict):
    # http://stackoverflow.com/questions/16766643/convert-date-string-to-day-of-week

    timeType = "%Y-%m-%d %H:%M:%S" # 2017-02-18 09:35:42
    try:
        weekdays = dict(Counter([datetime.datetime.strptime(str(datas.get("date")), timeType).strftime('%A') for _, datas in namedEntityMergedDict.items()]))
    except Exception as e:
        weekdays = {'Friday': 0, 'Monday': 0, 'Saturday': 0, 'Sunday': 0, 'Tuesday': 0, 'Thursday': 0, 'Wednesday': 0}

    return weekdays




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


def datesMinMaxCount(namedEntityMergedDict):

    dates = [datetime.datetime.date(datas.get("date")) for _, datas in namedEntityMergedDict.items()]
    try:
        dateList = [str(min(dates)), str(max(dates)), len(dates)]
    except Exception as e:
        dateList = ["0-0-0", "0-0-0", 0]

    return dateList

def setupAnalysisDict(namedEntityMergedDict):

    analysisDict = {}

    # check if any NEs have been saved to database, if not, create new.
    # create one bag for each NE and one for all NEs
    # earliest publication date, latest publication date

    topExcludeList = ["link", "Twitter", "Facebook_like_count", "StumbleUpon", "ne_id", "Facebook_total_count"]
    collectionExcludeList = ["link", "Twitter", "Facebook_like_count", "Facebook_total_count", "StumbleUpon"]

    for id, data in namedEntityMergedDict.items():
        # and one for all
        if data.get("ne") not in analysisDict:

            analysisDict[data.get("ne")] = {}

            for item in data:
                if item not in topExcludeList:
                    analysisDict[data.get("ne")].update({ item : [data.get(item)]} )

            analysisDict[data.get("ne")].update({"dailyStats" : { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} },
                                                "threeDayStats": { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} },
                                                "weekStats": { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} },
                                                "monthStats": { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} },
                                                "allStats": { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} }})

        else:
            for item in data:
                if item not in topExcludeList:
                    analysisDict[data.get("ne")][item].append(data.get(item))


        if "collection" not in analysisDict:

            analysisDict["collection"] = {}

            for item in data:
                if item not in collectionExcludeList:
                    analysisDict["collection"].update({ item : [data.get(item)]} )

            analysisDict["collection"].update({"dailyStats" : { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} },
                                                "threeDayStats": { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} },
                                                "weekStats": { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} },
                                                "monthStats": { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} },
                                                "allStats": { "ToC" : {}, "HeC" : {}, "TaC": {}, "shape": (), "media": {}, "section": {}, "dates": {}, "ne": {},
                                                                 "Pinterest" : {}, "LinkedIn" : {}, "GooglePlusOne" : {}, "Facebook_comment_count" : {}, "Facebook_share_count" : {} }})
        else:
            for item in data:
                if item not in topExcludeList:
                    analysisDict["collection"][item].append(data.get(item))

    return analysisDict


def getAnalytics(namedEntityMergedDict):


    oneDay = getDateXdaysAgo(1)
    threeDays = getDateXdaysAgo(3)
    sevenDays = getDateXdaysAgo(7)
    month = getDateXdaysAgo(30)
    halfYear = getDateXdaysAgo(182)
    year = getDateXdaysAgo(365)


    nemd = namedEntityMergedDict
    dateList = datesMinMaxCount(namedEntityMergedDict)
    print(dateList)

    analysisDict = setupAnalysisDict(namedEntityMergedDict)


    # print(analysisDict)
    exStats = ["dailyStats", "threeDayStats", "weekStats", "monthStats", "allStats" ] #, "halfYearStats", "yearStats"]
    valueItems = ["TaC", "ToC", "HeC", "LinkedIn", "Facebook_share_count", "Facebook_comment_count", "GooglePlusOne", "Pinterest", ]
    tokenItems = ["media", "section", "shape"]

    for id, data in analysisDict.items():
        # print(id, data)
        dailyStats, threeDayStats, weekStats, monthStats, allStats = [], [], [], [], []

        # get hold of the index of each item by using the date's index
        statsDict = {   "dailyStats" : [(data.get("date").index(date)) for date in data.get("date") if datetime.datetime.date(date) > oneDay],
                        "threeDayStats" : [(data.get("date").index(date)) for date in data.get("date") if datetime.datetime.date(date)  >= threeDays and datetime.datetime.date(date) <= oneDay],
                        "weekStats" : [(data.get("date").index(date)) for date in data.get("date") if datetime.datetime.date(date)  >= sevenDays and datetime.datetime.date(date) <= oneDay],
                        "monthStats" : [(data.get("date").index(date)) for date in data.get("date") if datetime.datetime.date(date)  >= month and datetime.datetime.date(date) <= oneDay],
                        "allStats" : [(data.get("date").index(date)) for date in data.get("date") if datetime.datetime.date(date)] }

        for item in data:
            # print(item)
            if item in valueItems:
                for statType in exStats:
                    # print(statType, item, getQuartilesData([data.get(item)[itemindex] for itemindex in statsDict.get(statType)]) )
                    analysisDict[id][statType][item] = getQuartilesData([data.get(item)[itemindex] for itemindex in statsDict.get(statType)])
                # print("i", item, "t", lastThree, "it", [data.get(item)[itemindex] for itemindex in lastThree])
                # print(item, getQuartilesData([data.get(item)[itemindex] for itemindex in lastThree]))

            if item in tokenItems:
                for statType in exStats:
                # print("i", item, "t", lastThree, "it", [data.get(item)[itemindex] for itemindex in lastMonth])
                    tokenCount = dict(Counter([data.get(item)[itemindex] for itemindex in statsDict.get("monthStats")]))
                    count = sum(tokenCount.values())
                    # for id, data in counterDict.items():
                    #     print(id, data, round(calculatePercentage(data, count),2) )
                    analysisDict[id][statType][item] = {id: {"count": data, "perc": round(calculatePercentage(data, count),2)} for id, data in sorted(tokenCount.items(), reverse=True, key=getKey2nd)}

                    # print("kkk", item, "--", {id: {"count": data, "perc": round(calculatePercentage(data, count),2)} for id, data in sorted(tokenCount.items(), reverse=True, key=getKey2nd)} )




        print(id, analysisDict[id])
        # print(dailyStats)
        # print(threeDayStats)
        # print(weekStats)
        # print(monthStats)
        # print(allStats)


    today = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) > oneDay}
    lastThree = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) >= threeDays and datetime.datetime.date(data.get("date")) <= oneDay}
    lastWeek = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) >= sevenDays and datetime.datetime.date(data.get("date")) <= oneDay}
    lastMonth = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) >= month and datetime.datetime.date(data.get("date")) <= oneDay}
    # allTime = {id: data for id, data in namedEntityMergedDict.items() if datetime.datetime.date(data.get("date")) <= month}

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

    print("MONTH", quartileDataDict_lastMonth.get("Facebook_share_count"), quartileDataDict_lastMonth.get("Facebook_share_count").get("mean")) # ToC, HeC, TaC, Facebook_comment_count, Facebook_share_count
    print("Wek", quartileDataDict_lastWeek.get("Facebook_share_count"), quartileDataDict_lastWeek.get("Facebook_share_count").get("mean")) # ToC, HeC, TaC, Facebook_comment_count, GooglePlusOne, LinkedIn, StumbleUpon, Pinterest, Twitter
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

    peakDays(namedEntityMergedDict)
    # print(computeTokenDataDict(peakDays(namedEntityMergedDict)))

    # return tokenDataDict_ALL.get("section")

    return analysisDict
