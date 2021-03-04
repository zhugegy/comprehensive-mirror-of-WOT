import os
import cv2
import uuid
import pytesseract
import numpy as np
import re

from PIL import Image

# from GY_stzb_ao_Parameters import *
import GY_logging

g_VERIFIED_CHARRECOG_PATH = ""
g_UNVERIFIED_CHARRECOG_PATH = ""

g_dVerifiedDic = {}
g_dUnverifiedDic = {}

g_nTypeAnnotation = 10

def init(strVerifiedPath, strUnverifiedPath):
    global g_VERIFIED_CHARRECOG_PATH
    global g_UNVERIFIED_CHARRECOG_PATH

    global g_dVerifiedDic
    global g_dUnverifiedDic
    global g_nTypeAnnotation

    GY_logging.info("开始初始化中文识别引擎。")

    g_VERIFIED_CHARRECOG_PATH = strVerifiedPath
    g_UNVERIFIED_CHARRECOG_PATH = strUnverifiedPath

    strExePath = os.getcwd() + "/"

    strVerifiedPath = strExePath + g_VERIFIED_CHARRECOG_PATH + "/"
    lVerifiedLst = os.listdir(strVerifiedPath)
    init_dict(lVerifiedLst, g_dVerifiedDic)

    strUnverifiedPath = strExePath + g_UNVERIFIED_CHARRECOG_PATH + "/"
    lUnverifiedLst = os.listdir(strUnverifiedPath)
    init_dict(lUnverifiedLst, g_dUnverifiedDic)

    g_nTypeAnnotation = 10

    #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    GY_logging.info("结束初始化中文识别引擎。")
    return True

# def set_recog_type(nType):
#     global g_nTypeAnnotation
#     g_nTypeAnnotation = nType
#     return True

def clean_string(line):
    #ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    #return ansi_escape.sub('', line).replace('\n', '').replace(' ', '')
    return line.replace(' ', '').replace('\n', '').replace('\f', '').replace('\r', '').replace('\n', '').replace("\"", "").replace("\\", "")  # replace('\xXX', '')

def init_dict(lContentList, dicTargetDict):
    dicTargetDict.clear()
    for strFileName in lContentList:
        lTmp = strFileName[:-4].split('#')
        nHashValue = int(lTmp[2], 16)
        if dicTargetDict.get(nHashValue, "") == "":
            dicTargetDict[nHashValue] = strFileName
        else:
            dicTargetDict[nHashValue] = dicTargetDict[nHashValue] + ";" + strFileName

    return True

def number_recog_for_binary_pic(picContent, strWhilteList = ""):
    strConfigStringTmp = "-c tessedit_char_whitelist=" + strWhilteList + "0123456789 --psm 6"
    ImageEnlarged = cv2.resize(picContent, (0, 0), fx=8, fy=8)  # 放大8倍，提高识别准确率
    strRes = pytesseract.image_to_string(ImageEnlarged, config=strConfigStringTmp)
    return clean_string(strRes)   #return strRes 不行，因为要去除空格

# 已弃用，放在这里是为了兼容之前的代码
def number_dot_recog_for_binary_pic(picContent):
    return number_recog_for_binary_pic(picContent, ".")

# 已弃用，放在这里是为了兼容之前的代码
def hms_time_string_recog_for_binary_pic(picContent):
    return number_recog_for_binary_pic(picContent, ":")

# 已弃用，放在这里是为了兼容之前的代码
def pure_number_recog_for_binary_pic(picContent):
    return number_recog_for_binary_pic(picContent)

def Chinese_char_recog_for_binary_pic(picContent, nRecogType = 10):
    #debug
    global g_dVerifiedDic
    global g_dUnverifiedDic
    global g_nTypeAnnotation

    # debug
    # print(dVerifiedDic)
    # print(dUnverifiedDic)

    g_nTypeAnnotation = nRecogType

    nHashValue = calculate_img_ahash(picContent)

    return get_str_via_verified(nHashValue, picContent)

