# coding: utf-8
import os
import shutil
from PIL import Image


# 暂只处理单层文件夹的
def forloop_file(*args):
    root_dir = args[0]
    if root_dir:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                print("===================================")
                print("make_thumbnail start::::: %s" % file)
                make_thumbnail(args, file)
                print("make_thumbnail finish:::: %s" % file)
                print("===================================")
    else:
        print("root_dir not exists")


def make_thumbnail(args, file=""):
    fullpath, thumb_dir = "", ""
    try:
        root_dir, thumb_dir, width, height = args
        if os.path.exists(thumb_dir) is False:
           os.makedirs(thumb_dir)
        save_path = thumb_dir + "/" + file
        fullpath = os.path.join(root_dir, file)
        pixbuf = Image.open(fullpath, "r")
        pixbuf.thumbnail((width, height), Image.ANTIALIAS)
        pixbuf.save(save_path)
    except Exception as e:
        print("make_thumbnail pic:::%s:::Exception:%s" % (file, str(e)))
        #将指定的文件file复制到file_dir的文件夹里面
        shutil.copy(fullpath, thumb_dir)
        
        
if __name__ == "__main__":
    root_dir, thumb_dir = "20220203ouxiniao", "20220203ouxiniao__ccc" #aaa:原图文件夹, bbb:处理后要放的文件夹
    pic_width, pic_height = 660, 440 #处理后图片最大宽高
    forloop_file(root_dir, thumb_dir, pic_width, pic_height)