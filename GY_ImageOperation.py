from PIL import ImageGrab  # 截图不崩溃
import pyautogui  # 操作模拟，图像定位
import cv2  # 图像处理
import numpy as np
import ctypes

import GY_logging

# recSupposedArea = None, 第二层检测机制。防止false-positive。
# recSupposedArea 图片在屏幕上的正常范围的top，left，bottom，right四坐标
# recTargetRegion = None 代表全屏搜索 （经测试，recTargetRegion = None 和不声明 recTargetRegion 参数，都会进行全屏搜索，而且速度一样）
def locate_in_region_with_confidence(strImagePath, recTargetRegion = None, recSupposedArea = None, fLowestConfidence = 0.4, bGrayScale = False):
    fCurrentConfidence = 1.00
    recImagePosition = pyautogui.locateOnScreen(strImagePath, region=recTargetRegion, grayscale = bGrayScale)

    # 不断微量调低confidence期望，以求找到最符合的结果
    while recImagePosition == None:
        if fCurrentConfidence == fLowestConfidence:
            break

        fCurrentConfidence -= 0.03
        if fCurrentConfidence < fLowestConfidence:
            fCurrentConfidence = fLowestConfidence

        recImagePosition = pyautogui.locateOnScreen(strImagePath, region=recTargetRegion,
                                                    confidence = fCurrentConfidence, grayscale = bGrayScale)

    GY_logging.debug("定位图像" + strImagePath + "结束。本次定位最终confidence：" + str(fCurrentConfidence) + "。")

    return rec_result_validation(recImagePosition, recSupposedArea)


# 冗余函数，为了兼容旧版本留着。
def locate_in_fullscreen_with_confidence(strImagePath, recSupposedArea = None, fLowestConfidence = 0.4, bGrayScale = False):
    return locate_in_region_with_confidence(strImagePath = strImagePath, recTargetRegion = None,
                                            recSupposedArea = recSupposedArea, fLowestConfidence = fLowestConfidence,
                                            bGrayScale = bGrayScale)

# 弃用，有内在缺陷（左边的如果没有在右边的之前被识别，即右边的confidence高一些，那么左边的会永远被忽略）
def __locate_all_in_region_with_confidence(strImagePath, recTargetRegion, recSupposedArea = None,
                                         fLowestConfidence = 0.4, bGrayScale = False):
    lstRes = []
    nXShifting = recTargetRegion[0]

    while True:
        recInstance = locate_in_region_with_confidence(strImagePath,
                                                       (nXShifting, recTargetRegion[1], recTargetRegion[2], recTargetRegion[3]),
                                                       recSupposedArea, fLowestConfidence, bGrayScale)
        if recInstance != None:
            lstRes.append(recInstance)

            nXShifting = recInstance[0] + recInstance[2]
            if nXShifting >= recTargetRegion[2] - recInstance[2]:
                break
        else:
            break

    return lstRes

def locate_all_in_region_with_confidence(strImagePath, recTargetRegion, recSupposedArea = None,
                                         fLowestConfidence = 0.65, bGrayScale = False):
    fConfidence = 1.0
    lstResFinal = []

    while True:
        fConfidence -= 0.03
        if fConfidence < fLowestConfidence:
            break

        lstResTmp = pyautogui.locateAllOnScreen(strImagePath, region=recTargetRegion, grayscale = bGrayScale, confidence = fConfidence)

        for eachPos in lstResTmp:
            if check_if_img_is_already_in_lst(tuple(eachPos), lstResFinal) == True:
                continue
            if check_if_img_is_inside_supposed_area(tuple(eachPos), recSupposedArea) == False:
                break

            lstResFinal.append(tuple(eachPos))

    return lstResFinal

def check_if_img_is_already_in_lst(recImg, lstImages, nDistanceAllowance = 10):
    for eachImg in lstImages:
        if calculate_img_distance_plain(recImg, eachImg) < nDistanceAllowance:
            return True

    return False

def calculate_img_distance_plain(recImgA, recImgB):
    return abs(recImgA[0] - recImgB[0]) + abs(recImgA[1] - recImgB[1])

def check_if_img_is_inside_supposed_area(recImg, recSupposedArea):
    if recImg[0] < recSupposedArea[0] or recImg[1] < recSupposedArea[1]:
        return False
    if recImg[0] + recImg[2] > recSupposedArea[2] or recImg[1] + recImg[3] > recSupposedArea[3]:
        return False

    return True

def rec_result_validation(recImagePosition, recSupposedArea):
    if recImagePosition == None:
        GY_logging.debug("已到达confidence底线，但没有定位到目标图像。")
        return None

    GY_logging.debug("定位到的位置是：" + str(recImagePosition))
    if recImagePosition != None and recSupposedArea != None:
        if check_if_img_is_inside_supposed_area(recImagePosition, recSupposedArea) == False:
            GY_logging.debug("定位到目标图像，但是和应在区域不符合，因此判断定位错误，即目标图像不存在于当前区域。")
            return None

    return recImagePosition

def get_recog_ready_binary_image(rec):
    CaptureImg = ImageGrab.grab(bbox=rec)
    CaptureImgNP = np.asarray(CaptureImg)
    ImgRGB = cv2.cvtColor(CaptureImgNP, cv2.COLOR_BGR2RGB)
    ImgGray = cv2.cvtColor(ImgRGB, cv2.COLOR_RGB2GRAY)
    (thresh, ImgBinary) = cv2.threshold(ImgGray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    return ImgBinary