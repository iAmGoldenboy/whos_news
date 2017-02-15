__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_news / testcron.py'
__datum__ = '15/02/17'

import schedule
import time

print("you are piethon")

def runHej():
    print("hej pejthorn")
    return "hopsa hopsasa"


def mySchedule():
    schedule.every(10).seconds.do(runHej)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    mySchedule()