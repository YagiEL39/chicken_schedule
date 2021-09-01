# -*- coding: utf-8 -*-
from opDate import getLastDate,currentDate,setDate
import rwData as rwd
import random
import datetime as dt
import numpy as np

from deap import base,creator,tools,cma

###getDataからの入力を整理###
#年と月の指定
year,month=currentDate(test=True)
month+=1
#月末日=その月の日数を取得
lastdate=getLastDate(year,month).day#GASと違いdayで日にちを取得する
#シフト数=月数×朝夕
numshift=2*lastdate


#作成した各員の希望シフトを返す
names,wills=rwd.makeDatas()
workers_init=rwd.makeWorkers(names,wills)
numworkers=len(workers_init)
lengene=numworkers*numshift
#平均シフト数
ave_numshift=numshift/numworkers

# シフトを表すクラス
# 内部的には 2(朝夕) * 1月の日数(約30日) * 入力した人数の長さの
class Shift:
    # シフトの名称を定義
    SHIFT_BOXES = []
    for i in range(1,lastdate+1):
        date= setDate(year,month,i).strftime("%m/%d")
        SHIFT_BOXES.append("%s朝"%date)
        SHIFT_BOXES.append("%s夕"%date)
    # 各コマの想定人数
    number_Need = np.ones((numshift,),dtype=int)
    #日にち
    DATES=np.array([i for i in range(1,lastdate+1)],dtype=int)
    
    #コンストラクタ
    def __init__(self, list):
        self.list = list#遺伝子を格納
        self.workers = []#workersは後からでも入れられるようにからの配列を用意しておく

    ##計算・情報成形用メソッド
    # ランダムなデータを生成
    def make_sample(self):
        sample_list = np.array([np.random.randint(0,2) for _ in range(lengene)],dtype=int)
        self.list = sample_list

    # 遺伝子を人ごとに分割
    def slice(self):
        lis=np.copy(self.list)
        sliced = lis.reshape(numworkers,lengene//numworkers)
        return sliced

    #ユーザ別にアサインコマ名を出力する
    def print_inspect(self):
        for user_no,line in enumerate(self.slice()):
            print(self.workers[user_no].name)#名前の出力
            print(line)#シフトの出力
            for ind,shif in enumerate(line):#勤務日の出力
                if shif == 1:
                    print(self.SHIFT_BOXES[ind])#対応する表記で出力
    
    #実態(どの日に何人入ることになっているか)
    def number_Actual(self):
        sliced=self.slice()
        res=np.empty((numshift,),dtype=int)
        for i in range(numshift):
            res[i]=np.sum(sliced[:,i])
        return res
    
    # CSV形式でアサイン結果の出力をする
    def print_csv(self):
        for line in self.slice():
            print(','.join(map(str, line)))

    # TSV形式でアサイン結果の出力をする
    def print_tsv(self):
        for line in self.slice():
            print("\t".join(map(str, line)))
    
    ##評価関数用メソッド
    #必要数と実態との差->最小化
    def delta_bet_Need_and_Actual(self):
        res=np.empty((numshift,),dtype=int)
        delta=self.number_Need-self.number_Actual()
        for ind,cont in enumerate(delta):
            res[ind]=np.abs(cont)
        return res

    #世話できない日にアサインされている数->最小化
    def not_Applicated_Assign(self):
        sliced=self.slice()
        count = 0
        for ind,line in enumerate(sliced):
            unwill=line-self.workers[ind].wills#現在のシフトと希望シフトの差
            for cont in unwill:
                count+=max(0,cont)
        return count

    #平均シフト数と実態との差->最小化
    def delta_bet_AVE_and_Actual(self):
        sliced=self.slice()
        deltas=np.array([np.abs(np.sum(line)-ave_numshift) for line in sliced],dtype=int)
        return deltas


##評価関数の定義
#来れない日は入れない
#できるだけ多くの日数人が入るようにする
#できるだけ同じ日数入る
def evalShift(individual):
    s = Shift(individual)
    s.workers = workers_init
    # 想定人数とアサイン人数の差
    delta_NA= np.sum(s.delta_bet_Need_and_Actual()) / lengene
    # 世話できない日にアサインされている数
    nAA = s.not_Applicated_Assign() / lengene
    # 各人員のシフト数をならす
    delta_AA = np.sum(s.delta_bet_AVE_and_Actual()) / numworkers
    return (delta_NA,nAA,delta_AA)

##GA関係の設定
def set_GA():
    ###GA関係の設定creator###
    #適応度の重みの設定
    #目的関数は
    #希望しない日時には人を入れないこと
    #全員ができるだけ同じ日数入ること->
    creator.create("FitnessPeopleCount", base.Fitness, weights=(-50.0, -2000.0, -1.0))
    #個体の設定
    creator.create("Individual", np.ndarray, fitness=creator.FitnessPeopleCount)

    ###GA関係の設定toolbox###
    toolbox = base.Toolbox()
    #遺伝子作成関数の登録(値0か1をランダムで返す)
    toolbox.register("attr_bool", random.randint, 0, 1)
    #設定した個体生成規則に基づいて、指定した長さの個体を登録
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, lengene)
    #個体群格納方法の登録
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    #評価関数を設定
    toolbox.register("evaluate", evalShift)
    # 交叉関数を設定(二点交叉)
    toolbox.register("mate", tools.cxTwoPoint)
    # 変異関数を登録(ビット反転)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    # 選択関数を登録(トーナメント選択)
    toolbox.register("select", tools.selTournament, tournsize=3)#tournsizeは各トーナメントで評価される個体数
    return toolbox

