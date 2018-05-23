'''
@author: xusheng
'''

import os
import numpy as np
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image

if __name__ == '__main__':
    txt = '2017年6月15日由上海市商务委上海市长宁区政府指导上海市长宁区青年联合会和亿欧联合主办的2017中国互联网新商业峰会在上海绿地会议中心拉开帷幕本次峰会以品质生活服务升级为主题上海市商务委上海市长宁区政府领导中国生活性服务领域的商业领袖投资大佬等齐聚一堂论道长宁共同探讨消费升级形势下生活性服务领域的创新创业之道车享CEO兼车享家CEO夏军发表了车享家的新商业之道的主题演讲夏军认为车享家是一个另类它既不是一个纯粹的互联网企业也不是一个传统企业在过去3-5年里从我个人和企业来讲都在做一件事情怎么样去互联网化把线上线下融为一体无论是互联网还是互联网最终都会回归商业的本质'

    jieba.load_userdict('jieba_user_dict.txt')
    wordlist_jieba = jieba.cut(txt, cut_all=False)
    wordlist_space_split = " ".join(wordlist_jieba)

    # font: ms yahei
    font_path = os.path.join('C:\\', 'Windows', 'Fonts', 'msyh.ttf')
     
    mask_images = np.array(Image.open(os.path.join('mask_wechat.jpg')))
    wc = WordCloud(background_color="white", max_words=2000, mask=mask_images, max_font_size=32, random_state=40, font_path=font_path)
    wc.generate(wordlist_space_split)
    wc.to_file('word_cloud.jpg')

    image_colors = ImageColorGenerator(mask_images)
    plt.imshow(wc.recolor(color_func=image_colors))
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
