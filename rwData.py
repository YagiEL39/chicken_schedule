import os
import numpy as np
from opDate import getLastDate,setDate,currentDate,getFirstDate

#データ読み書き
#いつのシフトかを確定させる
year,month=currentDate(test=True)
month+=1

#月末日=その月の日数を取得
lastdate=getLastDate(year,month).day#GASと違いdayで日にちを取得する
#シフト数=月数×朝夕
numshift=2*lastdate

#workerクラスの定義
class worker:
    SHIFT_BOXES = []
    for i in range(1,lastdate+1):
        date= setDate(year,month,i).strftime("%m/%d")
        SHIFT_BOXES.append("%s朝"%date)
        SHIFT_BOXES.append("%s夕"%date)
    def __init__(self,no,name,wills):
        self.no=no#番号
        self.name=name#名前
        self.wills=wills#シフト希望

    def nameShift(self):
        res=[]
        for ind,cont in enumerate(self.wills()):
            if cont==1:
                res.append(self.SHIFT_BOXES[ind])
    
    def Shift_str(self):#シフトを文字列として出力
        data=[]
        for i in self.wills:
            if i==1:#シフトがある日
                data.append("O")
            else:#シフトがない日
                data.append("X")
        res1=",".join(data[:lastdate])
        res2=",".join(data[lastdate:])
        return self.name,res1,res2

    def Shift_int(self):#シフトを数値として出力
        data=[]
        for i in self.wills:
            if i==1:#シフトがある日
                data.append("1")
            else:#シフトがない日
                data.append("0")
        res1=",".join(data[:lastdate])
        res2=",".join(data[lastdate:])
        return self.name,res1,res2

#データの成形
def form_data(string):
    splitted=string.split(",")
    formed=[]
    for i in splitted:
        formed.append(int(i.strip(" ")[3:5]))
    return formed

#csvファイルからの読み込み
def makeDatas(file="Data.csv"):
    with open(file,"r",encoding="utf_8_sig") as f:
        f.readline()
        ds=f.readlines()
        names=[]
        wills=[]
        for line in ds:
            splitted=line.strip("\n").split(",")
            names.append(splitted[0])#名前の取得
            will=np.array(list(map(int,splitted[1:])))
            wills.append(will)
        return names,wills

#スプレッドシートから入力情報を読み取り、workerクラスを作成し返す
def makeWorkers(names,wills):
    if len(names)!=len(wills):
        return []
    else:
        workers=[]
        for ind,(name,will) in enumerate(zip(names,wills)):
            worker1=worker(ind,name,will)
            workers.append(worker1)
        return workers

#シフトの出力(チェック用)
def writeShift_forCheck(workers_init,workers_res):
    with open("Shift.csv","w+",encoding="utf-8") as f:
        dates=["name"," "]
        dates.extend([str(i) for i in range(1,lastdate+1)])
        f.write(",".join(dates)+"\n")
        for work_init,work_res in zip(workers_init,workers_res):
            name,mor_init,eve_init=work_init.Shift_int()
            _,mor_res,eve_res=work_res.Shift_int()
            f.write(name+",result,"+mor_res+","+eve_res+"\n")
            f.write(" ,application,"+mor_init+","+eve_init+"\n")
#途中
def writeShift_forCalendar(workers_res):
    dictDay={"Sun":0,"Mon":1,"Tue":2,"Wed":3,"Thu":4,"Fri":5,"Sat":6}
    with open("Calendar.csv","w+") as f:
        year,month=currentDate(test=True)
        month+=1
        lastdate=getLastDate(year,month).day
        dates=[i for i in range(1,lastdate+1)]
        Firstday=getFirstDate(year,month).strftime("%a")#月初日の曜日
        locFirstday=dictDay[Firstday]
        f.write("Shift for,{}/,{}\n".format(year,month))
        f.write()
        f.write("\n\n")#朝夕シフト分の改行
#Googleカレンダー反映用    
def writeShift_forGoogleCal(workers_res):
    with open("GoogleCal.csv","w+",encoding="utf_8_sig") as f:
        dictName={}
        for work in workers_res:
            dictName[work.no]=work.name
        workers_will=[work.wills for work in workers_res]
        workers_np=np.array(workers_will,order="F")
        for i in range(lastdate):
            for ind,j in enumerate(workers_np[:,i]):
                if j==1:#朝シフト
                    f.write("{},morning,{}\n".format(i+1,dictName[ind]))
            for ind,j in enumerate(workers_np[:,lastdate+i]):
                if j==1:#夕シフト
                    f.write("{},evening,{}\n".format(i+1,dictName[ind]))

        



if __name__=="__main__":
    #print(makeWorkers()[0].wills)#0番目の人の希望シフト
    #print(setDate())
    print(makeDatas())
