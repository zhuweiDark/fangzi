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
myQueue = Queue.Queue(maxsize= 3)
reload(sys)
sys.setdefaultencoding( "utf-8" )



# 住浙网源
srcUrl = "http://www.house178.com"
startSrcUrl = srcUrl +"/loupan/"

user_agent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/545.1 (KHTML, like Gecko) Chrome/14.0.810.0 Safari/545.1"
dstImgFilePath = "/Users/zhuwei/钱江/"
excelFilePath = "/Users/zhuwei/qianjiang.xls"
excelFile = xlwt.Workbook(encoding ='utf-8')
excelSheet = excelFile.add_sheet(u"钱江")
totoalPageNum = 38


# 写入excel的线程
def writeToPreExcelData(allPageContens,indexData) :
    currentThread  = myQueue.get()
    print ('writeToPreExcelData thread  '+ str(indexData)  + threading.current_thread().name +"is running...")
    #开始遍历解析每个网页的内容,并且提取出有效的信息
    pageIndexValue  = 0
    for currentPageUrl  in allPageContens :
        #开始提取每个有用的数据.
        ret = getCurrentPageContentData(currentPageUrl,user_agent,pageIndexValue)
        if ret == -1 :
            continue
        pageIndexValue += 1

    myQueue.task_done()
    print ('writeToPreExcelData thread  '+ str(indexData)  + threading.current_thread().name +"is end...")

# 写入剩下excel的线程
def writeToSecPreExcelData(allPageContens,indexData) :
    currentThread  = myQueue.get()
    print ('writeToSecPreExcelData thread  '+ str(indexData)  + threading.current_thread().name +"is running...")
    #开始遍历解析每个网页的内容,并且提取出有效的信息
    pageIndexValue  = 0
    for currentPageUrl  in allPageContens :
        #开始提取每个有用的数据.
        tmpPageUrl = (currentPageUrl +"/canshu/")
        ret = getCurrentDetailPageContentData(tmpPageUrl,currentPageUrl,user_agent,pageIndexValue)
        if ret == -1 :
            continue
        pageIndexValue += 1

    myQueue.task_done()
    print ('writeToSecPreExcelData thread  '+ str(indexData)  + threading.current_thread().name +"is end...")


# 下载图片线程
def writeToThirdPreExcelData(allPageContens,indexData) :
    currentThread  = myQueue.get()
    print ('writeToThirdPreExcelData thread  '+ str(indexData)  + threading.current_thread().name +"is running...")
    # #开始遍历解析每个网页的内容,并且提取出有效的信息
    # pageIndexValue  = 0
    # for currentPageUrl  in allPageContens :
    #     #开始提取每个有用的数据.
    #     ret = getCurrentPageContentData(currentPageUrl,user_agent,pageIndexValue)
    #     if ret == -1 :
    #         continue
    #     pageIndexValue += 1

    myQueue.task_done()
    print ('writeToThirdPreExcelData thread  '+ str(indexData)  + threading.current_thread().name +"is end...")


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
            singlePagUrls = htmlTree.xpath('//div[@class="col-md-5 col-sm-5 col-IE-5 house-info"]/div[@class="oneline"]/a')
            if isinstance(singlePagUrls,list) and len(singlePagUrls) > 0 :
                for tmpCellEle  in  singlePagUrls:
                    if tmpCellEle != None :
                        cellUrlStr =  srcUrl + tmpCellEle.get("href")
                        if cellUrlStr != None and len(cellUrlStr) > 0 :
                            allDstUrls.append(cellUrlStr)

    return allDstUrls

# 获取所有的页数
def getAllPagesFromUrl(htmlTree) :
    allPagesUrlList = []
    # 钱江网站先简单写死总页数,先不忙搞实时获取总页数了.!!
    for i in range(1,(totoalPageNum)+1) :
        contentUrlStr =  startSrcUrl+"c"+str(i)
        allPagesUrlList.append(contentUrlStr)

    return allPagesUrlList


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


# 封装函数
def getNodeNextText(tmpElement,listNode) :
    if tmpElement != None and isinstance(tmpElement,list) and len(tmpElement) >0 :
        tmpText = tmpElement[0].tail
        if tmpText == None or len(tmpText) == 0 :
            tmpText = ""
        tmpText = tmpText.encode("utf-8")
        listNode.append(tmpText)
    else:
        listNode.append("")

