# coding: utf-8
import re
from PIL import Image


def make_thumbnail(content="", id=0, width=300, height=200):
    content = '<p style="text-align:center"><img src="/wp-content/uploads/aaacj/2021122418ouc/25088092039.jpg" width="500" alt="江南百景图桃花村鲫鱼在哪钓"></p>';
    content = content.replace("\n", "").replace("\b", "").replace("\r", "").replace("\t", "")
    print("content:::%s" % content)
    pattern = '<img.*?src="(.*?)".*?/?>'
    res = re.search(pattern, str(content))
    try:
        img_url = res.groups()[0]
    except AttributeError:
        img_url = ""
    print("img_url res:::%s" % img_url)
    try:
        if img_url != "":
            print("============================>>>>")
            ######################################
            # 这里暂时写死，后续根据实际情况来调整   #
            ######################################
            HREF1 = "https://static.aauy.com"
            HREF2 = "http://static.aauy.com"
            HREF3 = "//static.aauy.com"
            HREF4 = "https://www.17yly.com"
            HREF5 = "http://www.17yly.com"
            HREF6 = "//www.17yly.com"
            BASE_PATH = "/www/zweb/static.aauy.com"
            THUMB_PATH = "/wp-content/uploads/thumbs"
            pic_ext_name = img_url.split(".")[-1]
            purl = THUMB_PATH + "/" + str(id) + "_thumbnail" + "." + pic_ext_name
            save_path = BASE_PATH + purl
            pic_url = HREF6 + purl
            print("save_path:::%s" % save_path)
            print("pic_url:::%s" % pic_url)
            path = img_url.replace(HREF1, BASE_PATH)
            path = path.replace(HREF2, BASE_PATH)
            path = path.replace(HREF3, BASE_PATH)
            path = path.replace(HREF4, BASE_PATH)
            path = path.replace(HREF5, BASE_PATH)
            path = path.replace(HREF6, BASE_PATH)
            # 有的没有BASE_PATH，这里加上，有的就替换掉，再加上
            path = path.replace(BASE_PATH, "")
            path = BASE_PATH + path
            print("path============================>>>>%s" % path)
            pixbuf = Image.open(path)
            pixbuf.thumbnail((width, height), Image.ANTIALIAS)
            pixbuf.save(save_path, "jpeg")
            return pic_url
        else:
            print("img_url res2:::%s" % img_url)
            return False
    except Exception as e:
        print("生成缩略图出现异常：%s" % str(e))
        return False
        
if __name__ == "__main__":
    make_thumbnail()