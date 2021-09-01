///----month list----////
const monListEn=["January","February","March","April","May","June","July","August","September","October","November","December"];
const monListJp=["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"];

class Person{
  //コンストラクタ
  constructor(name,cando,maydo,cantdo){
    this.name=name;//名前
    this.cando=cando;//可能な日
    this.maydo=maydo;//できるかもしんない日
    this.cantdo=cantdo;//できない日
    this.shifts=0;//シフト回数
    this.shift=Person.makeShift(this.cando,this.maydo,this.cantdo);//データ成形後の可能シフト(実際のシフトではない)
    ////----test----////
    //for(let elem of this.shift.entries()){
      //Logger.log(elem);
    //}
  }
  //フォーマット
  static format1(day){//Date型のフォーマット
    return Utilities.formatDate(day,"JST","MM/dd");
  }
  static format2(day){//MM/dd(EEE)からddのみ切り出してNumber型で返す
    return Number(day.substr(3,2))-1;//"04"とかでも普通に4にしてくれるらしい 1引いとかないとインデックスが一致しなくなる。
  }
  static initialShift(){
    let initialShift=Array(31);//月の日数分の配列の取得->最大の31にしておく
    initialShift.fill(-1);//-1埋め->無回答のときは-1
    return initialShift;
  }
  static makeShift(cando,maydo,cantdo){//can->2,may->1,cantか無回答->0
    let shiftmap=Person.initialShift();
    let pa=cando.concat();
    let pb=maydo.concat();
    let pc=cantdo.concat();//不要だけど一応、ね。

    for(const elem of pa){//cando
      if(elem!==""){
        shiftmap[Person.format2(elem)]=2;
      }
    }
    for(const elem of pb){//maydo
      if(elem!==""){
        shiftmap[Person.format2(elem)]=1;
      }
    }
    for(const elem of pc){//cantdo
      if(elem==""){
        shiftmap[Person.format2(elem)]=0;
      }
    }
    return shiftmap
  }
  
  //セッター
  set setName(name){
    this.name=name
  }
  set setCando(cando){
    this.cando=cando;
    this.shift=Person.makeShift(this.cando,this.maydo,this.cantdo);
  }
  set setMaydo(maydo){
    this.maydo=maydo;
    this.shift=Person.makeShift(this.cando,this.maydo,this.cantdo);
  }
  set setCantdo(cantdo){
    this.cantdo=cantdo;
    this.shift=Person.makeShift(this.cando,this.maydo,this.cantdo);
  }
}

function makeForm(toDay,formID,ssID){//Googleフォームの変更->毎月15日に実行
  //IDでフォームとスプレッドシートを開く
  let form=FormApp.openById(formID);
  let spreadS=SpreadsheetApp.openById(ssID);

  //何月の予定か設定
  const curDate=new Date(toDay.getFullYear(),toDay.getMonth()+2,0);//対象月の末日を記録しておくと扱いやすい
  const curYear=curDate.getFullYear();//対象の年
  const curMonth=curDate.getMonth();//対象の月
  const lastDate=curDate.getDate();//対象の月の最終日
  let Date_for_column=new Date(curYear,curMonth,1);//質問カラム作成用
  //Logger.log(curDate);//チェック用

  ////----スプレッドシートをきれいにする----////
  const sheet1=spreadS.getSheets()[0];//フォームの回答が記録されるところ
  const sheet2=spreadS.getSheetByName("record");//いままでの回答が記録されるところ
  //const sheet3=spreadS.getSheetByName("foropt");//最適化に使うデータを記録(トリガーを別日=27日に設定してるので使わん)
  const lastRow1=sheet1.getLastRow();
  const lastRow2=sheet2.getLastRow();
  if(lastRow1>1.0){
    const prevName=sheet1.getRange(2,2,lastRow1-1,1).getValues();
    const prevData=sheet1.getRange(2,9,lastRow1-1,6).getValues();//先月の回答

    sheet2.getRange(lastRow2+1,1).setValue(new Date(curYear,curMonth-1,1));//何月のデータか記録
    sheet2.getRange(lastRow2+1,2,lastRow1-1,1).setValues(prevName);
    sheet2.getRange(lastRow2+1,3,lastRow1-1,6).setValues(prevData);//先月のデータを移転
    sheet1.deleteRows(2,lastRow1-1);
    
  }
  sheet1.deleteColumns(3,6);

  ////----ここまででスプレッドシートをきれいにしておく----////

  ////----ここからフォームの作成----////
  //利用する関数・回答条件の定義
  function format(day){//フォームの項目用フォーマットe.g.6/1(Tue)
    return Utilities.formatDate(day,'JST',"MM/dd(EEE)")
  }

  var checkboxGridValidation = FormApp.createCheckboxGridValidation()//チェックボックス型の回答方法に関する規制
  .setHelpText("select one item per column.")
  .requireLimitOneResponsePerColumn()
  .build();
  
  //フォーム関係の設定
  const formURL=form.getPublishedUrl();//フォームの回答用URL
  const listItems=form.getItems();//フォーム内のアイテムオブジェクト(質問など)をリスト化して取得

  //質問のrowとcolumn
  let column=[]
  let row=["可能 I can do","できるかもしれない I may do","不可能 I can't do"];

  //設定された月の日付をカラムに記録
  for(var i=1;i<=lastDate;i++){
    Date_for_column.setDate(i);
    column.push(format(Date_for_column));
  }

  //質問はインデックスで保持されているので、インデックスを選択して、それをチェックボックス型の質問であると定義する必要がある。
  //質問2(朝シフト)
  const Q2=listItems[1].asCheckboxGridItem();
  Q2.setTitle("世話できる日(朝10時) Which date can you do the morning shift(10 a.m.)?")//朝シフトフォーム作成
  .setRows(row)
  .setColumns(column)
  .setRequired(false)//必須回答はfalseに
  .setValidation(checkboxGridValidation);

  //質問3(夜シフト)
  const Q3=listItems[2].asCheckboxGridItem();
  Q3.setTitle("世話できる日(夕5時) Which date can you do the evening shift(5 p.m.)?")//よるシフトフォーム作成
  .setRows(row)
  .setColumns(column)
  .setRequired(false)//必須回答はfalseに
  .setValidation(checkboxGridValidation);

  //フォームタイトル
  form.setTitle("鶏世話スケジュール"+curYear+"年"+monListJp[curMonth]+"\nChicken Care Schedule "+monListEn[curMonth]+", "+curYear);

  ////----ここまででGoogleフォーム作成は完了----////
}