# 封装nodeElement获取文本函数
def getNodeElementText(tmpElement,listNode) :
    if tmpElement != None :
        tmpText = tmpElement.text
        if tmpText == None or len(tmpText) == 0 :
            tmpText = ""
        tmpText = tmpText.encode("utf-8")
        listNode.append(tmpText)
    else:
        listNode.append("")
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

# 提取给定url 中的详情页有效数据(同时进行写入excel)
def getCurrentDetailPageContentData(urlStr,originPageUrl,uaAgent,indexData):
    print("getCurrentDetailPageContentData:"+urlStr +"  indexData:"+str(indexData))
    currentContentsNode = []
    #开始爬网页内容
    resultText = pageUrlContent(urlStr,uaAgent)
    if resultText == None or len(resultText) == 0 :
        print ("getCurrentPageContentData is failed :" +(urlStr))
        return -1
    htmlTree = etree.HTML(resultText)
    headEleList = htmlTree.xpath('/html/body/div[7]/div/div[1]')
    if headEleList == None or isinstance(headEleList,list)== False \
            or len(headEleList) ==0 :
        print("headEleList is notFound!")
        return  -1
    headElement = headEleList[0]
    allHeadEleList =  headElement.xpath('.//*[@class="col-sm-6 col-xs-6 col-md-6 col-IE-6"]/table[@id="housedetailTable"]/tr/td[@class="t-t"]')
    if allHeadEleList == None or isinstance(allHeadEleList,list)== False \
            or len(allHeadEleList) ==0 :
        print("allHeadEleList is notFound!")
        return  -1
    for tmpElement in  allHeadEleList:
        getNodeElementText(tmpElement,currentContentsNode)

    bottomElent  = headEleList[0]
    allBottomList = bottomElent.xpath('.//*[@id="peitaodetailTable"]/tr')
    if allBottomList == None or isinstance(allBottomList,list)== False \
            or len(allBottomList) ==0 :
        print("allHeadEleList is notFound!")
        return  -1
    #先忽略内部配套信息
    for i in range(0,7):
        hasCurrent = False
        for tmpElement in allBottomList :
            tmpSubElementList = tmpElement.xpath('.//td[@class="t-h"]')
            if tmpSubElementList == None or isinstance(tmpSubElementList,list)== False \
                or len(tmpSubElementList) ==0 :
                continue
            tmpStr = tmpSubElementList[0].text
            tmpStr = tmpStr.replace("  ","")
            if tmpStr !=None and len(tmpStr) > 0 :
                if i == 0 and  tmpStr.find(u"车位数") >=0 :
                    tmpSubValueElementList = tmpElement.xpath('.//td[@class="t-t"]')
                    if tmpSubValueElementList == None or isinstance(tmpSubValueElementList,list)== False \
                        or len(tmpSubValueElementList) ==0 :
                        continue
                    tmpsubValueElement = tmpSubValueElementList[0]
                    getNodeElementText(tmpsubValueElement,currentContentsNode)
                    hasCurrent = True
                    break
                elif i == 1 and tmpStr.find(u"周边商业") >= 0 :
                    tmpSubValueElementList = tmpElement.xpath('.//td[@class="t-t"]')
                    if tmpSubValueElementList == None or isinstance(tmpSubValueElementList,list)== False \
                            or len(tmpSubValueElementList) ==0 :
                        continue
                    tmpsubValueElement = tmpSubValueElementList[0]
                    getNodeElementText(tmpsubValueElement,currentContentsNode)
                    hasCurrent = True
                    break
                elif i == 2 and tmpStr.find(u"周边景观") >= 0 :
                    tmpSubValueElementList = tmpElement.xpath('.//td[@class="t-t"]')
                    if tmpSubValueElementList == None or isinstance(tmpSubValueElementList,list)== False \
                            or len(tmpSubValueElementList) ==0 :
                        continue
                    tmpsubValueElement = tmpSubValueElementList[0]
                    getNodeElementText(tmpsubValueElement,currentContentsNode)
                    hasCurrent = True
                    break
                elif i == 3  and tmpStr.find(u"周边公园") >= 0 :
                    tmpSubValueElementList = tmpElement.xpath('.//td[@class="t-t"]')
                    if tmpSubValueElementList == None or isinstance(tmpSubValueElementList,list)== False \
                            or len(tmpSubValueElementList) ==0 :
                        continue
                    tmpsubValueElement = tmpSubValueElementList[0]
                    getNodeElementText(tmpsubValueElement,currentContentsNode)
                    hasCurrent = True
                    break
                elif i== 4 and tmpStr.find(u"周边医院") >= 0 :
                    tmpSubValueElementList = tmpElement.xpath('.//td[@class="t-t"]')
                    if tmpSubValueElementList == None or isinstance(tmpSubValueElementList,list)== False \
                            or len(tmpSubValueElementList) ==0 :
                        continue
                    tmpsubValueElement = tmpSubValueElementList[0]
                    getNodeElementText(tmpsubValueElement,currentContentsNode)
                    hasCurrent = True
                    break
                elif i == 5 and tmpStr.find(u"周边学校") >= 0 :
                    tmpSubValueElementList = tmpElement.xpath('.//td[@class="t-t"]')
                    if tmpSubValueElementList == None or isinstance(tmpSubValueElementList,list)== False \
                            or len(tmpSubValueElementList) ==0 :
                        continue
                    tmpsubValueElement = tmpSubValueElementList[0]
                    getNodeElementText(tmpsubValueElement,currentContentsNode)
                    hasCurrent = True
                    break
                elif i == 6 and tmpStr.find(u"周边交通") >= 0 :
                    tmpSubValueElementList = tmpElement.xpath('.//td[@class="t-t"]')
                    if tmpSubValueElementList == None or isinstance(tmpSubValueElementList,list)== False \
                            or len(tmpSubValueElementList) ==0 :
                        continue
                    tmpsubValueElement = tmpSubValueElementList[0]
                    getNodeElementText(tmpsubValueElement,currentContentsNode)
                    hasCurrent = True
                    break
            else:
                continue
        if hasCurrent == False :
            currentContentsNode.append(u"".encode("utf-8"))

    currentContentsNode.append(originPageUrl)
    #先写入excel
    if currentContentsNode != None and isinstance(currentContentsNode,list) and len(currentContentsNode) > 0:
        tmpcolumIndex = 5
        for tmpNodeData in currentContentsNode :
            excelSheet.write((indexData+1),tmpcolumIndex,tmpNodeData)
            tmpcolumIndex +=1

    return  0

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
    headLeftEleList = htmlTree.xpath('/html/body/div[@class="container b-name-area"]/div[@class="row"]')
    if headLeftEleList == None or isinstance(headLeftEleList,list)== False \
            or len(headLeftEleList) ==0 :
        print("contentEle is notFound!")
        return  -1

    headLeftEle = headLeftEleList[0]
    titleElement = headLeftEle.xpath('.//*[@class="building-name"]')
    getNodeText(titleElement,currentContentsNode)
    tmpTitle = currentContentsNode[0]

    #销售状态
    saleStatusElement =  headLeftEle.xpath('.//*[@class="house-status"]/span[@class="label label-success"]/em[@class="icon-list"]')
    getNodeNextText(saleStatusElement,currentContentsNode)
    tmpSaleStatus = currentContentsNode[1]

    #标签类元素
    headBottomEle = htmlTree.xpath('/html/body/div[@class="container b-tag-area clearfix"]/div[@class="row"]/span[@class="b-tag"]')
    if headBottomEle == None or isinstance(headBottomEle,list)== False \
            or len(headBottomEle) ==0 :
        print("headBottomEle is notFound!")
        return  -1
    tmpTitleTag = ""
    for i in range(0,len(headBottomEle)):
        tmpText = headBottomEle[i].text
        if tmpText == None or len(tmpText) == 0 :
            tmpText = ""
        if i +1 != len(headBottomEle)  :
          tmpTitleTag += (tmpText.encode('utf-8') + "|")
        else:
          tmpTitleTag += tmpText.encode('utf-8')

    if len(tmpTitleTag) >0 :
        currentContentsNode.append(tmpTitleTag)

    #正文body element
    bodyContentEle = htmlTree.xpath('/html/body/div[7]/div/div[2]')
    if bodyContentEle == None or isinstance(bodyContentEle,list)== False \
            or len(bodyContentEle) ==0 :
        print("bodyContentEle is notFound!")
        return  -1

    #价格
    tmpBodyContentEle = bodyContentEle[0]
    priceElement =  tmpBodyContentEle.xpath('.//*[@class="col-sm-7 col-xs-12 col-IE-7"]/span[@class="text-red price"]')
    if priceElement == None or isinstance(priceElement,list)== False \
            or len(priceElement) ==0 :
        print("bodyContentEle is notFound!")
        return  -1
    priceText =  priceElement[0].text.encode("utf-8")
    if priceElement[0].tail != None and len(priceElement[0].tail) > 0 :
        priceText += ( priceElement[0].tail.encode("utf-8"))
    currentContentsNode.append(priceText)

    #销售电话
    salePhoneNumEle = tmpBodyContentEle.xpath('.//*[@class="row info-line z1"]/div[@class="col-sm-10 col-xs-12 col-IE-12"]/span[@class="text-red Hotline"]')
    if salePhoneNumEle == None or isinstance(salePhoneNumEle,list)== False \
            or len(salePhoneNumEle) ==0 :
        print("bodyContentEle is notFound!")
        return  -1
    salePhoneText = ""
    for i in range(0,len(salePhoneNumEle)):
        tmpText = salePhoneNumEle[i].text
        if tmpText == None or len(tmpText) == 0 :
          tmpText = ""
        if i +1 != len(headBottomEle)  :
            salePhoneText += (tmpText.encode('utf-8') + "-")
        else:
            salePhoneText += tmpText.encode('utf-8')

    currentContentsNode.append(salePhoneText)

    #先写入excel
    if currentContentsNode != None and isinstance(currentContentsNode,list) and len(currentContentsNode) > 0:
        tmpcolumIndex = 0
        for tmpNodeData in currentContentsNode :
            excelSheet.write((indexData+1),tmpcolumIndex,tmpNodeData)
            tmpcolumIndex +=1
    return  0



