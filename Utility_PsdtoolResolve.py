import re 
import os

class ResdtoolResolveUtility:
    @classmethod
    def FormatName(cls, text:str):
        #フォルダ名にできない名前だったりを良い感じに変換する
        
        #フォルダ作成時の禁止用語コンバート
        text = re.sub(r'[\\/:*?"<>|]+','',text)
        text = text.replace('\x00','')
        if(text == ""):
            text = "_"
        
        return text

    @classmethod
    def createDirectory(cls, path:str):
        #いいかんじにディレクトリを作成する
        
        # 既に存在してたら消す実装にはしてたんだけど、配布先で事故ったらこわいな・・・隠しとこ・・・
        # if os.path.isdir(path):
        #     shutil.rmtree(path)
        os.makedirs(path)


