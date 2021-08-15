import json
import os
import sqlite3
from enum import Enum
from typing import List
from psd_tools.api.psd_image import PSDImage

class TemplateFileEnum(Enum):
    START = "START.txt"
    END = "END.txt"
    END_WITHMACRO = "END_WITHMACRO.txt"
    MACROSTART = "MACROSTART.txt"
    MACROSTART_INPUT = "MACROSTART_INPUT.txt"
    MEDIAOUT = "MEDIAOUT.txt"
    PSD_MEDIAIN = "PSD_MEDIAIN.txt"
    PSD_MEDIAIN_DESC = "PSD_MEDIAIN_DESC.txt"
    PSD_MEDIAIN_DESC_PARTS = "PSD_MEDIAIN_DESC_PARTS.txt"
    MERGE = "MERGE.txt"
    BACKGROUND = "BACKGROUND.txt"
    BACKGROUND_NOUSERCONTROL = "BACKGROUND_NOUSERCONTROL.txt"
    MERGE_NOUSERCONTROL = "MERGE_NOUSERCONTROL.txt"
    CONTROL_INPUT = "CONTROL_INPUT.txt"


class ResolveSettingCreator:

    DB_PATH = ""
    MEDIAID_DICT = {}
    OUTPUT_FUSIONTEMPLATE_FILEPATH = "./"
    SETTING_TEMPLATE_DICT_PATH = "./setting_template/"
    FUSIONSCRIPT_DICT_PATH = "C:/Users/" + os.environ['USERNAME'] + "/AppData/Roaming/Blackmagic Design/DaVinci Resolve/Support/Fusion/Templates/Edit/Generators/"
    FILE_NAME = "None"


    def __init__(self,project_name:str,output_dir = "./",output_file_name = ""):
        self.DB_PATH = "C:/Users/" + os.environ['USERNAME'] + "/AppData/Roaming/Blackmagic Design/DaVinci Resolve/Support/Resolve Disk Database/Resolve Projects/Users/guest/Projects/" + project_name + "/Project.db"
        
        self.FILE_NAME = project_name + "_" + output_file_name
        self.OUTPUT_FUSIONTEMPLATE_FILEPATH = output_dir + "/" + self.FILE_NAME + ".setting"

    def __getMediaId(self, media_name = ""):
        try:
            if self.MEDIAID_DICT == {}:
                conn = sqlite3.connect(self.DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT Name, UniqueMediaPoolItemId FROM Sm2MPMedia WHERE DbType = 'Sm2MpVideoClip' and substr(Name, -4) = '.psd'")
                res = cur.fetchall()
                cur.close()
                conn.close()
                self.MEDIAID_DICT = res
            
            for n in self.MEDIAID_DICT:
                if n[0] == media_name:
                    return n[1]
            
            return ""
        except Exception as e:
            raise ValueError("Mediaを取得できませんでした。プロジェクト上にMiniPsdが配備されているか確認してください")

    def __createContentFromTemplate(self, template_name:TemplateFileEnum, spec_dict:dict):
        #spec_dictは{"%%name%%":"hogehoge" , "%%POS_X%%":"120"}みたいなかんじで置換するとこdictみたいな
        
        template_path = self.SETTING_TEMPLATE_DICT_PATH + template_name.value
        content = ""
        with open(template_path) as f:
            content = f.read()
        
        for k,v in spec_dict.items():
            content = content.replace(k,str(v))

        content += "\n"

        return content

    def __createMergeContent(self,name:str,front_source:str,back_source:str,pos_x:int,pos_y:int,control_name:str):
        #control_nameが無かったら勝手にExpresion使わないと判断してnousercontrol使う

        spec_dict = {
            r"%%NAME%%":name,
            r"%%INPUT_SOURCEOP_FRONT%%":front_source,
            r"%%INPUT_SOURCEOP_BACK%%":back_source,
            r"%%POS_X%%":str(pos_x),
            r"%%POS_Y%%":str(pos_y),
            r"%%CONTROL_NAME%%":control_name
        }

        if control_name != "":
            content = self.__createContentFromTemplate(TemplateFileEnum.MERGE,spec_dict)
        else :
            content = self.__createContentFromTemplate(TemplateFileEnum.MERGE_NOUSERCONTROL,spec_dict)
        return content

    def __createPsdMediainContent(self,name:str,psd_filepath:str,mediaid:str,pos_x:int,pos_y:int):
        psd = PSDImage.open(psd_filepath)

        #ここでDISC作成
        psd_images_dir = os.path.dirname(psd_filepath)[:-8] + "_Image"
        layer_images_dir = ""

        for pathname,dirname,medianame in os.walk(psd_images_dir):
            if( os.path.basename(psd_filepath)[4:-4] in dirname):
                layer_images_dir = pathname + "/" + os.path.basename(psd_filepath)[4:-4]
                break;

        desc_content = ""
        if(layer_images_dir != ""):
            for layer in psd:
                json_open = open(layer_images_dir + "/" +  layer.name[:-1]  + '.json', 'r')
                json_load = json.load(json_open)
                spec_dict = {
                    r"%%LAYER_NAME%%":layer.name[:-1],
                    r"%%X_OFFSET%%":json_load["offset_x"],
                    r"%%Y_OFFSET%%":json_load["offset_y"],
                    r"%%HEIGHT%%":json_load["size_height"],
                    r"%%WIDTH%%":json_load["size_width"]
                }
                desc_content += self.__createContentFromTemplate(TemplateFileEnum.PSD_MEDIAIN_DESC_PARTS,spec_dict)

        layer_name = ""
        spec_dict = {
            r"%%NAME%%":name,
            r"%%MEDIA_PATH%%":psd_filepath.replace("/","\\\\"),
            r"%%MEDIA_HEIGHT%%":psd.size[0],
            r"%%MEDIA_WIDTH%%":psd.size[1],
            r"%%MEDIA_NAME%%":os.path.basename(psd_filepath),
            r"%%MEDIA_NUM_LAYERS%%":str(len(list(psd.descendants())) + 1),
            r"%%MEDIA_DESCS%%":desc_content,
            r"%%LAYER_NAME%%":str(layer_name),
            r"%%MediaID%%":mediaid,
            r"%%POS_X%%":str(pos_x),
            r"%%POS_Y%%":str(pos_y)
        }  
        content = self.__createContentFromTemplate(TemplateFileEnum.PSD_MEDIAIN_DESC,spec_dict)
        return content

    def __createMacroInput(self,psd_files:List):
        input_content = ""
        for index,psd_file in enumerate(psd_files):
            #MediaInのLayer変更用
            input_spac_dict_mediain = {
                r"%%NAME%%" : "Input" + str(index)  + "_MediaIn",
                r"%%SOURCEOP_NAME%%" : "MediaIn" + str(index),
                r"%%SOURCE_NAME%%" : "Layer",
                r"%%PARAM_NAME%%" : psd_file[4:-4] + "_Layer",
                r"%%ADDITIONAL%%" : ""
            }
            input_content += self.__createContentFromTemplate(TemplateFileEnum.MACROSTART_INPUT,input_spac_dict_mediain)
            input_spac_dict_merge = {
                r"%%NAME%%" : "Input" + str(index) + "_Merge",
                r"%%SOURCEOP_NAME%%" : "background0",
                r"%%SOURCE_NAME%%" : "BLEND_CONTROL" + str(index),
                r"%%PARAM_NAME%%" : "Visible",
                r"%%ADDITIONAL%%" : "Default = 0,"
            }
            input_content += self.__createContentFromTemplate(TemplateFileEnum.MACROSTART_INPUT,input_spac_dict_merge)
            

        macrostart_spec_dict = {
            r"%%NAME%%":"psdtool",
            r"%%MACROSTART_INPUT_CONTENT%%":input_content,
        }

        return self.__createContentFromTemplate(TemplateFileEnum.MACROSTART,macrostart_spec_dict)

    def createSetting(self,minipsd_dict:str):

        try:

            self.__getMediaId()
            files = os.listdir(minipsd_dict)

            psd_files = sorted([f for f in files if f[-4:] == ".psd"])
            #setting_contentが普通に出力されるやつ、macro_contentが良い感じにEditページで作られる奴
            macro_content = ""
            setting_content = ""
            macro_content += self.__createContentFromTemplate(TemplateFileEnum.START,{})
            setting_content += self.__createContentFromTemplate(TemplateFileEnum.START,{})
            macro_content += self.__createMacroInput(psd_files)
            #xは110単位、yは33単位がちょうどいいらしい
            BASE_POS_X = 110
            BASE_POS_Y = 33
            BASE_MEDIAIN_NAME = "MediaIn"
            BASE_MERGE_NAME = "Merge"

            #バックグラウンド置く
            usercontrol_content = ""
            for index, psd_file in enumerate(psd_files):
                usercontrol_content += self.__createContentFromTemplate(TemplateFileEnum.CONTROL_INPUT,{r"%%NAME%%": "BLEND_CONTROL" + str(index)})

            background_size = PSDImage.open(minipsd_dict + psd_files[0]).size
            background_spec_dict = {
                r"%%NAME%%":"background0",
                r"%%MEDIA_WIDTH%%":background_size[0],
                r"%%MEDIA_HEIGHT%%":background_size[1],
                r"%%POS_X%%":str(BASE_POS_X * 1),
                r"%%POS_Y%%":str(BASE_POS_Y * -1),
                r"%%CONTROL_INPUT_CONTENT%%":usercontrol_content
            }
            macro_content += self.__createContentFromTemplate(TemplateFileEnum.BACKGROUND,background_spec_dict)
            setting_content += self.__createContentFromTemplate(TemplateFileEnum.BACKGROUND_NOUSERCONTROL,background_spec_dict)
            next_sourceback = "background0"

            #MediainとMergeをつくる
            for index, psd_file in enumerate(psd_files):

                mediain_name = BASE_MEDIAIN_NAME + str(index)
                media_path = minipsd_dict + psd_file
                media_id = self.__getMediaId(psd_file)
                media_pos_x = BASE_POS_X * 0
                media_pos_y = BASE_POS_Y * index

                macro_content += self.__createPsdMediainContent(
                    name=mediain_name,psd_filepath=media_path,mediaid=media_id,pos_x=media_pos_x,pos_y=media_pos_y)
                setting_content += self.__createPsdMediainContent(
                    name=mediain_name,psd_filepath=media_path,mediaid=media_id,pos_x=media_pos_x,pos_y=media_pos_y)

                merge_name = BASE_MERGE_NAME + str(index)
                front_source = BASE_MEDIAIN_NAME + str(index)
                back_source = next_sourceback
                merge_pos_x = BASE_POS_X * 1
                merge_pos_y = BASE_POS_Y * index

                macro_content += self.__createMergeContent(
                    name=merge_name,front_source=front_source,back_source=back_source,pos_x=merge_pos_x,pos_y=merge_pos_y,control_name="BLEND_CONTROL" + str(index))
                setting_content += self.__createMergeContent(
                    name=merge_name,front_source=front_source,back_source=back_source,pos_x=merge_pos_x,pos_y=merge_pos_y,control_name="")
                
                next_sourceback = merge_name

            macro_content += self.__createContentFromTemplate(TemplateFileEnum.MEDIAOUT,
                {r"%%INPUT_SOURCEOP%%":next_sourceback,r"%%POS_X%%":str(BASE_POS_X * 2),r"%%POS_Y%%":str(BASE_POS_Y)})
            setting_content += self.__createContentFromTemplate(TemplateFileEnum.MEDIAOUT,
                {r"%%INPUT_SOURCEOP%%":next_sourceback,r"%%POS_X%%":str(BASE_POS_X * 2),r"%%POS_Y%%":str(BASE_POS_Y)})
            macro_content += self.__createContentFromTemplate(TemplateFileEnum.END_WITHMACRO,{r"%%ActiveTool%%":"psdtool"})
            setting_content += self.__createContentFromTemplate(TemplateFileEnum.END,{r"%%ActiveTool%%":"psdtool"})

            with open(self.FUSIONSCRIPT_DICT_PATH + self.FILE_NAME + "[psdtool].setting", mode='w',newline="\n",encoding="UTF8") as f:
                f.write(macro_content)
            with open(self.OUTPUT_FUSIONTEMPLATE_FILEPATH, mode='w',newline="\n",encoding="UTF8") as f:
                f.write(setting_content)


        except FileNotFoundError as e:
            print(e)
            raise ValueError("MiniPSDを取得できませんでした。MiniPSD_dirを確認してください")
        except ValueError as e:
            raise e
        except Exception as e:
            print(e)
            raise ValueError("なんかがバグってます。製作者に連絡頂けるとありがたいです")
    
