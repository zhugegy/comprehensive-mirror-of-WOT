from pynput.keyboard import Key, KeyCode
import time

import cv2
from matplotlib import pyplot as plt

import GY_ImageOperation
import GY_CharRecog
import GY_logging

import parameters

g_fAnalyzed = False


def locker():
    global  g_fAnalyzed
    global g_fTeamLayoutAnalyzed
    g_fAnalyzed = False
    g_fTeamLayoutAnalyzed = False
    GY_CharRecog.init(parameters.VERIFIED_CHARRECOG_PATH, parameters.UNVERIFIED_CHARRECOG_PATH)
    GY_logging.info("reset success")

def analysis_by_names():
    global  g_fAnalyzed
    if g_fAnalyzed:
        return
    time.sleep(0.3)   # 按下键盘后，游戏界面刷新延迟
    g_fAnalyzed = True
    map_analysis()
    team_layout_analysis()

def map_analysis():
    imgMapName = GY_ImageOperation.get_recog_ready_binary_image(
        (parameters.GAME_RECT_LEFT + parameters.GAME_MAP_NAME_LEFT,
         parameters.GAME_RECT_TOP + parameters.GAME_MAP_NAME_TOP,
         parameters.GAME_RECT_LEFT + parameters.GAME_MAP_NAME_LEFT + parameters.GAME_MAP_NAME_WIDTH,
         parameters.GAME_RECT_TOP + parameters.GAME_MAP_NAME_TOP + parameters.GAME_MAP_NAME_HEIGHT))

    strMapName = GY_CharRecog.Chinese_char_recog_for_binary_pic(imgMapName)
    GY_logging.info("Map name identified: " + strMapName)
    print(strMapName)


def team_layout_analysis():
    lstNames = ""
    for enemy in range(15):
        imgEnemyName = GY_ImageOperation.get_recog_ready_binary_image((parameters.GAME_RECT_LEFT + parameters.GAME_ENEMY_NAME_LEFT,
                                                                 parameters.GAME_RECT_TOP + parameters.GAME_ENEMY_NAME_TOP + enemy * parameters.GAME_ENEMY_NAME_HEIGHT,
                                                                 parameters.GAME_RECT_LEFT + parameters.GAME_ENEMY_NAME_LEFT + parameters.GAME_ENEMY_NAME_WIDTH,
                                                                 parameters.GAME_RECT_TOP + parameters.GAME_ENEMY_NAME_TOP + enemy * parameters.GAME_ENEMY_NAME_HEIGHT + parameters.GAME_ENEMY_NAME_HEIGHT))
        strEnemyName = GY_CharRecog.Chinese_char_recog_for_binary_pic(imgEnemyName)
        GY_logging.info("Enemy name identified: " + strEnemyName)
        print(strEnemyName)
        lstNames += strEnemyName + ", "

    print(lstNames)



def function_2():
    # print('Executed function_2')
    # img1 = cv2.imread('test/test11.png', 0)
    # cv2.imshow('image1', img1)
    # img2 = cv2.imread('test/test12.png', 0)
    # cv2.imshow('image2', img2)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return


combination_to_function = {
    frozenset([KeyCode(vk=9)]): analysis_by_names,  # tab
    frozenset([KeyCode(vk=110)]): locker,  # numpad - delete
    frozenset([Key.shift, KeyCode(vk=66)]): function_2,  # shift + b
    frozenset([Key.alt_l, KeyCode(vk=71)]): function_2,  # left alt + g
}



# show img
# cv2.imshow('image', imgMapName)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# plt.imshow(imgMapName, cmap='gray', interpolation='bicubic')
# plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
# plt.draw()
# plt.pause(0.001)