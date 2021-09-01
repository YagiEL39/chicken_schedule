function modeDesignate(test=true){
  if(test){
    formID="Google FormのID(テスト用)";
    ssID="Spread SheetのID(テスト用)";
    calID="Google CalendarのID(テスト用)";
    return [formID,ssID,calID]
  }else{
    formID="Google FormのID";
    ssID="Spread SheetのID";
    calID="Google CalendarのID";
    return [formID,ssID,calID]
  }
}
function make_send_form(test=true){
  [formID,ssID,calID]=modeDesignate(test)
  if(test){
    toDay=new Date(2021,8,15);//実行する日時
    //Logger.log(formID);//チェック用関数
    makeForm(toDay,formID,ssID)
    //makeCalendar(ssID,calID)
  }else{
    toDay=new Date()
    //Logger.log(formID)
    //Logger.log(toDay);//チェック用関数
    //データを吹っ飛ばさないように本番以外はコメントアウトしておく
    makeForm(toDay,formID,ssID,calID)
    //makeCalendar()
  }
}

function formwills(wills,length=35){//シフト希望をを遺伝子化する
  result=[]
  for(let dates of wills){
    res=[...Array(length).keys()].map((i)=>{return 0})
    datas1=dates[0].split(', ');
    datas2=dates[1].split(', ');
    for(let date of datas1){
      numDate=Number(date.substr(3,2));
      res[numDate-1]=1
    }
    for(let date of datas2){
      numDate=Number(date.substr(3,2));
      res[numDate-1]=1
    }
    result.push(res);
  }
  return result
}

function formData(test=true){//シフト希望を遺伝子化してスプレッドシートに反映する。
  const toDay=new Date();
  const year=toDay.getFullYear();
  const month=toDay.getMonth(test);
  const lastDate=new Date(year,month+2,0).getDate();//次の月の月末日を取得
  [formID,ssID,calID]=modeDesignate(test);
  let spreadS=SpreadsheetApp.openById(ssID);
  let sheet1=spreadS.getSheets()[0];//フォーム結果記録用シート
  let sheet2=spreadS.getSheetByName("foropt");//最適化用成形データ記録用シート
  let lastRow=sheet1.getLastRow();
  sheet2.clear();//シート2の情報をなくす
  const days=[...Array(lastDate).keys()].map((i)=>{return i+1});
  sheet2.getRange(1,1).setValue("name")
  sheet2.getRange(1,2,1,lastDate).setValues([days]);
  names=sheet1.getRange(2,2,lastRow-1,1).getValues();
  sheet2.getRange(2,1,lastRow-1,1).setValues(names);
  //sheet2.getRange(lastRow+1,1,lastRow-1,1).setValues(names)
  willsm=sheet1.getRange(2,9,lastRow-1,3).getValues();//朝シフト希望
  wills1=formwills(willsm,lastDate);
  sheet2.getRange(2,2,lastRow-1,lastDate).setValues(wills1);
  willse=sheet1.getRange(2,12,lastRow-1,3).getValues();//夕シフト希望
  wills2=formwills(willse,lastDate);
  sheet2.getRange(2,lastDate+2,lastRow-1,lastDate).setValues(wills2);
}

function makeGoogleCal(year,month,test=true){
  [formID,ssID,calID]=modeDesignate(test);
  inputGoogleCal(year,month,ssID,calID);
}

//トリガー設定用に引数を入れた関数
function main1(){
  make_send_form(false);
  sendNotice1();
}

function main2(){
  formData(false);
  sendNotice2();
}
//GoogleCalendarへの反映
function main3(){
  [year,month]=[2021,9];//いつのカレンダーに反映させるか
  makeGoogleCal(year,month,test=false);
}