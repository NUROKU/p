Davinci Resolveで、PsdToolライクなFusionTemplateを出力します

詳しく言うと、PSDファイルをグループごとに別のPSDファイルに分割(以後MiniPSD)。
MiniPSDを参照しつついい感じにするFusionTemplateを出力するツールです。


--------------------------------------------
操作方法(用意するもの、PSDファイル)

1,PSDTool_resolve.exeを実行

2,psd_fileを指定し、「MiniPSD生成」ボタンを押す
 →psdファイルがおかれていた場所に「{psd名}_Image」「{psd名}_miniPSD」が出力されます

3,Davinci Resolveを実行し、2の実行で出力されたMiniPSDフォルダ配下のpsdファイルを全てMediaPoolに置く
 →このとき、プロジェクトの名前をメモっといてください

4,PSDTool_resolve.exeを実行し、パラメータを指定して「setting生成」ボタンを押す
 MiniPsd_dir : MiniPsdが出力されているディレクトリ、2で出力された{psd名}_miniPSDを指定してください
 プロジェクト名： 3で置いたプロジェクトのパス
 名前：出力されるファイルの名前、好きな名前をつけてください
 

4まで正常に実行されると、Davinci Resolveのエディットページ > ツールボックス > ジェネレータ > Fusionジェネレーターに
PSDToolライクなFusionTemplateが出力されています。
（ついでにminiPSDディレクトリ下にもTemplateが出力されてます。Fusionページにドラッグ＆ドロップすると使えるはず）

---------------------------------------------
その他

FusionTemplateを消したい時:
 ↓のパスに置いてあるやつを消せば大丈夫です
 C:\Users\ ｛ユーザ名｝ \AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Templates\Edit\Titles

Davinci Resolveのエディットページで使ってみたけど、選択肢が反応しない：
 仕様です、ちょっとだけ時間置いてください。（配備されてから基のPSDファイルを参照しに行く形なので）
  →対応策見つけたかもしれないのでちょっと頑張っています

Davinci Resolveの別プロジェクトだと使えない：
 仕様です、公式が良い感じのアプデしたらいずれ使えるようになるかもしれない

エラーが起きた時：
 連絡いただけるとありがたいです