def get_str_via_verified(nHashValue, picContent):
    global g_dVerifiedDic

    strExePath = os.getcwd() + "/"
    strVerifiedPath = strExePath + g_VERIFIED_CHARRECOG_PATH + "/"

    lVerifiedRelativeKey = []

    # 查找dVerifiedDic
    GY_logging.debug("查找dVerifiedDic...")
    if g_dVerifiedDic.get(nHashValue, "") == "":
        # 查找dVerified未找到，查找relative
        GY_logging.debug("查找dVerified未找到，查找relative...")
        if get_relative_keys_based_on_hamming_distance(nHashValue, g_dVerifiedDic, lVerifiedRelativeKey) != 0:
            # 找到了relative keys,进一步对比图像尺寸和pixel具体差异
            GY_logging.debug("查找dVerified未找到，查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...")
            resFileName = compare_image_details(picContent, strVerifiedPath, g_dVerifiedDic, lVerifiedRelativeKey, "null")
            if resFileName != "null":  # != None? is also feasible in python
                # 找到对应图片了
                GY_logging.debug( "查找dVerified未找到，查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...找到了:" + resFileName)
                GY_logging.info("文字识别结果为：" + resFileName.split('#')[0])
                return resFileName.split('#')[0]

            # dVerified relative keys虽然有，但是依然没有找到内容完全匹配的图片，只好去unverified查找
            GY_logging.debug("查找dVerified未找到，查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...没找到...只好去unverified查找...")
            return get_str_via_unverified(nHashValue, picContent)
        else:
            # 没找到relative keys，只好去unverified查找
            GY_logging.debug("查找dVerified未找到，查找relative...没找到relative,只好去unverified查找...")
            return get_str_via_unverified(nHashValue, picContent)
    else:
        # 查找dVerified找到了，进一步对比图像尺寸和pixel具体差异
        GY_logging.debug("查找dVerified找到了，进一步对比图像尺寸和pixel具体差异...")
        resFileName = compare_image_details(picContent, strVerifiedPath, g_dVerifiedDic, nHashValue, "null")
        if resFileName != "null":
            # 找到对应图片了
            GY_logging.debug("查找dVerified找到了，进一步对比图像尺寸和pixel具体差异...找到了:" + resFileName)
            GY_logging.info("文字识别结果为：" + resFileName.split('#')[0])
            return resFileName.split('#')[0]

        # 查找dVerified找到了，进一步对比图像尺寸和pixel具体差异，没有匹配的，查找relative
        GY_logging.debug("查找dVerified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...")
        if get_relative_keys_based_on_hamming_distance(nHashValue, g_dVerifiedDic, lVerifiedRelativeKey) != 0:
            # 找到了relative keys,进一步对比图像尺寸和pixel具体差异
            GY_logging.debug("查找dVerified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...")
            resFileName = compare_image_details(picContent, strVerifiedPath, g_dVerifiedDic, lVerifiedRelativeKey, "null")
            if resFileName != "null":
                # 找到对应图片了
                GY_logging.debug(
                    "查找dVerified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...找到了：" + resFileName)
                GY_logging.info("文字识别结果为：" + resFileName.split('#')[0])
                return resFileName.split('#')[0]

            # relative keys虽然有，但是依然没有找到内容完全匹配的图片，只好去unverified查找
            GY_logging.debug(
                "查找dVerified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...没找到，只好去unverified查找...")
            return get_str_via_unverified(nHashValue, picContent)
        else:
            # 没找到relative keys，只好去unverified查找
            GY_logging.debug("查找dVerified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...没找到relative keys，只好去unverified查找...")
            return get_str_via_unverified(nHashValue, picContent)

    GY_logging.error("The program should NEVER reach here!")
    return get_str_via_unverified(nHashValue, picContent)

