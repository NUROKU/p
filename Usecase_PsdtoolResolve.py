import os
from psd_tools.api.psd_image import PSDImage
from ImageMigrator import ImageMigrator
from MiniPsdBuilder import MiniPsdBuilder 
from ResolveSettingCreator import ResolveSettingCreator

class PsdtoolResolveUsecase:

    def CreateMinipsd(self,psdpath:str):
        #psdを画像に分解した上で、グループごとにまとめたMiniPSDを出力します
        try:
            psd = PSDImage.open(psdpath)
            folder_name = os.path.dirname(psdpath)
            file_name = os.path.splitext(os.path.basename(psdpath))[0]
            png_folder = folder_name + "/" + file_name + "_Image" + "/"
            minipsd_folder = folder_name + "/" + file_name + "_MiniPSD" + "/"
        except Exception as e:
            raise ValueError("PSDファイルが見つかりません。指定されたパスを見直してください")

        print("pngファイル出力開始")
        image_migrator = ImageMigrator()
        image_migrator.psdToPng(psd,png_folder)

        print("psdファイル作成開始")
        minipsd_builder = MiniPsdBuilder(psd,minipsd_folder)
        minipsd_builder.createMiniPsd(png_folder)


    def CreateSettingFile(self,minipsd_dir:str,project_name:str,file_name:str,output_dir = "./"):
        #DavinciResolveでPsdToolKitライクに使えるsettingファイルを作ります。

        print("settingファイル作成開始")
        resolve_setting_creator = ResolveSettingCreator(project_name,output_dir,file_name)
        resolve_setting_creator.createSetting(minipsd_dir + "/")


        pass

