import time  #计时
import win32gui #WinAPI
import win32con
import re #正则
import ctypes  #屏幕分辨率识别

import GY_logging

class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self, strWindowName):
        """Constructor"""
        self._handle = None
        self._rect = [-1, -1, -1, -1]
        strWildCard = "^" + strWindowName +  "$"
        self.find_window_via_wildcard(strWildCard)
        if self.is_window_exsiting() == False:
            GY_logging.error("没有找到想要的窗口，窗口句柄为空。")

    # def find_window(self, class_name, window_name=None):
    #     """find a window by its class_name"""
    #     self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            GY_logging.debug("已找到匹配的窗口，wildcard：" + wildcard  + " 。句柄值：" + str(hwnd))
            self._handle = hwnd
            self._rect = list(win32gui.GetWindowRect(hwnd)).copy()

    def find_window_via_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        GY_logging.debug("根据wildcard：" + wildcard + "寻找匹配的窗口...")
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        if self._handle != None:
            win32gui.ShowWindow(self._handle, 5)  #SW_SHOW
            # SW_SHOW宏没有发现定义，所以只能硬编码
            # 详细编码内容见微软官网 https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-showwindow
            win32gui.ShowWindow(self._handle, 9)  #SW_RESTORE
            # gy_keynote 不用pyautogui库的restore()函数的原因：识别太宽泛，“率土之滨吧”这种窗口也会被getWindow()识别到
            # 因此就选择了使用WinAPI配合正则 (pyautogui库的getWindow()函数不支持正则（准确地说，是不支持获取窗口名称，
            # 即WinAPI的GetWindowText()功能）)
            win32gui.SetForegroundWindow(self._handle)
            return True
        else:
            return False

    def is_window_exsiting(self):
        """check if the window exists"""
        if self._handle != None:
            return True
        else:
            return False

    def get_rect(self):
        return self._rect

    def get_client_rect(self):
        return win32gui.GetClientRect(self._handle)

    def close_window(self):
        if (self.is_window_exsiting() == False):
            return
        return win32gui.PostMessage(self._handle,win32con.WM_CLOSE,0,0)

    def get_client_absolute_position(self):
        return win32gui.ClientToScreen(self._handle, (0,0))

    def align_window_to_topleft(self, nWidth, nHeight, nClientWidth, nClientHeight):
        GY_logging.info("我的老班长，技术援助留念！")
        if self.is_window_exsiting() == False:
            GY_logging.error("窗口句柄为空，无法操作。")
            return False

        # 把窗口弄到左上角
        # WINDOW_WIDTH = int(1168 * WS_A)
        # WINDOW_HEIGHT = int(686 * WS_A)
        # Client Stardard 1152 648
        win32gui.SetWindowPos(self._handle, 0, 0, 0, nWidth, nHeight, 0x0040)
        self.set_foreground()
        recSize = self.get_client_rect()
        GY_logging.debug("客户区Rect：" + str(recSize))
        lp = self.get_client_absolute_position()
        GY_logging.debug("客户区左上角绝对坐标：" + str(lp))

        # todo 根据客户区的大小，进行调整 （暂时不用弄，因为客户区大小目前符合标准）
        return True

    def set_window_position(self, nLeft, nTop, nWidth, nHeight):
        if self.is_window_exsiting() == False:
            GY_logging.error("窗口句柄为空，无法操作。")
            return False

        win32gui.SetWindowPos(self._handle, 0, nLeft, nTop, nWidth, nHeight, 0x0040)
        self.set_foreground()

        return True

    def get_client_region_absolute_postion(self):
        if self.is_window_exsiting() == False:
            GY_logging.error("窗口句柄为空，无法操作。")
            return (-1, -1, -1, -1)

        recSize = self.get_client_rect()
        lp = self.get_client_absolute_position()

        return (recSize[0] + lp[0], recSize[1] + lp[1], recSize[2] + lp[0], recSize[3] + lp[1])

    # 弃用
    def __resize_window(self, nWidth, nHeight, bResetIfNotFullyDisplay):
        if nWidth <= 0 or nHeight <= 0:
            return False

        if bResetIfNotFullyDisplay == True:
            # 获取当前屏幕分辨率
            user32 = ctypes.windll.user32
            screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            if self._rect[0] + nWidth >= screensize[0] or self._rect[1] + nHeight >= screensize[1]:
                self.reset_window_to_topleft()

        # win32gui.MoveWindow(self._handle,
        #                     self._rect[0], self._rect[1], nWidth, nHeight,
        #                     True)

        GY_logging.info("我的老班长 技术援助留念！")
        # win32gui.SetWindowPos(self._handle, 0,
        #                     self._rect[0], self._rect[1], nWidth + 8, nHeight + 26, 0x0040)
        win32gui.SetWindowPos(self._handle, 0,
                            self._rect[0], self._rect[1], nWidth, nHeight, 0x0040)

        # 8 -> 12 width  +4
        # 30 -> 52 height  + 22
        recSize = win32gui.GetClientRect(self._handle)
        print(recSize)

        lp = win32gui.ClientToScreen(self._handle, (0,0))
        print("absolute")
        print(lp)

        return True

    # 弃用，MoveWindow这个函数容易出错，让窗口“消失”，绘制不出来
    def __reset_window_to_topleft(self):
        self._rect[2] = self._rect[2] - self._rect[0]
        self._rect[3] = self._rect[3] - self._rect[1]
        self._rect[0] = 0
        self._rect[1] = 0

        win32gui.MoveWindow(self._handle,
                            self._rect[0], self._rect[1], self._rect[2] - self._rect[0], self._rect[3] - self._rect[1],
                            True)

        return True

