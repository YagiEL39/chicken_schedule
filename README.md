# chicken_schedule

README 作成中...

## プログラム概要
数人共同で鶏の世話をしてます。ところで毎月の仕事のシフト調整だるくないですか?自動化できたら楽じゃないですか?

シフト調整にはこんな感じの行程があります。

- 調整さんなりLINEなりで各員のシフト希望を集計
- 色々気にしながらシフト調整
- シフトをカレンダーにまとめて公開

いやーだるいですね...

シフト調整するのにも、考慮することは山ほど...

- 皆ができるだけ同じ日数入れるように
- 希望してない日にちにシフトを入れないように
- シフト毎に必要人数を過不足なくアサインする

e.t.c.

じゃあこいつらぜーんぶ自動化できたら嬉しいですね!!

このプログラムは以下のことを勝手にやってくれます。

1. Googleフォームの自動作成(GAS)
2. フォームの作成後に、作成できた旨の連絡(GAS) [^1]
3. 集計したシフト希望をもとに、GAでシフトの最適化(Python)
4. Googleカレンダーにシフトを登録(GAS) [^2]

[^1]: できればLINEbotとかを利用してフォームのリンク送るところまで自動でやりたい

[^2]: こっちもできればシフト確認に自動で応答できるようなLINEbotを作りたい


# 諸々の設定
GASのフォームやスプレッドシート、カレンダー機能を利用している関係で、必要な設定がいくつかあります。あとPython側もいくつか設定設定してほしい部分があります。
## GAS

### IDの設定
テスト用と本番用で2つ用意しておくといいかも

### トリガーの設定
定期的(月1回)に実行するのでmain.gs内の2つの関数にトリガー設定をします。

1. main1
   
   Googleフォームを自動作成する関数。
   毎月15日に実行するようトリガー設定
2. main2
   
   集計したシフト希望をGAで用いる遺伝子化するための関数。
   毎月27日に実行するようトリガー設定

## Python

### DEAPのインストール
進化計算ライブラリDEAPのインストールが必要です。

```
pip install deap
```
# 今後の課題
GASからPython,PythonからGASのデータの流れをスムーズにする。現状手動でcsvファイルのダウンロードとアップロードが必要です。

