import os
import traceback
from Usecase_PsdtoolResolve import PsdtoolResolveUsecase
import Modules.PySimpleGUI as sg

def __main__():
    #正直DavinciResolveのスクリプトから実行する方が手間が少ないと思ってる(PSDをDavinciResolveに置く処理もしてくれそうだし)。なのでこれは暫定的なGUI

    sg.theme('BlueMono') 

    DB_DICT_PATH =  "C:/Users/" + os.environ['USERNAME'] + "/AppData/Roaming/Blackmagic Design/DaVinci Resolve/Support/Resolve Disk Database/Resolve Projects/Users/guest/Projects"
    coms = os.listdir(DB_DICT_PATH)
    coms = sorted(coms, key=lambda f: os.stat(DB_DICT_PATH + "/" + f).st_mtime, reverse=True)
    comlist = []
    for com in coms:
        comlist.append(com) 

    layout = [  
            [sg.Text('psd_file', size=(15, 1)), sg.Input(), sg.FileBrowse('ファイルを選択', key='psd_file')],
            [sg.Button('MiniPSD生成')] ,
            [sg.Text('MiniPsd_dir', size=(15, 1)), sg.Input(key='minipsd_dir_text',enable_events=True), sg.FolderBrowse('フォルダを選択', key='minipsd_dir')],
            [sg.Text('プロジェクト名', size=(15, 1)), sg.Combo(comlist, size=(30, 1),key='project_name')],
            [sg.Text('名前', size=(15, 1)), sg.Input(key='name')],
            [sg.Button('setting生成')],
            [sg.Button('終了')]
            ]
    window = sg.Window('PSDTOOL_RESOLVE', layout)

    usecase = PsdtoolResolveUsecase()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == '終了':
            break
        elif event == 'MiniPSD生成':
            try:
                usecase.CreateMinipsd(values['psd_file'])
                minipsd_folder = os.path.dirname(values['psd_file']) + "/"
                window["minipsd_dir_text"].Update(minipsd_folder)
                window["name"].Update(os.path.splitext(os.path.basename(values['psd_file']))[0])
                sg.Popup( "MiniPSDを出力しました。")

            except Exception as e:
                print(traceback.format_exc())
                sg.PopupError( e , title="MiniPSD生成中にエラー")
        elif event == "minipsd_dir_text":
            window["name"].Update(os.path.splitext(os.path.basename(values['minipsd_dir_text']))[0][:-8])
        elif event == 'setting生成':
            try:
                usecase.CreateSettingFile(values['minipsd_dir_text'],values['project_name'],values['name'],output_dir = values['minipsd_dir_text'])
                sg.Popup( "settingFileを出力しました。Davinci ResolveのEditページのツールボックス＞ジェネレータ＞Fusionジェネレータから使えます")
            except Exception as e:
                print(traceback.format_exc())
                sg.PopupError( e , title="settingFile生成中にエラー")
    window.close()


__main__()
