import GY_logging
import GY_WindowsOperation
import GY_CharRecog

import parameters
import hotkey_listener


if __name__ == '__main__':
    # 设置日志
    GY_logging.init(parameters.LOG_FILE_NAME, "debug")
    GY_logging.info("程序开始运行。")

    # 初始化字符识别引擎
    GY_CharRecog.init(parameters.VERIFIED_CHARRECOG_PATH, parameters.UNVERIFIED_CHARRECOG_PATH)

    # 调整窗口
    GY_logging.info("调整窗口。")
    objWindowMgr = GY_WindowsOperation.WindowMgr(parameters.GAME_WINDOW_NAME)
    if objWindowMgr.is_window_exsiting() == False:
        GY_logging.critical("找不到游戏窗口。")
        exit()

    objWindowMgr.set_window_position(parameters.GAME_RECT_LEFT, parameters.GAME_RECT_TOP,
                                     parameters.GAME_RECT_WIDTH, parameters.GAME_RECT_HEIGHT)

    hotkey_listener.init()