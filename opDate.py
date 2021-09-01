import datetime as dt
from calendar import monthrange

#現在の年と月を返す
def currentDate(test=False):
    if test:#テストのときは任意の時間を設定
        now=setDate(2021,8)
        return now.year,now.month
    else:#テストでない場合は現在の時間を設定
        now=dt.datetime.now()
        return now.year,now.month

#月初日を返す
def getFirstDateOf(date):
    return date.replace(day=1)
def getFirstDate(year,month):
    return dt.date(year,month,1)

#月末日を返す
def getLastDateOf(date):
    return date.replace(day=monthrange(dt.year, dt.month)[1])
def getLastDate(year,month):
    return dt.date(year,month,monthrange(year,month)[1])

def setDate(year,month,date=1):
    return dt.date(year,month,date)

def strptime(date_str):
    return dt.datetime.strptime(date_str,"%m/%d")

if __name__=="__main__":
    date=dt.datetime.today()
    date2=getFirstDateOf(date)
    print(date)
    print(date2)
    print(getFirstDate(2018,2))
    print(getLastDate(2016,2))