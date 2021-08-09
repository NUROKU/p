from logging import exception
import re
import os
import json
from pytoshop.core import PsdFile
from Utility_PsdtoolResolve import ResdtoolResolveUtility as util

class ImageMigrator:
#psdの中を読み取ってpngとかjsonとかにして出力するやつ
    def __savePng(self, layer,output_folder_path):
        pil_img = layer.topil()
        if pil_img != None:
            pil_img.save(output_folder_path + util.FormatName(layer.name) + ".png")
        pass

    def __saveJson(self, layer, output_folder_path):
        output_json = {
            "size_width": layer.size[0],
            "size_height": layer.size[1],
            "offset_x": layer.offset[0],
            "offset_y": layer.offset[1]
            }
        with open(output_folder_path + util.FormatName(layer.name) + ".json", mode='w') as f:
            json.dump(output_json, f, indent=2, ensure_ascii=False)


    def layerToPng(self,layer,output_folder_path):
        print(layer)
        if layer.is_group():
            output_folder_path += util.FormatName(layer.name) + '/'
            util.createDirectory(output_folder_path)
            for child_layer in layer:
                self.layerToPng(child_layer,output_folder_path)
        else :
            #こういうリポジトリ/データストアな奴は外出しされるべき。
            self.__savePng(layer,output_folder_path)
            self.__saveJson(layer,output_folder_path)

    def psdToPng(self, psd:PsdFile, output_folder_path:str):
        util.createDirectory(output_folder_path)
        for layer in psd:
            self.layerToPng(layer,output_folder_path)
 