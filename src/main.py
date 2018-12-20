#!/usr/bin/python3
import os
import sys
from cv2 import imread
import sklearn
import sklearn.neighbors.typedefs
import sklearn.neighbors.quad_tree
import sklearn.tree
import sklearn.tree._utils
from nilearn import plotting
from nilearn import image
from nilearn import datasets
from PIL import Image
from PyQt5 import uic
from PyQt5.QtCore import QPointF, QRegExp
from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsScene, QGraphicsView, QLabel, QListView, QMainWindow, \
    QSlider, QPushButton, QLineEdit, QCheckBox, QListWidget
from CursorGraphicsView import CursorGraphicsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindow.ui', self)

        self.action_Open.triggered.connect(self.open_file)
        _path = os.getcwd()
        self.roaming_path = os.path.join(_path, 'Roaming')
        if not os.path.isdir(self.roaming_path):
            os.mkdir(self.roaming_path)
        self.roaming_path += '\ '
        self.image_sliders = []
        self.image_viewers = []
        self.image_labels = []
        for i in range(3):
            self.image_sliders.append(self.findChildren(QSlider, QRegExp("image_slider_" + str(i)))[0])
            self.image_viewers.append(self.findChildren(QGraphicsView, QRegExp("image_viewer_" + str(i)))[0])
            self.image_labels.append(self.findChildren(QLabel, QRegExp("image_slice_label_" + str(i)))[0])
        # self.image_labels = self.findChildren(QLabel, QRegExp("image_slice_label_."))
        self.options_btn = self.findChildren(QPushButton, QRegExp("options_btn"))[0]
        self.options_btn.clicked.connect(self.option_change)
        self.html_2d_btn = self.findChildren(QPushButton, QRegExp("html_2d"))[0]
        self.html_2d_btn.clicked.connect(self.html_2d_change)
        self.html_3d_btn = self.findChildren(QPushButton, QRegExp("html_3d"))[0]
        self.html_3d_btn.clicked.connect(self.html_3d_change)

        self.threshold_line = self.findChildren(QLineEdit, QRegExp("threshold_line"))[0]
        self.threshold = float(self.threshold_line.text())

        self.contour_color_line = self.findChildren(QLineEdit, QRegExp("contour_color_line"))[0]
        self.contour_color = self.contour_color_line.text()

        self.dim_line = self.findChildren(QLineEdit, QRegExp("dim_line"))[0]
        self.dim = self.dim_line.text()

        self.black_bg_checkbox = self.findChildren(QCheckBox, QRegExp("black_checkbox"))[0]
        self.black_bg = self.black_bg_checkbox.isChecked()

        self.filled_checkbox = self.findChildren(QCheckBox, QRegExp("filled_checkbox"))[0]
        self.filled = self.filled_checkbox.isChecked()

        self.annotate_checkbox = self.findChildren(QCheckBox, QRegExp("annotate_checkbox"))[0]
        self.annotate = self.annotate_checkbox.isChecked()

        self.bg_list = self.findChildren(QListWidget, QRegExp("bg_list"))[0]
        self.bg_list_value = []
        self.bg_img = ""
        self.get_bg_list()

        self.setWindowTitle('Nii')
        self.show()
        # redraw viewers whenever a slider is moved
        for i in range(3):
            self.image_sliders[i].valueChanged.connect(lambda value, i=i: self.draw_viewer(i))

    def get_bg_list(self):
        self.bg_list_value = [i for i in os.listdir("canonical/")]
        if len(self.bg_list_value):
            self.bg_list.addItems(self.bg_list_value)
            self.bg_list.setCurrentRow(0)
            self.bg_img = self.bg_list_value[0]

    def html_3d_change(self):
        if not self.stat_img:
            return
        file_info = QFileDialog.getSaveFileName(parent=self, directory=os.path.expanduser('~'), filter='*.html')
        if len(file_info) == 1:
            return
        view = plotting.view_img_on_surf(self.stat_img, threshold=self.threshold, black_bg=self.black_bg, )
        view.save_as_html(file_info[0])

    def html_2d_change(self):
        if not self.stat_img:
            return
        file_info = QFileDialog.getSaveFileName(parent=self, directory=os.path.expanduser('~'), filter='*.html')
        if len(file_info) == 1:
            return
        view = plotting.view_img(self.stat_img, threshold=self.threshold,
                                 annotate=self.annotate,
                                 black_bg=self.black_bg, dim=self.dim)
        # view.open_in_browser()
        view.save_as_html(file_info[0])

    def option_change(self):
        print(self.bg_list.currentRow())
        # if not open
        if self.stat_img is None:
            return
        if not self.dim_line.text() == 'auto':
            self.dim = float(self.dim_line.text())
        self.filled = self.filled_checkbox.isChecked()
        self.black_bg = self.black_bg_checkbox.isChecked()
        self.contour_color = self.contour_color_line.text()
        self.threshold = float(self.threshold_line.text())
        self.annotate = self.annotate_checkbox.isChecked()
        self.bg_img = self.bg_list_value[self.bg_list.currentRow()]
        for i, viewer in enumerate(self.image_viewers):
            self.draw_viewer(i)

    def open_file(self):
        file_info = QFileDialog.getOpenFileName(parent=self, directory=os.path.expanduser('~'), filter='*.nii *.nii.gz')
        if not os.path.isfile(file_info[0]):
            return

        # menu buttons for saving and deleting points are enabled only once an image has been loaded

        for i, save_button in enumerate([self.action_Save_sagittal_slice,
                                         self.action_Save_coronal_slice,
                                         self.action_Save_transverse_slice]):
            save_button.triggered.connect(lambda value, i=i: self.save_slice(i))
        self.stat_img = image.load_img(file_info[0])
        file_name = file_info[0][file_info[0].rfind('/') + 1:file_info[0].find('.')]
        import time
        self.roaming_path += file_name + '_' + str(int(time.time()))
        data = self.stat_img
        self.num_image = 0
        # ‘x’ - sagittal, ‘y’ - coronal, ‘z’ - axial
        self.display = ['x', 'y', 'z']
        self.img_list = []
        self.offset = [abs(data.get_header()['qoffset_x']), abs(data.get_header()['qoffset_y']),
                       abs(data.get_header()['qoffset_z'])]

        # if the image is 4D, prepare the 4th image slider
        if len(data.shape) == 4:
            self.image_cycle_slider.setMaximum(data.shape[3] - 1)

        # ‘x’ - sagittal, ‘y’ - coronal, ‘z’ - axial
        for i, d in enumerate(self.image_sliders):
            d.setMaximum(self.offset[i] * 2 + 1)
            d.setValue(self.offset[i])

        # the custom viewers need some data to work properly, and need to draw the slices a first time once the image
        # has been loaded
        for i, viewer in enumerate(self.image_viewers):
            viewer.set_num(i)
            viewer.set_viewers(self.image_viewers)
            viewer.set_sliders(self.image_sliders)
            self.draw_viewer(i)

    def save_slice(self, num: int):
        file_info = QFileDialog.getSaveFileName(parent=self, directory=os.path.expanduser('~'), filter='*.png')

        if file_info[0] == '':
            return

        # python-pillow can load any kind of image and save it in any common format
        image = Image.fromqpixmap(self.image_viewers[num].scene().items()[-1].pixmap())
        image.save(file_info[0], 'PNG')

    def draw_viewer(self, num_slider: int):
        if self.stat_img is None:
            return
        data = self.stat_img.get_data()
        header = self.stat_img.get_header()

        if data is None or header is None:
            return

        # we need a 2D array from a 3D or 4D array to display as an image

        # the slice(None) index will take an entire dimension, so using 2 of them and a number will reduce the
        # dimensions of the original array by one if the image is 3D
        slice_range = [slice(None)] * 3
        slice_range[num_slider] = self.image_sliders[num_slider].value()
        slice_range = tuple(slice_range)
        d = self.display[num_slider]
        j = slice_range[num_slider] - self.offset[num_slider]
        self.image_labels[num_slider].setText(self.tr("Slice " + str(j)))
        file_path = self.roaming_path + '_' + d + '_' + str(j) + '_' + self.contour_color + '_' + str(
            self.threshold) + '_' + str(self.black_bg) + '_' + str(self.filled) + '_' + str(self.annotate) + "_"+self.bg_img+'.png'
        if file_path not in self.img_list:
            self.img_list.append(file_path)
            '''#enable non background picture view
            display = plotting.plot_anat(self.stat_img, display_mode=d,
                                             cut_coords=[j], black_bg=self.black_bg,
                                             dim=str(self.dim), annotate=self.annotate)
            '''
            display = plotting.plot_stat_map(self.stat_img, bg_img="canonical/"+self.bg_img, display_mode=d,
                                             cut_coords=[j], black_bg=self.black_bg,
                                             dim=str(self.dim), annotate=self.annotate)
            display.add_contours(self.stat_img, levels=[self.threshold], colors=self.contour_color,
                                 filled=self.filled, )
            display.savefig(file_path)
            display.close()
        # if the original image is 4D, we need to further reduce the number of dimensions by selecting a 3D image
        if len(data.shape) == 4:
            slice_range = slice_range + (self.num_image,)
        # after the 2D plane has been extracted, the contrast must be changed according to the contrast sliders' values
        plane = imread(file_path)

        converted = plane

        scales_indexes = [((x + num_slider) % 3) + 1 for x in [1, 2]]
        scale = QPointF(header['pixdim'][min(scales_indexes)], header['pixdim'][max(scales_indexes)])

        # the plane needs to be rotated in order to be properly displayed

        pixmap = Image.fromarray(converted).toqpixmap()
        scene = QGraphicsScene(0, 0, pixmap.width(), pixmap.height())

        scene.addPixmap(pixmap)
        self.image_viewers[num_slider].setScene(scene)
        self.image_viewers[num_slider].set_scale(scale)
        self.image_viewers[num_slider].make_cursor()

    def draw_viewers(self):
        for i in range(3):
            self.draw_viewer(i)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec())