def get_str_via_unverified(nHashValue, picContent):
    global g_dUnverifiedDic

    strExePath = os.getcwd() + "/"
    strUnverifiedPath = strExePath + g_UNVERIFIED_CHARRECOG_PATH + "/"

    lUnverifiedRelativeKey = []

    # 查找dUnverifiedDic
    GY_logging.debug("查找dUnverifiedDic...")
    if g_dUnverifiedDic.get(nHashValue, "") == "":
        # 查找dUnverified未找到，查找relative
        GY_logging.debug("查找dUnverified未找到，查找relative...")
        if get_relative_keys_based_on_hamming_distance(nHashValue, g_dUnverifiedDic, lUnverifiedRelativeKey) != 0:
            # 找到了relative keys,进一步对比图像尺寸和pixel具体差异
            GY_logging.debug("查找dUnverified未找到，查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...")
            resFileName = compare_image_details(picContent, strUnverifiedPath, g_dUnverifiedDic, lUnverifiedRelativeKey, "null")
            if resFileName != "null":
                # 找到对应图片了
                GY_logging.debug(
                    "查找dUnverified未找到，查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...找到了:" + resFileName)
                GY_logging.info("文字识别结果为：" + resFileName.split('#')[0])
                return resFileName.split('#')[0]

            # dUnverified relative keys虽然有，但是依然没有找到内容完全匹配的图片，只好ORC
            GY_logging.debug(
                "查找dUnverified未找到，查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...没找到...只好去ORC...")
            return get_str_via_ORC(nHashValue, picContent)
        else:
            # 没找到relative keys，只好去ORC
            GY_logging.debug("查找dUnverified未找到，查找relative...没找到relative,只好去ORC...")
            return get_str_via_ORC(nHashValue, picContent)
    else:
        # 查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异
        GY_logging.debug("查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异...")
        resFileName = compare_image_details(picContent, strUnverifiedPath, g_dUnverifiedDic, nHashValue, "null")
        if resFileName != "null":
            # 找到对应图片了
            GY_logging.debug("查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异...找到了:" + resFileName)
            GY_logging.info("文字识别结果为：" + resFileName.split('#')[0])
            return resFileName.split('#')[0]

        # 查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异，没有匹配的，查找relative
        GY_logging.debug("查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...")
        if get_relative_keys_based_on_hamming_distance(nHashValue, g_dUnverifiedDic, lUnverifiedRelativeKey) != 0:
            # 找到了relative keys,进一步对比图像尺寸和pixel具体差异
            GY_logging.debug(
                "查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...")
            resFileName = compare_image_details(picContent, strUnverifiedPath, g_dUnverifiedDic, lUnverifiedRelativeKey, "null")
            if resFileName != "null":
                # 找到对应图片了
                GY_logging.debug(
                    "查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...找到了：" + resFileName)
                GY_logging.info("文字识别结果为：" + resFileName.split('#')[0])
                return resFileName.split('#')[0]

            # relative keys虽然有，但是依然没有找到内容完全匹配的图片，只好去ORC
            GY_logging.debug(
                "查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...找到了relative keys,进一步对比图像尺寸和pixel具体差异...没找到，只好去ORC...")
            return get_str_via_ORC(nHashValue, picContent)
        else:
            # 没找到relative keys，只好去ORC
            GY_logging.debug(
                "查找dUnverified找到了，进一步对比图像尺寸和pixel具体差异...没找到...所以查找relative...没找到relative keys，只好去ORC...")
            return get_str_via_ORC(nHashValue, picContent)

    GY_logging.error("The program should NEVER reach here!")
    return get_str_via_ORC(nHashValue, picContent)

def get_str_via_ORC(nHashValue, picContent):
    global g_dUnverifiedDic

    GY_logging.warning("文字识别引擎不得不使用第三方库对图片进行文字识别。")
    ImageEnlarged = cv2.resize(picContent, (0, 0), fx=8, fy=8)  # 放大8倍，提高识别准确率
    # black list : /  这是为了防止产生\n，它会违法文件名的命名规范进而引起程序崩溃
    #result = pytesseract.image_to_string(ImageEnlarged, lang='eng', config="-c tessedit_char_blacklist=/*:_.| --psm 6")
    result = pytesseract.image_to_string(ImageEnlarged, lang='eng', config="-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6")
    result = clean_string(result)

    if len(result) == 0:
        result = "NULL"

    save_file_to_folder(result, nHashValue, picContent, g_dUnverifiedDic, g_UNVERIFIED_CHARRECOG_PATH)
    GY_logging.info("文字识别结果为：" + result)
    return result

def save_file_to_folder(strRecogResult, nHashValue, picContent, dicTarget, strFolderName, strTailer =""):
    strExePath = os.getcwd() + "/"
    strFolderPath = strExePath + strFolderName + "/"

    # 分机str(uuid.uuid4())[:1] 甚至1-5 (12345),确保分机不会造成过多重复垃圾，从而影响图片匹配效率。
    # 主机依然是str(uuid.uuid4())[:8]，确保在字符产生变化波动的时候，能持续不断地获取尽量多的样本。
    strFileName = strRecogResult + "#" + "r" + str(g_nTypeAnnotation) + "t" + str(uuid.uuid4())[:8] + "#" + str(hex(nHashValue)) + strTailer + ".png"

    # cv2.imwrite(strUnverifiedPath + strFileName, picContent)
    # np.save(strUnverifiedPath + strFileName, picContent)
    im = Image.fromarray(picContent)
    # 测试重名文件：结果：覆盖原文件，并不会产生两个文件
    im.save(strFolderPath + strFileName)

    GY_logging.warning("文字识别引擎往硬盘里存了文件：" + strFolderPath + strFileName)

    # 更新dic
    if dicTarget.get(nHashValue, "") == "":
        dicTarget[nHashValue] = strFileName
    else:
        dicTarget[nHashValue] = dicTarget[nHashValue] + ";" + strFileName

    return True

