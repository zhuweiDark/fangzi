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
reload(sys)
sys.setdefaultencoding( "utf-8" )

import requests

imageDir = "/Users/zhuwei/房天下/"
#filepath = '/Users/zhuwei/Documents/testpachong/text.txt'
excelFilePath = "/Users/zhuwei/fangtianxia.xls"

#url = "http://www.baidu.com"

excelFile = xlwt.Workbook(encoding ='utf-8')
excelSheet = excelFile.add_sheet(u"房天下")

def getRequestUrlText(url,user_agent):
    try :
        headers = { 'User-Agent' : user_agent ,
                    'Content-Encoding':'gzip, deflate, sdch',
                    'Vary':'Accept-Encoding',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection':'keep-alive'}
        response = requests.get(url,headers = headers)
        response.raise_for_status()
        response.encoding = 'gb2312'

    except requests.RequestException as e:
        print( str(e))
        return  None
    else:
        return  response.text

# 爬单个网页的内容
def getSinglePageContent(headerElement,allRowDataLists,titleStr,nowFenStr,cityStr,addressStr,urlStr):

    title = ""
    nowfenData = ""
    totalfen = ""
    zixundianhua  = ""
    junjia = ""
    xiangmudizhi = ""
    zhulihuxing = ""
    jinqikaipan = ""
    tmpHeaderElement  = headerElement[0]
    #名称
    if titleStr == None :
        titleElement = tmpHeaderElement.find("./div/div/h1/strong")
        if len(titleElement.text) >0 :
             title = titleElement.text.encode('utf-8')
        else :
             print("title is not get !!!")
    else:
        title = titleStr.encode('utf-8')
    nowFenElement = None
    if nowFenStr == None :
        # 当前评分
        nowFenElement =   tmpHeaderElement.find("./div/div/a")
        if nowFenElement.get('target') == '_blank' :
             if nowFenElement != None and nowFenElement.text != None and len(nowFenElement.text) > 0 :
                 nowfenData = nowFenElement.text.encode('utf-8')
             else:
                  print("now fen is not get!!!")
    else :
        nowfenData = nowFenStr.encode("utf-8")
    # 总分
    if nowFenElement == None :
        totalfen = "5分".encode('utf-8')
    else :
        totalElement = nowFenElement.find("./span")
        if totalElement != None and totalElement.text != None and len(totalElement.text) > 0 :
             tmpzongfen = totalElement.text
             totalfen = tmpzongfen.replace('／',"").encode('utf-8')
        else:
             print("totalelemnt is not get !!!!")
    # 均价
    junjiaElement = tmpHeaderElement.xpath('//div/*[@class="inf_left fl "]')
    if isinstance(junjiaElement,list) :
        for tmpJunJia in junjiaElement :
            if tmpJunJia.get("class") == 'inf_left fl ' :
                tmpjunjiaData = tmpJunJia.find("./span")
                if tmpjunjiaData != None and tmpjunjiaData.get('class') == 'prib cn_ff' :
                    if len(tmpjunjiaData.text) >0 :
                        nextJunJiaStr = tmpjunjiaData.tail
                        nextJunJiaStr = nextJunJiaStr.replace("\t","")
                        nextJunJiaStr = nextJunJiaStr.replace("\n","")
                        junjia = tmpjunjiaData.text.encode('utf-8')
                        if len(nextJunJiaStr) > 0 :
                            junjia += nextJunJiaStr.encode('utf-8')
                            break
                else :
                    tmpjunjiaData = tmpJunJia.find("./p/span")
                    if tmpjunjiaData != None and tmpjunjiaData.get('class') == 'prib cn_ff' :
                        if len(tmpjunjiaData.text) >0 :
                            nextJunJiaStr = tmpjunjiaData.tail
                            nextJunJiaStr = nextJunJiaStr.replace("\t","")
                            nextJunJiaStr = nextJunJiaStr.replace("\n","")
                            junjia = tmpjunjiaData.text.encode('utf-8')
                            if len(nextJunJiaStr) > 0 :
                                junjia += nextJunJiaStr.encode('utf-8')
                                break
    else:
        print("junjia element is not get!!!")
    # 咨询电话
    zixundianhuanElement = tmpHeaderElement.xpath('//*[@class="advice_left"]/p/span')
        #tmpHeaderElement.findall("./div/div/p/span")
    if isinstance(zixundianhuanElement,list) :
        for tmpzixunText in zixundianhuanElement :
            if len(tmpzixunText.text) >0 :
                zixundianhua += tmpzixunText.text.encode('utf-8')
            else :
                print("tmpzixunText is not found!!!")
    else:
        print("zixundianhuanElement is not list ,zixundianhua not get!!!")

    # 项目地址//*[@id="xfdsxq_B04_12"]
    xiangmudizhiElement = tmpHeaderElement.xpath('//div/*[@class="inf_left fl"]')
    if isinstance(xiangmudizhiElement,list) :
        for tmpxiangmuText in xiangmudizhiElement :
            if tmpxiangmuText != None  and tmpxiangmuText.get('class') == 'inf_left fl' \
                    and (tmpxiangmuText.get('id') == 'xfdsxq_B04_12' or tmpxiangmuText.get('id') == 'xfptxq_B04_12'):
                tmpSpanEle =  tmpxiangmuText.find("./span")
                if tmpSpanEle != None  :
                    tmpxiangmuTitle =  tmpSpanEle.get("title")
                    if tmpxiangmuTitle != None and len(tmpxiangmuTitle) > 0 :
                        xiangmudizhi = tmpxiangmuTitle.encode('utf-8')
                        break
                else :
                    tmpSpanEle =  tmpxiangmuText.find("./p/span")
                    if tmpSpanEle != None  :
                         tmpxiangmuTitle =  tmpSpanEle.get("title")
                         if tmpxiangmuTitle != None and len(tmpxiangmuTitle) > 0 :
                              xiangmudizhi = tmpxiangmuTitle.encode('utf-8')
                              break

    else:
        print("xiangmudizhiElement is not get!!!")

    # 主力户型
    zhulihuxingElement =  tmpHeaderElement.findall("./div/div/div/a")
    if isinstance(zhulihuxingElement,list)  and len(zhulihuxingElement) > 0:
        for tmpzhuliText in zhulihuxingElement :
            if tmpzhuliText.get("target") == '_blank':
                #此处需要转换转换成utf-8编码不然m2显示成乱码
                tmppingfangmi = '㎡'
                tes11  = tmppingfangmi.encode('utf-8')
                tmpzhuliTextStr = tmpzhuliText.text.encode('utf-8').replace('�',tmppingfangmi).strip()
                if len(zhulihuxing) > 0 :
                    zhulihuxing += ("  |  " + tmpzhuliTextStr.encode('utf-8'))
                else:
                    zhulihuxing += tmpzhuliTextStr.encode('utf-8')
    else:
         zhulihuxingElement = tmpHeaderElement.xpath('//*[@id="xfdsxq_B04_13"][@class="inf_left fl"]/div/a')
         if zhulihuxingElement == None or len(zhulihuxingElement) == 0 :
             zhulihuxingElement = tmpHeaderElement.xpath('//*[@id="xfptxq_B04_13"][@class="inf_left fl"]/p/a')
         if isinstance(zhulihuxingElement,list)  and len(zhulihuxingElement) > 0:
             for tmpzhuliText in zhulihuxingElement :
                 if tmpzhuliText.get("target") == '_blank':
                     #此处需要转换转换成utf-8编码不然m2显示成乱码
                     tmppingfangmi = '㎡'
                     tes11  = tmppingfangmi.encode('utf-8')
                     tmpzhuliTextStr = tmpzhuliText.text.encode('utf-8').replace('�',tmppingfangmi).strip()
                     if len(zhulihuxing) > 0 :
                          zhulihuxing += ("  |  " + tmpzhuliTextStr.encode('utf-8'))
                     else:
                          zhulihuxing += tmpzhuliTextStr.encode('utf-8')

    # 近期开盘
    jinqikaipanElement = tmpHeaderElement.xpath('//div/*[@class="inf_left fl"]')
    if isinstance(jinqikaipanElement,list) :
        for subjinQiElement in  jinqikaipanElement:
            if subjinQiElement != None and subjinQiElement.get("class") == 'inf_left fl' \
                    and subjinQiElement.get("id") == None :
                tmpKaiPanElement =  subjinQiElement.find("a")
                tmpH3Element = subjinQiElement.find("h3")
                tmpPElement = subjinQiElement.find("p")
                if tmpKaiPanElement == None and tmpH3Element != None  :
                    tmptailText  = tmpH3Element.tail
                    if tmptailText != None :
                        tmptailText = tmptailText.replace("\n","")
                        tmptailText = tmptailText.replace("\t","")
                        tmptailText = tmptailText.replace('  ',"")
                        if len(tmptailText) > 0:
                            jinqikaipan = tmptailText.encode('utf-8')
                            break
                elif tmpKaiPanElement != None:
                    if tmpKaiPanElement.get("class") == 'kaipan' :
                        jinqikaipan = tmpKaiPanElement.get("title").encode('utf-8')
                        break
                elif tmpKaiPanElement == None and tmpH3Element == None  and tmpPElement != None :
                     tmpAElement = tmpPElement.find("a")
                     if tmpAElement!= None and tmpAElement.get("target") =="_blank" :
                            jinqikaipan = tmpAElement.get("title")
                            if len(jinqikaipan) == 0 :
                                jinqikaipan = tmpAElement.text
                            jinqikaipan = jinqikaipan.encode("utf-8")
                            break
            elif  subjinQiElement != None and subjinQiElement.get("class") == 'inf_left fl' \
                    and subjinQiElement.get("id") == "xfptxq_B04_12" :
                tmpKaiPanElement =  subjinQiElement.find("span")
                if tmpKaiPanElement != None  and  len(tmpKaiPanElement.text) >0 :
                    tmpKaiPanContent  = tmpKaiPanElement.text.encode('utf-8')
                    if tmpKaiPanContent != xiangmudizhi :
                        jinqikaipan =  tmpKaiPanContent
                        break



    else:
        print("jinqikaipanElement is not get!!!!")

    rowDataList = []
    rowDataList.append(title)
    rowDataList.append(nowfenData)
    rowDataList.append(totalfen)
    rowDataList.append(junjia)
    rowDataList.append(zixundianhua)
    rowDataList.append(zhulihuxing)
    rowDataList.append(xiangmudizhi)
    rowDataList.append(jinqikaipan)
    rowDataList.append(cityStr)
    rowDataList.append(addressStr)
    rowDataList.append(urlStr)
    allRowDataLists.append(rowDataList)

    #写入excel
    columIndexData = 0
    rowIndexData =  len(allRowDataLists)
    for tmpNameStrRow in rowDataList :
        tmpNameData = tmpNameStrRow
        if  isinstance(tmpNameData,str) == False or len(tmpNameData) == 0 :
            tmpNameData = "None".encode("utf-8")

        print("rowIndex:" + str(rowIndexData))
        print("columIndex:"+str(columIndexData))
        print("tmpName:" +tmpNameData)
        excelSheet.write(rowIndexData,columIndexData,tmpNameData)
        columIndexData += 1

    print("getSinglePageContent is done!!")



def getSingleImageDownload(url,imageTitle,filePathStr,user_agent):
    print(url)
    # 开始下载单个图片
    try:
        headers = { 'User-Agent' : user_agent ,
                    'Content-Encoding':'gzip, deflate, sdch',
                    'Vary':'Accept-Encoding',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection':'keep-alive'}
        resText= requests.get(url,headers = headers, timeout=30)
    except requests.exceptions.RequestException as e:
        print ("当前图片无法下载:"+ str(e))
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

def getImageDownloads(url,title,user_agent) :
    #判断目录在不在,不再创建
    if (os.path.exists(imageDir) == False) :
        os.mkdir(imageDir,)
    #判断要下载的文件在不在,不在的话创建
    fileDirStr = imageDir +title
    if (os.path.exists(fileDirStr) == False ) :
        #发现文件夹没有创建,创建该文件夹
        os.mkdir(fileDirStr,)

    resText = getRequestUrlText(url,user_agent)
    if resText == None   :
        print("妈妈的获取图片失败了:"+url)
        return  False
    #解析成dom树
    html = etree.HTML(resText)
    bigImages = html.xpath('//*[@id="imageShowBig"]/li')
    print ("images cout: " + str(len(bigImages)))
    for tmpImage in bigImages :
        tmpImageStr =  tmpImage.find("./div/a/img")
        if tmpImageStr == None :
            tmpImageStr = tmpImage.find("./div/div/a/img")
        imageStr = tmpImageStr.get("src")
        imageTile = tmpImageStr.get("alt")
        if len(imageStr) :
            if imageStr.startswith("http://"):
                #开始下载图片
               res = getSingleImageDownload(imageStr,imageTile,fileDirStr,user_agent)
               if res == False :
                   print("妈妈告诉我图片下载失败了!!")
                   continue
            else:
                continue
        else:
            continue

# 获取单页面数据
def getSinglePageContentDownloads(url,user_agent,allRowDataLists) :
    print("getSinglePageContentDownloads:"+url)
    resText =  getRequestUrlText(url,user_agent)
    if resText == None :
        print("获取单页数据失败了:"+url)
        return  False

    #解析dom树
    html = etree.HTML(resText)
    links = html.xpath('//*[@id="bx1"]/div/div[1]/div[1]/div/div/ul/li')
    listUrl = []
    for tmpChild in links :
        children =  tmpChild.getchildren()
        for secondChild in children:
            if secondChild.get("class") == "clearfix":
                jumUrlattri = secondChild.find("./div/div/div/a")
                urlJump = jumUrlattri.get("href")
                if len(urlJump) :
                    #开始撸啊撸了
                    if urlJump.startswith("http://"):
                        listUrl.append(urlJump)
                        break
                    else :
                        continue
                else :
                    continue
            else :
                continue


    print ("list len is :" +str(len(listUrl)))
    #开始爬正文内容了哈
    for urlStr  in listUrl:
        print("contentUrl:"+urlStr)
        resText = getRequestUrlText(urlStr,user_agent)
        if  resText == None :
            print("正文解析失败了:"+urlStr)
            continue
        html = etree.HTML(resText)
        headerElement = html.xpath('/html/body/div[3]/div[3]/div[2]/div[1]')
        titleStr = None
        nowFenStr = None
        cityStr = None
        addressStr = None
        # 还有两个需要爬,一个city 一个address
        #获取 city
        pattern = re.compile(ur'var city = \W*;')
        resultCity = re.search(pattern,resText)
        if resultCity != None and resultCity.group() != None  :
            tmpCityStr = resultCity.group()
            tmpCityStr = tmpCityStr.replace('var city =',"")
            tmpCityStr = tmpCityStr.replace(';',"")
            tmpCityStr = tmpCityStr.replace('"',"")
            if len(tmpCityStr) > 0 :
                cityStr =  tmpCityStr.encode('utf-8')
        #获取 address
        pattern = re.compile(ur'address=\W*;')
        resultAddress = re.search(pattern,resText)
        if resultAddress != None and resultAddress.group() != None  :
            tmpAddressStr = resultAddress.group()
            tmpAddressStr = tmpAddressStr.replace('address=',"")
            tmpAddressStr = tmpAddressStr.replace(';',"")
            tmpAddressStr = tmpAddressStr.replace('"',"")
            tmpAddressStr = tmpAddressStr.replace('\'',"")
        if len(tmpAddressStr) > 0 :
            addressStr =  tmpAddressStr.encode('utf-8')
        if len(headerElement) >0 :
            getSinglePageContent(headerElement,allRowDataLists,titleStr,nowFenStr,cityStr,addressStr,urlStr)
        else:
            # 先获取标题啊
            titleElement = html.xpath('//*[@id="xfptxq_B03_01"]')
            if isinstance(titleElement,list) :
                for titleTmpElement  in titleElement :
                    if titleTmpElement.get('class') == 'ts_linear' and titleTmpElement.get('id') == 'xfptxq_B03_01' \
                            and len(titleTmpElement.get('title')) > 0:
                        titleStr = titleTmpElement.get('title').encode('utf-8')
                        break
            # 获取当前评分
            #var score_array_total = "4.23"
            pattern = re.compile(ur'var score_array_total = "[0-9].*[0-9]";')
            resultNowFen = re.search(pattern,resText)

            if resultNowFen != None and resultNowFen.group() != None  :
                groupNowFen = resultNowFen.group()
                groupNowFen = groupNowFen.replace('var score_array_total = ',"")
                groupNowFen = groupNowFen.replace(';',"")
                groupNowFen = groupNowFen.replace('"',"")
                if len(groupNowFen) > 0 :
                    nowFenStr =  groupNowFen.encode('utf-8')
            # 妈的一个网站多种样式,我日了狗了
            # 重试另一种爬法
            headerElement = html.xpath('/html/body/div[9]/div[10]/div[2]/div[1]')
            if len(headerElement) > 0 :
                getSinglePageContent(headerElement,allRowDataLists,titleStr,nowFenStr,cityStr,addressStr,urlStr)
            else:
                headerElement = html.xpath('/html/body/div[7]/div[10]/div[2]/div[1]')
                if len(headerElement) > 0 :
                    getSinglePageContent(headerElement,allRowDataLists,titleStr,nowFenStr,cityStr,addressStr,urlStr)
        #爬图片了
        currentRowDataIndex = len(allRowDataLists) -1
        currentRowDataList =  allRowDataLists[currentRowDataIndex]
        titleData = currentRowDataList[0]
        getImageDownloads(urlStr,titleData,user_agent)

    return  True


def main() :
    url = "http://newhouse.hz.fang.com/house/s"
  #  user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    user_agent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/545.1 (KHTML, like Gecko) Chrome/14.0.810.0 Safari/545.1"
    allRowDataLists = []
    indexValue = 0

    listColums = [u"标题",u"当前评分",u"总分",u"均价",u"咨询电话",u"主力户型",u"项目地址",u"近期开盘",u"城市",u"具体区",u"网站地址"]

    columIndex = 0
    for tmpName in listColums :
        excelSheet.write(0,columIndex,tmpName)
        columIndex += 1
    rowIndexData = 1
    #获取内容
    resText =  getRequestUrlText(url,user_agent)
    if resText == None :
        print("getRequestUrlText is fail" +url)
        return False

    html = etree.HTML(resText)
    pagesList = html.xpath('//*[@id="sjina_C01_47"]/ul/li[2]/a')

    pagesUrlList = []
    if isinstance(pagesList,list)  and len(pagesList) > 0:
        lastpageData =  pagesList[-1]
        if lastpageData!= None and lastpageData.get("class") == "last" :
            lastPageStr = lastpageData.get("href")
            lastPageStr = lastPageStr.replace("/house/s/b9","")
            lastPageStr = lastPageStr.replace("/","")
            lastPageData = int(lastPageStr)
            for i in range(1,lastPageData+1) :
                tmpUrlData = url +"/b9"+ str(i) +"/"
                pagesUrlList.append(tmpUrlData)
        else:
            print("can't find last page")
            return None
    else  :
        print("pagesList is not List")
        return None

    if len(pagesUrlList) == 0 :
        print("pagesUrlList is 0")
        return None
    for tmpUrlPage in pagesUrlList :
        getSinglePageContentDownloads(tmpUrlPage,user_agent,allRowDataLists)



    excelFile.save(excelFilePath)
    print ("pachong is over right!!!")

#主函数
if __name__ == '__main__':
   sys.exit(main())