# todo 有时候不稳（全屏的时候，默认屏幕大小倒是稳定）
def active_window(strWindowName, nWidth, nHeight, nClientWidth, nClientHeight):
    w = WindowMgr(strWindowName)
    return w.align_window_to_topleft(nWidth, nHeight, nClientWidth, nClientHeight)

def get_client_region_absolute_postion(strWindowName):
    w = WindowMgr(strWindowName)
    return w.get_client_region_absolute_postion()

# 失败的设计，弃用了
# 之前是为了针对客户（把程序交给客户使用），现在只有自己用，所以也就没有这些条条框框了
# 把名为strWindowName的窗口激活，并移动到最前
# OUT_lnLeftUpperPos 为返回的窗口左上角坐标
# 如果传入nWidth和nHeight，则会重置窗口大小
# bResetIfNotFullyDisplay用于处理当重置窗口大小后无法全部显示出来的情况：会直接把窗口移动到屏幕的最左上角(0, 0)处
def __active_window(strWindowName, OUT_lnLeftUpperPos = [-1, -1], nWidth = 0, nHeight = 0, bResetIfNotFullyDisplay = False):
    # w = WindowMgr()
    # strWildCard = "^" + strWindowName + "$"         # 防止“率土之滨吧”这种浏览器窗口被误识别
    #                                                 # todo --> 这个正则表达式对复杂字符串的支持不好（escape的处理）


    strWindowName = "测试 程序 空格.txt - 记事本"
    w = WindowMgr(strWindowName)
    w.set_foreground()
    exit()

    #w.find_window_via_wildcard(strWildCard)
    if w.is_window_exsiting() != True:
        return False

    GY_logging.debug("窗口初始尺寸坐标：" + str(w.get_rect()))
    GY_logging.debug("尝试把窗口移到最前...")
    w.set_foreground()

    if nWidth != 0 and nHeight != 0:
        w.resize_window(nWidth, nHeight, bResetIfNotFullyDisplay)

    GY_logging.debug("最终分辨率：" + str(w.get_rect()))
    OUT_lnLeftUpperPos[0] = w.get_rect()[0]
    OUT_lnLeftUpperPos[1] = w.get_rect()[1]

    time.sleep(1)
    exit()

def active_window_loose(strWindowName):
    top_windows = []
    win32gui.EnumWindows(_windowEnumerationHandler_callback, top_windows)
    for i in top_windows:
        if strWindowName in i[1].lower():
            win32gui.ShowWindow(i[0], 5)
            win32gui.SetForegroundWindow(i[0])
            break

def _windowEnumerationHandler_callback(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

def close_window(strWindowName):
    w = WindowMgr(strWindowName)
    return w.close_window()