import os
import json
from re import S
from pytoshop import enums
from pytoshop.user import nested_layers
from pytoshop.core import PsdFile
import json
import numpy as np
from PIL import Image
from Utility_PsdtoolResolve import ResdtoolResolveUtility as util

class MiniPsdBuilder:
    OUTPUT_FOLDER = ""
    PSD = None
    PSD_SIZE = (0,0)
    PSD_LAYER_ORDER = {}

    def __init__(self,psd:PsdFile,output_folder:str):
        self.PSD = psd
        self.PSD_SIZE = psd.size
        self.OUTPUT_FOLDER = output_folder
    
    #def __createPsdPrename(self,folder_locate : list) -> str:
    #    if folder_locate == []:
    #        return ""
    #    res = ""
    #    for n in folder_locate:
    #        res += str(n)
    #        res += "-"
    #    
    #    res = res[0:-1] + "_"
    #    return res

    def __createOrder(self):
        #レイヤーの順番の情報が欠け落ちてるからいったん出しとく
        psd = self.PSD
        order = 0
        for layer in list(psd.descendants()):
            if layer.is_group():
                order += 1
                self.PSD_LAYER_ORDER[util.FormatName(layer.name)] = order
        order += 1
        print(psd.name)
        self.PSD_LAYER_ORDER[psd.name + "_image"] = order

    
    def __getLayerOrder(self,layer_name:str):
        if self.PSD_LAYER_ORDER == {}:
            return 0
        
        if(layer_name in self.PSD_LAYER_ORDER):
            return self.PSD_LAYER_ORDER[layer_name]
        else:
            return 999
        

    def createImageLayer(self,folder_path,image_file):
        # 透明度がある良い感じなレイヤーを返す

        #json読み込み
        json_file = image_file[:-4] + ".json"
        image_prop = {}
        with open(folder_path + "/" + json_file) as f:
            image_prop = json.load(f)

        #日本語パス混じりでバグるの回避でpil経由
        tmp_pil_img = Image.open(folder_path + "/" + image_file).convert("RGBA")
        if(tmp_pil_img == None):
            #存在しない場合は、1*1サイズの100%透過な画像ファイルで代用
            tmp_pil_img = Image.new("RGB", (1, 1), (0, 0, 0))
            tmp_pil_img.putalpha(0)
            image_prop["offset_x"] = 0
            image_prop["offset_y"] = 0
        img_arr = np.asarray(tmp_pil_img)

        #-1がA 0,1,2がRGBらしい
        channels = {-1:img_arr[:,:,3],0:img_arr[:,:,0], 1:img_arr[:,:,1], 2:img_arr[:,:,2]}

        layer = nested_layers.Image(name=image_file[:-4], visible=False, opacity=255, group_id=0,
                                    blend_mode=enums.BlendMode.normal, top=image_prop["offset_y"],
                                    left=image_prop["offset_x"], channels=channels,
                                    metadata=None, layer_color=0, color_mode=None)
        return layer

    def createPsdFromFolder(self,folder_path):
        # folderを指定してもらって、そこからpsdを作る
        files = os.listdir(folder_path)
        files_file = [f for f in files if f[-4:] == ".png"]

        layers = []
        for image_file in files_file:
            layer = self.createImageLayer(folder_path,image_file)
            layers.append(layer)

        if(layers == []):
            return

        psd = nested_layers.nested_layers_to_psd(layers, color_mode=3, size=self.PSD_SIZE)
        psd_file_name = os.path.basename(os.path.dirname(folder_path + "/"))

        output_file_name = str(self.__getLayerOrder(psd_file_name)).zfill(3) + "_" + psd_file_name + ".psd"
        with open(self.OUTPUT_FOLDER + "/" + output_file_name, 'wb') as fd2:
            psd.write(fd2)

        print(folder_path + "/" + psd_file_name + " 出力しました")
        return


    def __invokerForCreatePsd(self,folder_path):
        #生成されたフォルダーごとにcreatePsdFromFolderを実行するためのやつ。とっても再帰的
        #folder_locateとlevelは今どのディレクトリの階層を処理中か…みたいなやつ(psdの名付け用)
        #my_folder_locate = list(folder_locate)
        #my_folder_locate.append(0)

        files = os.listdir(folder_path)
        files_dir = [f for f in files if os.path.isdir(os.path.join(folder_path, f))]

        for dir in files_dir:
            #my_level = level + 1
            #my_folder_locate[level] = my_folder_locate[level] + 1
            self.__invokerForCreatePsd(folder_path + dir + "/")
        self.createPsdFromFolder(folder_path)

    def createMiniPsd(self,folder_path:str):
        util.createDirectory(self.OUTPUT_FOLDER)
        self.__createOrder()
        
        self.__invokerForCreatePsd(folder_path)
        