function makeCalendar(ssID,calID){//カレンダーの作成
  //IDでカレンダーとスプレッドシートを開く
  let spreadS=SpreadsheetApp.openById(ssID);
  let Cal=CalendarApp.getCalendarById(calID);
  //何月の予定か設定
  const curDate=new Date(toDay.getFullYear(),toDay.getMonth()+2,0);//対象月の末日を記録しておくと扱いやすい
  const curYear=curDate.getFullYear();
  const curMonth=curDate.getMonth();
  const lastDate=curDate.getDate();
  let Date_for_Cal=new Date(curYear,curMonth,1)//カレンダー用
  //Logger.log(curDate);//チェック用

  const ssCal=spreadS.getSheetByName("Calendar");
  ssCal.getRange(1,5).setValue("Shift "+monListEn[curMonth]+" "+monListJp[curMonth]);//タイトルの変更
  const firstDay=Date_for_Cal.getDay();//月初日の曜日の取得
  function mapDay(d){//日にち→曜日→データ位置の写像
    const day=d-1+firstDay
    const column=day%7+2
    const row=3*(Math.floor(day/7)+1)
    return [row,column]
  }
  ssCal.getRange(3,2,1,7).setValue("");
  for(var i=1;i<=lastDate+7;i++){
    const pos=mapDay(i)
    if(i<=lastDate){
      ssCal.getRange(pos[0],pos[1]).setValue(i)
    }else{//前の月のデータを""で上書きして消しておく
      ssCal.getRange(pos[0],pos[1]).setValue("")
    }
  }
  for(var i=0;i<=5;i++){
    ssCal.getRange(3*i+4,2,2,7).setValue("");
  }
}

function inputGoogleCal(year,month,ssID,calID){//決まったシフトをGoogleカレンダーに記録
  let Cal=CalendarApp.getCalendarById(calID);
  let spreadS=SpreadsheetApp.openById(ssID);
  const sheet4=spreadS.getSheetByName("forGC");
  const lastRow4=sheet4.getLastRow();
  const datas=sheet4.getRange(1,1,lastRow4,3).getValues();
  //イベント削除
  const s_time=new Date(year,month-1,1);
  const e_time=new Date(year,month,0);
  const events = Cal.getEvents(s_time, e_time);
  if(events.length>0){
    for(const event of events){
      event.deleteEvent();
      Utilities.sleep(500);
    }
  }
  //イベント削除完了

  //イベント追加
  let se_time=new Date(year,month-1,1);
  for(let data of datas){
    const title=data[2]+"鶏シフト";//シフト名
    se_time.setDate(data[0]);//日までのデータをここで作って後はifで朝か夕を分岐
    if(data[1]==="morning"){
      se_time.setHours(10);
    }else if(data[1]==="evening"){
      se_time.setHours(17);
    }
    //Logger.log(title)
    //Logger.log(se_time)
    
    Cal.createEvent(title,se_time,se_time);//予定名,開始時間,終了時間
    Utilities.sleep(500);//高速に処理するとエラーが出るのでsleepする
  }
  //イベント追加完了
}

function sendNotice1(URL){//Googleフォームのリンクを送るようリマインドする
  let toAdr="送り先アドレス";//
  let subj="[定期通知]GoogleフォームLINEせよ";//メールタイトル
  let name="送信者名";
  let body="来月の予定をGoogleフォームに入力してください。\nPlease answer your schedule for the next month\n"+URL;//メール本文
  MailApp.sendEmail({to:toAdr,subject:subj,name:name,body:body});
}

function sendNotice2(){//スケジュール表完成時に実行される
  let toAdr="送り先アドレス";
  let subj="[定期通知]最適化せよ";//メールタイトル
  let name="送信者名";//
  let body="遺伝子が集まったので最適化してください";//メール本文
  MailApp.sendEmail({to:toAdr,subject:subj,name:name,body:body});
}