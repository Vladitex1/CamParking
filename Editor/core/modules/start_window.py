import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import os
import logic.file as file
import logic.camera_control as camera
import logic.visualizer as visualizer
import logic.detector as detector
import asyncio
import Editor.core.modules.constants as const
from datetime import date

FILE_TAG:str = "start"
FILE_TAG=FILE_TAG+"_"
WINDOW_LABEL = f"{FILE_TAG}main_window"
WINDOW_TAG = f"{FILE_TAG}main_window"

class program:
    def __init__(self):
        if not dpg.does_item_exist(WINDOW_TAG):
            with dpg.window(label=WINDOW_LABEL, tag=WINDOW_TAG,
                            no_title_bar=True, no_move=True, no_resize=True, no_collapse=True, no_close=True,
                            width=const.WINDOW_FULL_SIZE[0], height=const.WINDOW_FULL_SIZE[1]+const.MENU_BAR_HEIGHT,
                            pos=(0, const.MENU_BAR_HEIGHT)):

                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=int(const.WINDOW_FULL_SIZE[0] / 2 - 50))
                    dpg.add_text(f"Начало")

                dpg.add_separator()
                dpg.add_text("Управление")
                dpg.add_text("", wrap=0)

    def bup(self):
        print("буп")

    def get_tags(self=None):

        data: list = []
        data.append(WINDOW_TAG)
        #data.append(TOOLS_TAG)

        return data
