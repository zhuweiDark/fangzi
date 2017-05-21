#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib
import urllib2
import re
import requests
from lxml import etree
#from bs4 import BeautifulSoup
import chardet
import xlwt
#from xlwt import  *
import  sys
import  os
import  traceback
import requests
import Queue
import time
import  threading
myQueue = Queue.Queue(maxsize= 2)
reload(sys)
sys.setdefaultencoding( "utf-8" )

# 住浙网源
srcUrl = "http://www.keyhouse.cn/"
startSrcUrl = srcUrl +"search.aspx"
user_agent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/545.1 (KHTML, like Gecko) Chrome/14.0.810.0 Safari/545.1"
dstImgFilePath = "/Users/zhuwei/住浙网/"
excelFilePath = "/Users/zhuwei/zhuzhewang.xls"
excelFile = xlwt.Workbook(encoding ='utf-8')
excelSheet = excelFile.add_sheet(u"住浙网")

# 写入excel的线程
def writeToExcelData(excelDataList,indexData) :
    currentThread  = myQueue.get()
    print ('writeToExcelData thread  '+ str(indexData)  + threading.current_thread().name +"is running...")
    if excelDataList != None and isinstance(excelDataList,list) and len(excelDataList) > 0:
        tmpcolumIndex = 0
        for tmpNodeData in excelDataList :
            excelSheet.write((indexData+1),tmpcolumIndex,tmpNodeData)
            tmpcolumIndex +=1
    else:
        print("writeToExcelData srcData is wrong")
    myQueue.task_done()
    print ('writeToExcelData thread  '+ str(indexData)  + threading.current_thread().name +"is end...")

def downloadImgDataFun(imgsList,uaAgent,imgDir,indexData) :
    currentThread  = myQueue.get()
    print ('downloadImgDataFun thread  '+ str(indexData)  + threading.current_thread().name +"is running...")
    if imgsList != None and isinstance(imgsList,list) and len(imgsList) > 0:
        imgIndex = 0
        for imgUrlStr in imgsList :
            ret = getSingleImageDownload(imgUrlStr,str(imgIndex),imgDir,uaAgent)
            if ret == False :
                print("getSingleImageDownload is failed op!!!")
                continue
            imgIndex +=1

    myQueue.task_done()
    print ('downloadImgDataFun thread  '+ str(indexData)  + threading.current_thread().name +"is end...")