# main 处理
def main() :
    # 判断图片根路径是否存在,不存在的话创建一下
    if (os.path.exists(dstImgFilePath) == False) :
        os.mkdir(dstImgFilePath,)
    # 创建excel 并写入值

    listColums = [u"标题",u"销售状态",u"标签",u"价格",u"销售电话",u"楼盘位置",u"建筑面积",u"户型面积",
                  u"入住时间",u"产权",u"容积率",u"绿化率",u"占地面积",u"售楼地址",u"物业类型",u"开盘时间",u"建筑类别",u"装修情况",u"户数",u"开发商",u"物业公司",u"车位数",u"周边商业",u"周边景观",u"周边公园",u"周边医院",u"周边学校",u"周边交通",u"网站地址"]
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

    #开子线程来下
    excelWriteThread = threading.Thread(target=writeToPreExcelData,name=("excelWriteThread" +str("0")),args=(allPageContens,"0"))
    excelWriteThread.setDaemon(True)
    excelWriteThread.start()
    myQueue.put(excelWriteThread)


    #开第二个子线程来下
    excelSecWriteThread = threading.Thread(target=writeToSecPreExcelData,name=("excelSecWriteThread" +str("1")),args=(allPageContens,"1"))
    excelSecWriteThread.setDaemon(True)
    excelSecWriteThread.start()
    myQueue.put(excelSecWriteThread)


    #开第三个子线程来下图
    excelThirdWriteThread = threading.Thread(target=writeToThirdPreExcelData,name=("writeToThirdPreExcelData" +str("2")),args=(allPageContens,"2"))
    excelThirdWriteThread.setDaemon(True)
    excelThirdWriteThread.start()
    myQueue.put(excelThirdWriteThread)

    myQueue.join()
    excelFile.save(excelFilePath)
    print("all is Done ~~~!!")

    return  0

#主函数
if __name__ == '__main__':
    sys.exit(main())