import cv2
import numpy as np

from PySide6.QtWidgets import QLabel, QFileDialog
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt


class ImageView(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("Открой изображение")
        self.setStyleSheet("background: #222; color: #aaa;")

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "", "Images (*.png *.jpg *.bmp)"
        )
        if path:
            img = cv2.imread(path)
            self.show_image(img)

    def show_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w

        qimg = QImage(
            img.data, w, h, bytes_per_line, QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qimg)
        self.setPixmap(pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def resizeEvent(self, event):
        if self.pixmap():
            self.setPixmap(self.pixmap().scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