def getSingleImageDownload(url,imageTitle,filePathStr,user_agent):
    print(url)
    # 开始下载单个图片
    try:
        headers = { 'User-Agent' : user_agent ,
                    'Content-Encoding':'gzip, deflate, sdch',
                    'Vary':'Accept-Encoding',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection':'keep-alive'}
        resText= requests.get(url,headers = headers, timeout=40)
    except requests.exceptions.RequestException as e:
        print ("当前图片无法下载 is failed:"+ str(e))
        return  False

    fileDstPath = filePathStr +"/"+ imageTitle +".jpg"
    fp = open(fileDstPath,'wb')
    try:
        fp.write(resText.content)
    except Exception as e:
        print("e:"+ str(e))
        fp.close()
        return  False
    fp.close()
    return  True

# 封装函数
def getNodeText(tmpElement,listNode) :
    if tmpElement != None and isinstance(tmpElement,list) and len(tmpElement) >0 :
        tmpText = tmpElement[0].text
        if tmpText == None or len(tmpText) == 0 :
            tmpText = ""
        tmpText = tmpText.encode("utf-8")
        listNode.append(tmpText)
    else:
        listNode.append("")

# 获取网页数据
def pageUrlContent(srcUrl,userAgent):
    try :
        headers = { 'User-Agent' : userAgent ,
                    'Content-Encoding':'gzip, deflate, sdch',
                    'Vary':'Accept-Encoding',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection':'keep-alive'}
        response = requests.get(srcUrl,headers = headers)
        response.raise_for_status()
       # response.encoding = 'gb2312'

    except requests.RequestException as e:
        print(str(e))
        return  None
    else:
        return  response.text

# 获取所有的页数
def getAllPagesFromUrl(htmlTree) :
    allPagesUrlList = []
    pageurlList = htmlTree.xpath('//*[@id="NetPager"]/a')
    if isinstance(pageurlList,list) and len(pageurlList) > 0 :
        pagesCount = len(pageurlList)
        lastPageEle = pageurlList[pagesCount -1]
        if lastPageEle != None and lastPageEle.get("href") != None :
            lastPageConent = lastPageEle.get("href")
            lastPageConent = lastPageConent.replace("search.aspx?page=","")
            for i in range(1,int(lastPageConent)+1) :
                contentUrlStr =  startSrcUrl+"?page="+str(i)
                allPagesUrlList.append(contentUrlStr)
        else :
            print("找不到最后一页数据")
    else :
        print("解析列表失败了  failed!!!")

    return allPagesUrlList

#先获取所有需要爬的目标网页地址
def getAllDstPageUrlStr(pages):
    allDstUrls = []
    for tmpUrlStr in pages :
        #先获取页内容
        resultText = pageUrlContent(tmpUrlStr,user_agent)
        if resultText == None or len(resultText) == 0 :
            print ("resultText,startUrl is failed :" +(tmpUrlStr))
            continue
        else :
            htmlTree = etree.HTML(resultText)
            singlePagUrls = htmlTree.xpath('//*[@id="form1"]/div[7]/div[10]/table/tr[@class="pktb_1"]/td[@colspan="5"]/a[1]')
            if isinstance(singlePagUrls,list) and len(singlePagUrls) > 0 :
                for tmpCellEle  in  singlePagUrls:
                    if tmpCellEle != None :
                        cellUrlStr =  srcUrl + tmpCellEle.get("href")
                        if cellUrlStr != None and len(cellUrlStr) > 0 :
                            allDstUrls.append(cellUrlStr)

    return allDstUrls

# 提取给定url的中的有效数据(同时进行异步写入excel ,和异步下载图片)
def getCurrentPageContentData(urlStr,uaAgent,indexData) :
    print("currenturl:"+urlStr +"  indexData:"+str(indexData))

    currentContentsNode = []
    currentImgsNode = []
    tmpTitle = ""
    #开始爬网页内容
    resultText = pageUrlContent(urlStr,uaAgent)
    if resultText == None or len(resultText) == 0 :
        print ("getCurrentPageContentData is failed :" +(urlStr))
        return -1
    htmlTree = etree.HTML(resultText)

    # 先解析头部左边部分
    #标题
    headLeftEleList = htmlTree.xpath('//*[@id="lp-name"]')
    if headLeftEleList == None or isinstance(headLeftEleList,list)== False \
            or len(headLeftEleList) ==0 :
        print("contentEle is notFound!")
        return  -1

    headLeftEle = headLeftEleList[0]
    titleElement = headLeftEle.xpath('//*[@class="c-fl lp-name-tittle"]')
    getNodeText(titleElement,currentContentsNode)
    tmpTitle = currentContentsNode[0]
    # 板块
    banKuaiElement = headLeftEle.xpath('//*[@id="BanKuai"]')
    getNodeText(banKuaiElement,currentContentsNode)
    #项目地址:
    xiangmudizhiElement = headLeftEle.xpath('//*[@id="XiangmuAddress"]')
    getNodeText(xiangmudizhiElement,currentContentsNode)
    #售楼地址:
    shouloudizhiElement = headLeftEle.xpath('//*[@id="XiaoShouAddress"]')
    getNodeText(shouloudizhiElement,currentContentsNode)

    # 再解析头部右边部分
    headRightEleList = htmlTree.xpath('/html/body/div[6]/div[2]')
    if headRightEleList == None or isinstance(headRightEleList,list)== False \
            or len(headRightEleList) ==0 :
        print("headRightEle is notFound!")
        #昨日成交
        currentContentsNode.append("")
        # 今日成交
        currentContentsNode.append("")
        # 最新开盘
        currentContentsNode.append("")
        # 最新开盘套数
        currentContentsNode.append("")
        #价格
        currentContentsNode.append("")
        #楼盘热线
        currentContentsNode.append("")
    else :
       headRightEle = headRightEleList[0]
       # 昨日成交
       zuorichengjiaoElement = headRightEle.xpath('//*[@id="ChengJiao0"]')
       getNodeText(zuorichengjiaoElement,currentContentsNode)
       #今日成交
       jinrichengjiaoElement = headRightEle.xpath('//*[@id="ChengJiao1"]')
       getNodeText(jinrichengjiaoElement,currentContentsNode)
       #最新开盘
       zuixinkaipanElement = headRightEle.xpath('//*[@id="HistoryOpenDate"]')
       getNodeText(zuixinkaipanElement,currentContentsNode)
       #最新开盘套数
       zuixinkaipantaoshuElement = headRightEle.xpath('//*[@id="HistoryOpenTaoShu"]')
       getNodeText(zuixinkaipantaoshuElement,currentContentsNode)
       #价格
       jiageElement = headRightEle.xpath('//*[@id="Price01"]')
       getNodeText(jiageElement,currentContentsNode)
       #楼盘热线
       loupanElement = headRightEle.xpath('//*[@id="SellPhone"]')
       getNodeText(loupanElement,currentContentsNode)

    # 再解析正文详细资料
    contentDataElementList = htmlTree.xpath('//*[@class="Datadetails"]')
    if contentDataElementList == None or isinstance(contentDataElementList,list)== False \
            or len(contentDataElementList) ==0 :
       print("contentDataElement is failed")
       # 物业类型
       currentContentsNode.append("")
       # 拿地时间:
       currentContentsNode.append("")
       # 楼面价:
       currentContentsNode.append("")
       # 总户数:
       currentContentsNode.append("")
       # 建筑面积:
       currentContentsNode.append("")
       # 占地面积:
       currentContentsNode.append("")
       # 主力户型:
       currentContentsNode.append("")
       # 产权:
       currentContentsNode.append("")
       # 装修:
       currentContentsNode.append("")
       # 容积率:
       currentContentsNode.append("")
       # 绿化率:
       currentContentsNode.append("")
       # 车位数:
       currentContentsNode.append("")
       # 物业费:
       currentContentsNode.append("")
       # 物业公司:
       currentContentsNode.append("")
    else :
       contentDataElement = contentDataElementList[0]
       # 物业类型
       wuyeleixingElement = contentDataElement.xpath('//*[@id="WuYe02"]')
       getNodeText(wuyeleixingElement,currentContentsNode)
       # 拿地时间
       nadishijianElement = contentDataElement.xpath('//*[@id="TurnoverTime"]')
       getNodeText(nadishijianElement,currentContentsNode)
       # 楼面价:
       loumianjiaElement = contentDataElement.xpath('//*[@id="LouMianQiJia"]')
       getNodeText(loumianjiaElement,currentContentsNode)
       # 总户数:
       zonghushuElement = contentDataElement.xpath('//*[@id="ZongHuShu02"]')
       getNodeText(zonghushuElement,currentContentsNode)
       #建筑面积
       jianzhumianjiElement = contentDataElement.xpath('//*[@id="JianZhuMianji02"]')
       getNodeText(jianzhumianjiElement,currentContentsNode)
       #占地面积
       zhandimianjiElement = contentDataElement.xpath('//*[@id="ZhanDiMianJi02"]')
       getNodeText(zhandimianjiElement,currentContentsNode)
       #主力户型:
       zhulihuxingElement = contentDataElement.xpath('//*[@id="ZhuLiHuXing02"]')
       getNodeText(zhulihuxingElement,currentContentsNode)
       #产权
       chanquanElement = contentDataElement.xpath('//*[@id="Property"]')
       getNodeText(chanquanElement,currentContentsNode)
       #装修
       zhuangxiuElement = contentDataElement.xpath('//*[@id="Decoration"]')
       getNodeText(zhuangxiuElement,currentContentsNode)
       #容积率
       rongjilvElement = contentDataElement.xpath('//*[@id="RongJiLv02"]')
       getNodeText(rongjilvElement,currentContentsNode)
       #绿化率
       lvhualvElement = contentDataElement.xpath('//*[@id="LvHuaLv02"]')
       getNodeText(lvhualvElement,currentContentsNode)
       #车位数
       cheweishuElement = contentDataElement.xpath('//*[@id="CheWeiShu02"]')
       getNodeText(cheweishuElement,currentContentsNode)
       #物业费
       wuyefeiElement = contentDataElement.xpath('//*[@id="WuYeFei02"]')
       getNodeText(wuyefeiElement,currentContentsNode)
       #物业公司
       wuyegongsiElement = contentDataElement.xpath('//*[@id="WuYeGongSi02"]')
       getNodeText(wuyegongsiElement,currentContentsNode)

    #把网站地址也给写上去
    currentContentsNode.append(urlStr)

    # 解析图片list
    #首先先创建要下载图片的文件夹
    dstImgListDir = dstImgFilePath + tmpTitle +"/"
    if (os.path.exists(dstImgListDir) == False) :
        os.mkdir(dstImgListDir,)

    imgsElement = htmlTree.xpath('//*[@class="example-image"]')
    if imgsElement != None and isinstance(imgsElement,list) and len(imgsElement) >0 :
        #说明获取到了图片了.开始装载进list
        for tmpImgElement in imgsElement :
            if tmpImgElement != None and tmpImgElement.get("class") == "example-image" :
                tmpImgSrcStr = tmpImgElement.get("src")
                if tmpImgSrcStr != None and len(tmpImgSrcStr) >0 :
                    currentImgsNode.append(tmpImgSrcStr)
    else :
        print("imgsElement is not Get!!!")

    print 'current thread %s is running...' + threading.current_thread().name

    # 开始异步写入excel内容
    excelWriteThread = threading.Thread(target=writeToExcelData,name=("excelWriteThread" +str(indexData)),args=(currentContentsNode,indexData))
    excelWriteThread.setDaemon(True)
    excelWriteThread.start()
    myQueue.put(excelWriteThread)

    #  excelWriteThread.join()
#    # 开始异步下载图片了
    imgDownloadThread = threading.Thread(target=downloadImgDataFun,name=("imgDownloadThread"+str(indexData)),args=(currentImgsNode,user_agent,dstImgListDir,indexData))
    imgDownloadThread.setDaemon(True)
    imgDownloadThread.start()
    myQueue.put(imgDownloadThread)
    return  0
    # imgDownloadThread.join()
# main 处理
def main() :
    # 判断图片根路径是否存在,不存在的话创建一下
    if (os.path.exists(dstImgFilePath) == False) :
        os.mkdir(dstImgFilePath,)
    # 创建excel 并写入值

    listColums = [u"标题",u"板块",u"项目地址",u"售楼地址",u"昨日成交",u"今日成交",u"最新开盘",u"最新开盘套数",u"价格",u"楼盘热线",u"物业类型",
                  u"拿地时间",u"楼面价",u"总户数",u"建筑面积",u"占地面积",u"主力户型",u"产权",u"装修",u"容积率",u"绿化率",u"车位数",u"物业费",u"物业公司",u"网站地址"]
    tmpcolumIndex = 0
    for tmpName in listColums :
        excelSheet.write(0,tmpcolumIndex,tmpName)
        tmpcolumIndex += 1

    # 先解析源网页的数据
    resultText = pageUrlContent(startSrcUrl,user_agent)
    if resultText == None or len(resultText) == 0 :
        print ("startUrl is failed :" +(startSrcUrl))
        return -1
    htmlTree = etree.HTML(resultText)

    #解析出该网页所有的界面数组
    pagesList = getAllPagesFromUrl(htmlTree)
    if len(pagesList) == 0 :
        print("获取页数失败了!!!!")
        return  -1

    print("pagesList count is:" + str(len(pagesList)))

    #解析给出网页地址的内容地址,集合装入数组
    allPageContens = getAllDstPageUrlStr(pagesList)
    print("allPageContens count is:"+ str(len(allPageContens)))

    if allPageContens== None or len(allPageContens) == 0 :
        print("allPageContens is failed")
        return  -1
    #开始遍历解析每个网页的内容,并且提取出有效的信息
    pageIndexValue  = 0
    for currentPageUrl  in allPageContens :
         #开始提取每个有用的数据.
        ret = getCurrentPageContentData(currentPageUrl,user_agent,pageIndexValue)
        if ret == -1 :
            continue
        pageIndexValue += 1

    myQueue.join()
    excelFile.save(excelFilePath)
    print("all is Done ~~~!!")

    return  0


#主函数
if __name__ == '__main__':
    sys.exit(main())