# 放大8倍抵消glich，不好用（完全没效果）
def __compare_image_details(picContent, strHaystackPath, dictHaystack, nORlKey, strDefaultRet = "null",
                          percentageMaxPixelTolerance = 0.01, percentageTolerablePixel = 0.005,
                          nExactCutoffPixels = -1, nExactTolerablePixel = -1):
    global g_dVerifiedDic
    # 构建FileName的list
    h, w = picContent.shape[:2]
    nRectSize = h * 8  * w * 8
    GY_logging.debug("当前图片像素总量：" + str(nRectSize))

    picContent = cv2.resize(picContent, dsize=(w * 8, h * 8), interpolation = cv2.INTER_AREA)

    if nExactCutoffPixels == -1:
        nExactCutoffPixels = int(nRectSize * percentageMaxPixelTolerance)  # 火星子问题
    GY_logging.debug("当前图片大容忍设置为：" + str(nExactCutoffPixels))

    if nExactTolerablePixel == -1:
        nExactTolerablePixel = int(nRectSize * percentageTolerablePixel)
    GY_logging.debug("当前图片小容忍设置为：" + str(nExactTolerablePixel))

    lFileNames = []

    if str(type(nORlKey)) == "<class 'list'>":
        GY_logging.debug("传入的参数是list类型，开始收集文件名...")
        for eachkey in nORlKey:
            strRawList = dictHaystack[eachkey]
            lstFileNamesSub = strRawList.split(';')
            for eachFileName in lstFileNamesSub:
                lFileNames.append(eachFileName)
    elif str(type(nORlKey)) == "<class 'int'>":
        GY_logging.debug("传入的参数是int类型，开始收集文件名...")
        strRawList = dictHaystack[nORlKey]
        lstFileNamesSub = strRawList.split(';')
        for eachFileName in lstFileNamesSub:
            lFileNames.append(eachFileName)
    else:
        GY_logging.error("The program should NEVER reach here!")

    # 比较图像尺寸，找到最小差异的图片
    nCurrentMinDiff = nExactCutoffPixels
    strFileName = strDefaultRet

    for eachFileName in lFileNames:
        stream = open(strHaystackPath + eachFileName, "rb")
        bytes = bytearray(stream.read())
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        imgTarget = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        hTarget, wTarget = imgTarget.shape[:2]

        if hTarget != h or wTarget != w:
            GY_logging.debug("图像尺寸不一致，否决。 FileName: " + eachFileName)
            continue

        imgTarget = cv2.resize(imgTarget, dsize=(w * 8, h * 8), interpolation = cv2.INTER_AREA)


        # 比较像素点差异数量 (a == b).sum()
        nCounter = (imgTarget != picContent).sum()
        GY_logging.debug("当前图像：" + eachFileName + "。像素差异点数量：" + str(nCounter))

        if nCounter <= nCurrentMinDiff :
            nCurrentMinDiff = nCounter
            strFileName = eachFileName
            GY_logging.debug("得到当前最符合条件图片。 FileName: " + eachFileName)

    if strFileName != "null" and nCurrentMinDiff >= nExactTolerablePixel:
        nPicHash = calculate_img_ahash(picContent)
        save_file_to_folder(strFileName.split('#')[0], nPicHash, picContent, g_dVerifiedDic, g_VERIFIED_CHARRECOG_PATH, "#SUSP")
        GY_logging.debug("当前图片像素总量：" + str(nRectSize))
        GY_logging.debug("当前图片大容忍设置为：" + str(nExactCutoffPixels))
        GY_logging.debug("当前图片小容忍设置为：" + str(nExactTolerablePixel))
        GY_logging.debug("图片pixel差异较大，有些可疑，备案保存至Verified-SUSPICIOUS。 差异数量：" +
                         str(nCurrentMinDiff) + "。原FileName: " + strFileName + "。新FileHash:" + str(hex(nPicHash)))

    return strFileName

