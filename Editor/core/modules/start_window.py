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

WINDOW_NAME = "Начало"

def run():
    with dpg.window(label="Start Window", tag="start_window",
                    no_title_bar=True, no_move=True, no_resize=True, no_collapse=True, no_close=True,
                    width=const.MAIN_WIDTH, height=const.MAIN_HEIGHT,
                    pos=(const.MAIN_POS_X, const.MAIN_POS_Y)):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=int(const.TOOLS_WIDTH / 2 - 50))
                dpg.add_text("Полигоныasdasdasda")

            dpg.add_separator()

            dpg.add_text("Управление")
            dpg.add_text("", wrap=0)
            return WINDOW_NAME
