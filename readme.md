# Py JoinLogoSCP Encode
## 概要

* TSファイルまたはM2TS(拡張子をTSにすることで、TSファイルとして扱えるもの)を読み込み
* JoinLogoSCPで処理
* 上記処理でresultフォルダに出力されたin_cutcm_logo.avsをAviUtlでエンコード
* 上記処理の際、エラーとなる原因がファイル名に含まれる場合、リネームする
* (ついでに処理状態をLine Notifyに投げる)

　上記を自動化するためにpythonで作成したものです。

---
## 開発環境
* Python > 3.10(PyCharm)
* AviUtl > 110
* AUC > 1.5
* JoinLogoSCP > join_logo_scp_set_v4

---
## 使い方
### 下準備
* JoinLogoSCPのセットアップ（ツールのインストール、ロゴファイル準備含む）が必要です。
* AviUtl+AUC+プラグイン出力(x264など)の設定が必要です。
* [JoinLogoSCPのセットアップはこのサイト](https://enctools.com/join-logo-scp/#toc4)が参考になると思います。
* [AviUtl+AUCのセットアップはこのサイト](https://www.cg-method.com/aviutl-aviutl-control/)が参考になると思います。
* AviUtlやプラグイン出力の設定はお好みで。

### ツールの設定
* 各ツールの保存先がデフォルト以外の場所の場合、初回起動時に選択画面が表示されます。
* デフォルトの場合の各ツール配置は下記画像の通りです。 ※.py->.exeに置き換えて下さい。
  ![pyjlsenc_dir.png](img%2Fpyjlsenc_dir.png)
* Line通知には別途設定が必要です。(必須ではありません。)
* Line通知を設定すると、「1/2「●動画名●」変換開始」などのメッセージがLineに届きます。

### Line通知をする場合
* Line Notifyのパーソナルアクセストークンを発行し、登録、テストする必要があります。
* [Line Notify](https://notify-bot.line.me/ja/)にアクセス、ログイン後「トークンを発行する」から発行してください。
* トークン名は何でも構いません。
* 通知の送信先は「1:1でLineNotifyから通知を受け取る」を選択してください。
* トークンは1度しか表示されません。何らかの理由で紛失した場合は削除、再作成してください。
#### 設定方法
* Line Token設定をクリックします。
　![main_window0.2.png](img%2Fmain_window0.3.png)
* Tokenを入力(Ctrl+Vで貼り付けも可)し、OKをクリック。その後閉じてください。
　![line_token_window.png](img%2Fline_token_window.png)
* 一度設定すると、開くことはできません。
* Tokenを変更する場合は下記を参考に手動でconfig.iniを編集してください。
* 初期値(未設定の場合)は0です。

#### 設定方法(config.ini書き換え)
* 本ツールを1度でも起動すると作成されるconf/config.iniをテキストエディタで開きます。
* [Line]の下にある「key = 」にトークンを記入します。(例：key = ABCDEF...)
* 記入後、起動するとテストメッセージが送信されます。送信できると有効になります。
* なお、無効にする場合は[Line]の下を「enable = False」と記入して保存してください。

### 処理の実行
1. 設定が全て完了していると、.tsまたは.m2tsの選択画面が表示されます。
2. 複数選択した場合はファイル名によるソート後、下記処理が開始されます。
3. ファイル名の末尾(123.tsの場合3の部分)に空白が含まれる場合、削除しリネームします。
4. ファイル名に全角空白が含まれる場合、半角空白に置換します。
5. .m2tsを選択すると.tsにリネームします。
6. jlse_bat.batに処理を投げます。(設定されている場合、Line通知されます。)
7. 完了後、aviutlをaucにより起動、in_cutcm.avsを読み込み、指定のプラグイン出力を開始します。
8. 複数ファイルの場合、次のファイルを対象に3.から繰り返します。
9. (設定されている場合、Lineに完了を通知します。)

---
## その他
* config.iniを手動で編集した場合、動作設定から読み込む必要があります。
* 動作時は起動日時のログファイル(テキスト)をlog/以下に生成します。
* 各ツールのエラーは収集しません。
* 動かない場合は主にパスに問題があるか、それぞれのツールが手動でも動かない状態である可能性があります。
パスを確認し、手動で問題なく動作するか確認してください。
* 自分に需要があったので作ったものです。
* AYOR

