import traceback
from Usecase_PsdtoolResolve import PsdtoolResolveUsecase
import PySimpleGUI as sg
#UIつくるかあ

def __main__():
    sg.theme('BlueMono') 

    layout = [  
            [sg.Text('psd_file', size=(15, 1)), sg.Input(), sg.FileBrowse('ファイルを選択', key='psd_file')],
            [sg.Button('MiniPSD生成')] ,
            [sg.Text('MiniPsd_dir', size=(15, 1)), sg.Input(), sg.FolderBrowse('フォルダを選択', key='minipsd_dir')],
            [sg.Text('プロジェクト名', size=(15, 1)), sg.Input(key='project_name')],
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
                sg.Popup( "MiniPSDを出力しました。")
            except Exception as e:
                sg.PopupError( e , title="MiniPSD生成中にエラー")
        elif event == 'setting生成':
            try:
                usecase.CreateSettingFile(values['minipsd_dir'],values['project_name'],values['name'],output_dir = values['minipsd_dir'])
                sg.Popup( "settingFileを出力しました。Davinci ResolveのEditページのツールボックス＞ジェネレータ＞Fusionジェネレータから使えます")
            except Exception as e:
                print(traceback.format_exc())
                sg.PopupError( e , title="settingFile生成中にエラー")
    window.close()


__main__()