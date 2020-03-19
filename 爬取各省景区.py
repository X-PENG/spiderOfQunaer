#爬取热门景区
import requests
import json
import time
import os


#生成器函数
def generateUrl(url):
    for j in range(17,len(province_list)):
        keyword = province_list[j]
        global filePath
        #每个省份一个文件
        filePath=basePath+keyword+".csv"
        init()
        #重新开始一个省时，清空id_set
        global id_set
        id_set=set()
        global repeat_count
        #输出上一个省去重的次数
        print(province_list[j-1]+"，去重--->"+str(repeat_count)+"次")
        #重置repeat_count
        repeat_count=0
        for i in range(start,end+1):
            page=i
            yield url+'?keyword='+str(keyword)+'&page='+str(page)

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
    #景区集合
    sight_list = data_dict['data']['sightList']
    results=[]
    for i in range(0,len(sight_list)):
        sight=sight_list[i]
        #如果景区id已存在
        if sight['sightId'] in id_set:
            global repeat_count
            repeat_count=repeat_count+1
            continue
        id_set.add(sight['sightId'])
        one_line_data = []
        districts = sight['districts']
        for j in range(0,len(attr_list)):
            if attr_list[j]=='star':
                one_line_data.append(sight.get(attr_list[j],' '))
            elif attr_list[j]=='qunarPrice':
                one_line_data.append(sight.get(attr_list[j], '0'))
            elif attr_list[j]=='province':
                one_line_data.append(districts.split('·')[0])
            elif attr_list[j]=='city':
                one_line_data.append(districts.split('·')[1])
            elif attr_list[j]=='intro':
                intro=sight.get(attr_list[j], ' ')
                intro = intro.replace(',', '，')
                intro = intro.replace('\n', '')
                one_line_data.append(intro)
            else:
                one_line_data.append(str(sight.get(attr_list[j],' ')).replace(',','，'))
        results.append(one_line_data)
    return results


def writeDataToFile(list):
    with open(filePath,'a+',encoding="utf-8-sig") as file:
        for i in range(0,len(list)):
            one_line=list[i]
            file.write(",".join(one_line) + '\n')

def main():
    successCount=0
    for url in generateUrl(url_interface):
        jsonText=getJsonText(url)
        if jsonText=='':
            print(url+'--->返回空jsonText')
            time.sleep(10)
            continue
        results=processDataAndRetrunList(jsonText)
        writeDataToFile(results)
        successCount = successCount + 1
        print(successCount)
        time.sleep(10)
    # 输出最后一个省去重的次数
    print(province_list[len(province_list)-1] + "，去重--->" +str(repeat_count)+"次")



#初始化文件
def init():
    if os.path.exists(filePath)==False:
        file = open(filePath, 'w',encoding='utf-8-sig')
        file.write(",".join(attr_list)+'\n')
        file.close()

#存储景区id，集合可去重
id_set=set()
start,end=1,15
attr_list=['sightId','sightName','intro','address','star','qunarPrice','saleCount','point','sightImgURL','province','city']
basePath='D:/桌面文件站/实训课/数据爬取集合/'
filePath=''
repeat_count=0
#idFilePath='D:/桌面文件站/实训课/数据爬取集合/sights_id.csv'

url_interface='https://piao.qunar.com/ticket/list.json'
province_list=['北京市','天津市','上海市','重庆市','河北省','山西省','辽宁省','吉林省','黑龙江省','江苏省','浙江省','安徽省',
               '福建省','江西省','山东省','河南省','湖北省','湖南省','广东省','海南省','四川省','贵州省','云南省','陕西省',
               '甘肃省','青海省','台湾省','内蒙古','广西','西藏','宁夏','新疆','香港','澳门']

if __name__=="__main__":
    main()