def compare_image_details(picContent, strHaystackPath, dictHaystack, nORlKey, strDefaultRet = "null",
                          percentageMaxPixelTolerance = 0.05, percentageTolerablePixel = 0.005,
                          nExactCutoffPixels = -1, nExactTolerablePixel = -1):
    global g_dVerifiedDic
    # 构建FileName的list
    h, w = picContent.shape[:2]
    nRectSize = h * w
    GY_logging.debug("当前图片像素总量：" + str(nRectSize))

    if nExactCutoffPixels == -1:
        nExactCutoffPixels = int(nRectSize * percentageMaxPixelTolerance)  # 火星子问题
    GY_logging.debug("当前图片大容忍设置为：" + str(nExactCutoffPixels))

    if nExactTolerablePixel == -1:
        nExactTolerablePixel = int(nRectSize * percentageTolerablePixel)
    GY_logging.debug("当前图片小容忍设置为：" + str(nExactTolerablePixel))

    lFileNames = []

    if str(type(nORlKey)) == "<class 'list'>":
        GY_logging.debug("传入的参数是list类型，开始收集文件名...")
        for eachkey in nORlKey:
            strRawList = dictHaystack[eachkey]
            lstFileNamesSub = strRawList.split(';')
            for eachFileName in lstFileNamesSub:
                lFileNames.append(eachFileName)
    elif str(type(nORlKey)) == "<class 'int'>":
        GY_logging.debug("传入的参数是int类型，开始收集文件名...")
        strRawList = dictHaystack[nORlKey]
        lstFileNamesSub = strRawList.split(';')
        for eachFileName in lstFileNamesSub:
            lFileNames.append(eachFileName)
    else:
        GY_logging.error("The program should NEVER reach here!")

    # 比较图像尺寸，找到最小差异的图片
    nCurrentMinDiff = nExactCutoffPixels
    strFileName = strDefaultRet

    for eachFileName in lFileNames:
        stream = open(strHaystackPath + eachFileName, "rb")
        bytes = bytearray(stream.read())
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        imgTarget = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        hTarget, wTarget = imgTarget.shape[:2]

        if hTarget != h or wTarget != w:
            GY_logging.debug("图像尺寸不一致，否决。 FileName: " + eachFileName)
            continue

        # 比较像素点差异数量 (a == b).sum()
        nCounter = (imgTarget != picContent).sum()
        GY_logging.debug("当前图像：" + eachFileName + "。像素差异点数量：" + str(nCounter))

        if nCounter <= nCurrentMinDiff :
            nCurrentMinDiff = nCounter
            strFileName = eachFileName
            GY_logging.debug("得到当前最符合条件图片。 FileName: " + eachFileName)
            if nCounter == 0:
                break

    if strFileName != "null" and nCurrentMinDiff >= nExactTolerablePixel:
        nPicHash = calculate_img_ahash(picContent)
        save_file_to_folder(strFileName.split('#')[0], nPicHash, picContent, g_dVerifiedDic, g_VERIFIED_CHARRECOG_PATH, "#SUSP")
        GY_logging.debug("当前图片像素总量：" + str(nRectSize))
        GY_logging.debug("当前图片大容忍设置为：" + str(nExactCutoffPixels))
        GY_logging.debug("当前图片小容忍设置为：" + str(nExactTolerablePixel))
        GY_logging.debug("图片pixel差异较大，有些可疑，将备案保存至Verified-SUSPICIOUS。 差异数量：" +
                         str(nCurrentMinDiff) + "。原FileName: " + strFileName + "。新FileHash:" + str(hex(nPicHash)))

    return strFileName

def get_relative_keys_based_on_hamming_distance(nHashValue, dTargetDict, OUT_lnRelativeKeys, nCutoffDistance = 10):
    nCounter = 0
    for key in dTargetDict:
        if calculate_hamming_distance(nHashValue, key) <= nCutoffDistance:
            GY_logging.debug("哈希hamming差异值：" + str(calculate_hamming_distance(nHashValue, key)) + " 哈希1:" + str(hex(nHashValue)) + "哈希2：" + str((hex(key))))
            OUT_lnRelativeKeys.append(key)
            nCounter += 1

    return nCounter

def calculate_hamming_distance(n1, n2):
    x = n1 ^ n2
    setBits = 0

    while (x > 0):
        setBits += x & 1
        x >>= 1

    return setBits

def calculate_img_ahash(picContent, hashSize=8):
    # resize the input image
    resized = cv2.resize(picContent, (hashSize, hashSize))

    diff = resized[:,:] != 255

    # convert the difference image to a hash
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])