##main実行部分
if __name__ == '__main__':
    NPOP =100#個体数
    CXPB =0.6#交叉確率
    MUTPB=0.5#変異確率
    NGEN =500#世代数
    toolbox=set_GA()
    # 初期集団を生成する
    pop = toolbox.population(n=NPOP)
    #GA開始
    print("-- start evolution --")
    # 初期集団の個体を評価する
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):  # zipは複数変数の同時ループ
        # 適合性をセットする
        ind.fitness.values = fit

    #print("%i individuals are evaluated" % len(pop))

     # 進化計算開始
    for g in range(1,NGEN+1):
        print("--%i generation--" % g)

        # 選択
        # 次世代の個体群を選択
        offspring = toolbox.select(pop, len(pop))
        # 個体群のクローンを生成
        offspring = list(map(toolbox.clone, offspring))

        # 選択した個体群に交差と突然変異を適応する

        # 交叉
        # 偶数番目と奇数番目の個体を取り出して交差
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                # 交叉された個体の適合度を削除する
                del child1.fitness.values
                del child2.fitness.values

        # 変異
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # 適合度が計算されていない個体を集めて適合度を計算
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        #print("%i individuals are evaluated" % len(invalid_ind))

        # 次世代群をoffspringにする
        pop[:] = offspring

    print("-- end evolution --")

    best_ind = tools.selBest(pop, 1)[0]
    print("best individual: %s, %s" % (best_ind, best_ind.fitness.values))
    s = Shift(best_ind)
    #s.print_inspect()
    #s.print_csv()
    #s.print_tsv()

    #workersに結果の格納(名前と番号は格納済み)
    
    wills_res=s.slice()
    workers_res=rwd.makeWorkers(names,wills_res)
    rwd.writeShift_forCheck(workers_init,workers_res)

    Checked=input("Are you Checked? Y/N-> ")
    if Checked=="Y"or Checked=="y":
        #チェック後に動作
        names_checked,wills_checked=rwd.makeDatas("CheckedShift.csv")
        workers_Checked=rwd.makeWorkers(names_checked,wills_checked)
        rwd.writeShift_forGoogleCal(workers_Checked)