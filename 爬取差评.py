#爬取热门景区
import requests
import json
import time
import os
import re
import jieba
import jieba.posseg as pseg

#生成器函数
def generateUrl(url):
    for j in range(21,len(province_list)):
        keyword = province_list[j]
        currentProvinceSightIds=readEveryProvinceFile(province_file_path+keyword+'.csv')
        if currentProvinceSightIds=='error':
            #读取下一个文件
            continue
        global filePath
        #每个省份一个文件
        filePath=basePath+baseName+keyword+".csv"
        #创建并初始化文件
        init()
        for i in range(0,len(currentProvinceSightIds)):
            global current_sight_id
            current_sight_id=currentProvinceSightIds[i]
            yield url+current_sight_id

#是否重复请求
def isRepeat(jsonText):
    data_dict = json.loads(jsonText)
    #commentList
    comment_list = data_dict['data'].get('commentList','')
    #tagList
    tag_list = data_dict['data'].get('tagList','')
    #一般不存在没有tagList属性
    if comment_list==[] or tag_list==[]:
        print("reason-->"+"len(comment_list)="+str(len(comment_list))+",len(tag_list)="+str(len(tag_list)))
        return True
    elif tag_list=='':
        print("reason-->" + "未得到tagList字段")
        return True
    elif comment_list=='':
        result = processTagList(tag_list, '0')
        #没commentList字段，但是有差评
        if result[2] != '0':
            print("reason-->" + "未得到comment_list字段，但是有差评")
            return True
    else:#tag_list有内容且（comment_list有内容 或者 没有commentList属性且的确差评为0）
        return False


def getJsonText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        return ''

def processDataAndRetrunList(jsonText):
    data_dict = json.loads(jsonText)
    #commentList
    comment_list = data_dict['data'].get('commentList','')
    results=[]
    #没有评论
    if comment_list=='':
        results.append([current_sight_id,' ',' ','3'])
        return results
    txt=''
    for i in range(0,len(comment_list)):
        content=comment_list[i].get('content','')
        if content!='':
            #排除特殊字符
            content=regex.sub('',content)
        # if content=='用户未点评系统默认好评':
        #     txt=txt+''
        #     continue
        txt=txt+content+' '
    #处理txt
    allwords_n_or_a=cutTxtNeed_n_a(txt)
    txt_n = ' '.join(allwords_n_or_a[0])
    txt_a = ' '.join(allwords_n_or_a[1])
    results.append([current_sight_id,txt_n,txt_a,'3'])
    return results

#对一个文本进行分词：分别取名词和形容词
def cutTxtNeed_n_a(txt):
    #所有名词
    allwords_n = []
    #所有形容词
    allwords_a = []
    words=pseg.cut(txt)
    for w,f in words:
        if f.startswith('n'):     #是名词
            allwords_n.append(w)
        elif f.startswith('a'):   #是形容词
            allwords_a.append(w)
    return [allwords_n,allwords_a]

# #对一个文本进行分词：取形容词
# def cutTxtNeed_a(txt):
#     allwords=[]
#     words=pseg.cut(txt)
#     for w,f in words:
#         if f.startswith('a'):     #是形容词
#             allwords.append(w)
#     return allwords
#
# #对一个文本进行分词：取名词
# def cutTxtNeed_n(txt):
#     allwords=[]
#     words=pseg.cut(txt)
#     for w,f in words:
#         if f.startswith('n'):     #是名词
#             allwords.append(w)
#     return allwords

def processTagList(tagList,comment_sum_count):
    good_count=0
    bad_count=0
    for tag in tagList[0:]:
        tagType=tag.get('tagType',-1)
        if tagType==1:
            good_count=tag['tagNum']
        if tagType==3:
            bad_count=tag['tagNum']
    return [current_sight_id,str(good_count),str(bad_count),comment_sum_count]

#向评论文件写数据
def writeDataToFile(list):
    with open(filePath,'a+',encoding="utf-8-sig") as file:
        file.write(",".join(list) + '\n')

# #向评论数文件写数据
# def writeCommentCountToFile(list):
#     with open(comment_count_file_path,'a+') as file:
#         file.write(",".join(list) + '\n')

#读取每个省文件，返回该省所以景区id
def readEveryProvinceFile(provinceFile):
    data_list = []
    try:
        with open(provinceFile, encoding='utf-8') as file:
            data_list = file.readlines()
    except FileNotFoundError:
        print(provinceFile+'-->文件不存在')
        return 'error'
    sightIds = []
    for item in data_list[1:]:
        # 空行
        if item == '\n':
            continue
        sightIds.append(item.split(',', 1)[0])
    return  sightIds

#初始化文件
def init():
    if os.path.exists(filePath)==False:
        file = open(filePath, 'w',encoding='utf-8-sig')
        file.write(",".join(attr_list)+'\n')
        file.close()

#初始化目录
def initDirectory():
    if os.path.exists(basePath)==False:
        os.mkdir(basePath)

def main():
    successCount=0
    for url in generateUrl(url_interface):
        jsonText=getJsonText(url)
        if jsonText=='':#第一次为空，重复请求一下
            time.sleep(10)
            jsonText = getJsonText(url)
            print(url + '--->返回空jsonText，重复请求一次')
        if jsonText=='':#还是空
            print(url+'--->《还》返回空jsonText，不再重复请求')
            time.sleep(10)
            continue
        if isRepeat(jsonText):
            time.sleep(10)
            jsonText = getJsonText(url)
            print(url+'--> repeat request')
        results=processDataAndRetrunList(jsonText)
        writeDataToFile(results[0])
        successCount = successCount + 1
        print(successCount)
        time.sleep(10)

#评论文件的头部
attr_list=['sightId','content_n','content_a','tagType']
basePath='./badComment'
baseName='/badComment_'
filePath=''
#之前爬取的所有省份景区信息csv文件存放目录
province_file_path='D:/桌面文件站/实训课/数据爬取集合/'
#当前景区id
current_sight_id=0
#排除特殊字符
regex=re.compile(r'[\'\"，\|。？?、！‘’“”：；\\~@#￥$（）*+-/=%!^&(),.;:\n<>]')

url_interface='https://piao.qunar.com/ticket/detailLight/sightCommentList.json?index=1&page=1&pageSize=500&tagType=3&sightId='
province_list=['北京市','天津市','上海市','重庆市','河北省','山西省','辽宁省','吉林省','黑龙江省','江苏省','浙江省','安徽省',
               '福建省','江西省','山东省','河南省','湖北省','湖南省','广东省','海南省','四川省','贵州省','云南省','陕西省',
               '甘肃省','青海省','台湾省','内蒙古','广西','西藏','宁夏','新疆','香港','澳门']

if __name__=="__main__":
    initDirectory()
    main()

