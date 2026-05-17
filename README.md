# SSPDM_Scratch-Studio-Project-Data-Meter
scratchのスタジオ統計情報。

このフォルダには、Scratchスタジオの統計を取得する
`studio_meter.py` を追加しています。

使い方:
1.緑色のボタン、<> CodeからDownload ZIPをします。

2.ダウンロードしたZIPファイル、「SSPDM_Scratch-Studio-Project-Data-Meter」を展開します。
windowsの場合、「ファイルを下のフォルダーに展開する(F):」が表示されるので、
C:\Users\自分のユーザー名\Downloads\　にします。心配な方は、「右の参照(R)」から、「ダウンロード」フォルダを選択しましょう。

3.展開された、「SSPDM_Scratch-Studio-Project-Data-Meter-main」フォルダに入り、
「README.md」と、「studio_mater.py」があることを確認します。右クリックから、「ターミナルで開く」を押し、

「py -3.11 studio_meter.py 数字」と入力します。
コピペ推奨。数字は好きなスタジオの番号にしてください。
(https://scratch.mit.edu/studios/00000000←この部分が番号)

pythonが無いと弾かれる場合があるので、「python　インストール方法」で調べてインストールしてください。

上手くいくと、「スタジオからプロジェクト取得中...[42s]」のように表示されます。
あとはしばらく待つだけです。



出力結果は `data` フォルダに日時付きの txt ファイルとして保存されます。
