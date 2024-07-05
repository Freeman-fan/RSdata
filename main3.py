import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QFileDialog, QLabel, QGridLayout, \
    QMessageBox, QInputDialog, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np
from osgeo import gdal


# 主窗体
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('遥感影像处理')
        self.setGeometry(200, 200, 500, 1000)

        self.file_path = ''  # ENVI文件路径
        self.image = None  # 原始图像
        self.image_output = None  # 展示(保存)图像
        self.image_raw = None  # 指数图像(未二值化)
        self.t = 0  # 二值化阈值
        self.dataset = ''  # 数据集
        self.now_text = None
        self.NDVI_image = None
        self.NDBI_image = None
        self.MNDWI_image = None

        # 创建数据库连接
        self.conn = sqlite3.connect('results.db')
        self.cursor = self.conn.cursor()
        # 创建表
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS areas (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, area_km2 REAL)")

        self.file_textbox = QLineEdit('文件地址', self)
        self.browse_button = QPushButton('选择文件', self)
        self.NDVI_button = QPushButton('提取NDVI', self)
        self.NDBI_button = QPushButton('提取NDBI', self)
        self.MNDWI_button = QPushButton('提取NDWI', self)
        self.binarization_button = QPushButton('二值化', self)
        self.bina_label = QLabel('二值化阈值', self)
        self.bina_t_num_textbox = QLineEdit('参数', self)
        self.save_button = QPushButton('保存', self)
        self.area_label = QLineEdit('提取区域面积: 0 平方千米', self)
        self.image_label = QLabel(self)

        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.browse_button, 1, 0, 1, 2)
        self.browse_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_layout.addWidget(self.NDVI_button, 3, 0, 1, 2)
        self.NDVI_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_layout.addWidget(self.NDBI_button, 5, 0, 1, 2)
        self.NDBI_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_layout.addWidget(self.MNDWI_button, 7, 0, 1, 2)
        self.MNDWI_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_layout.addWidget(self.binarization_button, 9, 0, 1, 2)
        self.binarization_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_layout.addWidget(self.bina_label, 11, 0, 1, 1)
        self.grid_layout.addWidget(self.bina_t_num_textbox, 11, 1, 1, 1)
        self.grid_layout.addWidget(self.save_button, 12, 0, 1, 2)
        self.save_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_layout.addWidget(self.file_textbox, 13, 0, 1, 300)
        self.grid_layout.addWidget(self.area_label, 15, 0, 1, 300)
        self.grid_layout.addWidget(self.image_label, 0, 3, 13, 300)
        self.image_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.grid_layout)

        self.image_label.setScaledContents(True)
        self.image_label.setStyleSheet(
            "border: 2px solid black; background-color: #f0f0f0;")

        self.browse_button.clicked.connect(self.browse_files)
        self.NDVI_button.clicked.connect(self.get_NDVI)
        self.NDBI_button.clicked.connect(self.get_NDBI)
        self.MNDWI_button.clicked.connect(self.get_MNDWI)
        self.binarization_button.clicked.connect(self.get_binarization)
        self.save_button.clicked.connect(self.save_image)

    # 选择文件
    def browse_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter('ENVI影像 (*.dat);;所有格式 (*)')
        if file_dialog.exec_():
            self.file_path = file_dialog.selectedFiles()[0]
            self.file_textbox.setText(self.file_path)
            self.load_and_display_image()

    # 加载影像
    def load_and_display_image(self):
        self.dataset = gdal.Open(self.file_path)
        if self.dataset is None:
            QMessageBox.warning(self, '错误', '无法打开影像文件')
            return

        image_data = self.read_image_data(self.dataset)

        height, width, bands = image_data.shape
        if bands < 3:
            QMessageBox.warning(self, '错误', '影像波段数不足')
            return

        block_size = 1024  # 分块大小

        # 创建空白图像
        rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

        for row in range(0, height, block_size):
            for col in range(0, width, block_size):
                # 计算当前块的结束位置
                row_end = min(row + block_size, height)
                col_end = min(col + block_size, width)
                # 提取红、绿、蓝波段块
                red_band = image_data[row:row_end, col:col_end, 0]
                green_band = image_data[row:row_end, col:col_end, 1]
                blue_band = image_data[row:row_end, col:col_end, 2]
                # 计算每个波段的拉伸范围
                min_val_red = np.percentile(red_band, 5)
                max_val_red = np.percentile(red_band, 95)
                min_val_green = np.percentile(green_band, 5)
                max_val_green = np.percentile(green_band, 95)
                min_val_blue = np.percentile(blue_band, 5)
                max_val_blue = np.percentile(blue_band, 95)
                # 进行5%线性拉伸
                red_band_stretched = (red_band - min_val_red) * \
                    (255 / (max_val_red - min_val_red))
                green_band_stretched = (
                    green_band - min_val_green) * (255 / (max_val_green - min_val_green))
                blue_band_stretched = (
                    blue_band - min_val_blue) * (255 / (max_val_blue - min_val_blue))
                # 将像素值限制在0-255范围内
                red_band_stretched = np.clip(red_band_stretched, 0, 255)
                green_band_stretched = np.clip(green_band_stretched, 0, 255)
                blue_band_stretched = np.clip(blue_band_stretched, 0, 255)
                # 将块的结果放回到RGB图像中
                rgb_image[row:row_end, col:col_end, 0] = blue_band_stretched
                rgb_image[row:row_end, col:col_end, 1] = green_band_stretched
                rgb_image[row:row_end, col:col_end, 2] = red_band_stretched

        # 创建QImage对象并显示
        qimage = QImage(rgb_image.data, width, height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        # 缩放图像以适应label大小
        scaled_pixmap = pixmap.scaled(self.image_label.size(
        ), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)

        QMessageBox.information(self, '成功', '影像加载完成')

        self.dataset = None  # 关闭数据集

    # 读取影像
    def read_image_data(self, dataset):
        bands = dataset.RasterCount
        width = dataset.RasterXSize
        height = dataset.RasterYSize

        image_data = np.zeros((height, width, bands), dtype=np.float32)

        for i in range(bands):
            band = dataset.GetRasterBand(i + 1)
            data = band.ReadAsArray()
            image_data[:, :, i] = data
        return image_data

    # 显示影像
    def display_image(self, image):
        height, width = image.shape
        byte_per_pixel = image.dtype.itemsize
        q_image = QImage(image.data, width, height, width *
                         byte_per_pixel, QImage.Format_Indexed8)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), Qt.KeepAspectRatio)  # 缩放图像
        self.image_label.setPixmap(scaled_pixmap)

    # 提取NDVI及植被区域
    def get_NDVI(self):
        if self.file_path == '':
            QMessageBox.warning(self, '错误', '请选择影像文件')
            return
        try:
            self.image = None
            self.image_output = None
            self.image_raw = None
            self.now_text = 'NDVI'
            self.dataset = None
            self.dataset = gdal.Open(self.file_path)
            if self.dataset is None:
                QMessageBox.warning(self, '错误', '无法打开影像文件')
                return

            self.image = self.read_image_data(self.dataset)
            block_size = 10000  # 分块大小
            height, width, _ = self.image.shape
            image_output = np.zeros((height, width), dtype=np.uint8)
            for row in range(0, height, block_size):
                for col in range(0, width, block_size):
                    end_row = min(row + block_size, height)
                    end_col = min(col + block_size, width)
                    block = self.image[row:end_row, col:end_col, :]
                    nir_band = block[:, :, 3].astype(np.float32)  # 近红外波段索引为3
                    red_band = block[:, :, 2].astype(np.float32)  # 红光波段索引为2
                    ndvi = (nir_band - red_band) / (nir_band + red_band)
                    # 标准化
                    normalized = (ndvi - ndvi.min()) / \
                        (ndvi.max() - ndvi.min())
                    scaled = normalized * 255
                    scaled = scaled.astype(np.uint8)
                    image_output[row:end_row, col:end_col] = scaled
                    self.image_raw = ndvi
            self.image_output = image_output
            self.display_image(self.image_output)
            self.bina_t_num_textbox.setText('0.4')  # 设置默认阈值
            QMessageBox.information(self, '成功', 'NDVI提取完成')

            # 保存NDVI结果为TIFF文件
            output_file = 'NDVI_output.tiff'  # 输出文件路径
            driver = gdal.GetDriverByName('GTiff')  # 获取TIFF驱动程序
            output_dataset = driver.Create(
                output_file, width, height, 1, gdal.GDT_Float32)  # 创建输出数据集
            output_dataset.SetGeoTransform(self.dataset.GetGeoTransform())
            output_dataset.SetProjection(self.dataset.GetProjection())
            output_band = output_dataset.GetRasterBand(1)
            for row in range(0, height, block_size):
                for col in range(0, width, block_size):
                    end_row = min(row + block_size, height)
                    end_col = min(col + block_size, width)
                    block_ndvi = ndvi[row:end_row, col:end_col]
                    output_band.WriteArray(block_ndvi, col, row)
            output_band.FlushCache()
            self.dataset = None  # 关闭数据集
        except Exception as e:
            QMessageBox.warning(self, '错误', '发生错误: {}'.format(str(e)))

    # 提取NDBI及不透水区域
    def get_NDBI(self):
        if self.file_path == '':
            QMessageBox.warning(self, '错误', '请选择影像文件')
            return
        try:
            self.image = None
            self.image_output = None
            self.image_raw = None
            self.now_text = 'NDBI'
            self.dataset = None
            self.dataset = gdal.Open(self.file_path)
            if self.dataset is None:
                QMessageBox.warning(self, '错误', '无法打开影像文件')
                return
            self.image = self.read_image_data(self.dataset)
            block_size = 10000  # 分块大小
            height, width, _ = self.image.shape
            image_output = np.zeros((height, width), dtype=np.uint8)
            for row in range(0, height, block_size):
                for col in range(0, width, block_size):
                    end_row = min(row + block_size, height)
                    end_col = min(col + block_size, width)
                    block = self.image[row:end_row, col:end_col, :]
                    mir_band = block[:, :, 4].astype(np.float32)  # 短波红外波段索引为4
                    nir_band = block[:, :, 3].astype(np.float32)  # 近红外波段索引为3
                    ndbi = (mir_band - nir_band) / (mir_band + nir_band)
                    # 标准化
                    normalized = (ndbi - ndbi.min()) / (ndbi.max()-ndbi.min())
                    scaled = normalized * 255
                    scaled = scaled.astype(np.uint8)
                    image_output[row:end_row, col:end_col] = scaled
                    self.image_raw = ndbi
            self.image_output = image_output
            self.display_image(self.image_output)
            self.bina_t_num_textbox.setText('0.1')  # 设置默认阈值
            QMessageBox.information(self, '成功', 'NDBI提取完成')

            # 保存NDBI结果为TIFF文件
            output_file = 'NDBI_output.tiff'  # 输出文件路径
            driver = gdal.GetDriverByName('GTiff')  # 获取TIFF驱动程序
            output_dataset = driver.Create(
                output_file, width, height, 1, gdal.GDT_Float32)  # 创建输出数据集
            output_dataset.SetGeoTransform(self.dataset.GetGeoTransform())
            output_dataset.SetProjection(self.dataset.GetProjection())
            output_band = output_dataset.GetRasterBand(1)
            for row in range(0, height, block_size):
                for col in range(0, width, block_size):
                    end_row = min(row + block_size, height)
                    end_col = min(col + block_size, width)
                    block_ndbi = ndbi[row:end_row, col:end_col]
                    output_band.WriteArray(block_ndbi, col, row)
            output_band.FlushCache()
            self.dataset = None  # 关闭数据集
        except Exception as e:
            QMessageBox.warning(self, '错误', '发生错误: {}'.format(str(e)))

    # 提取MNDWI及水体区域
    def get_MNDWI(self):
        if self.file_path == '':
            QMessageBox.warning(self, '错误', '请选择影像文件')
            return
        try:
            self.image = None
            self.image_output = None
            self.image_raw = None
            self.now_text = 'MNDWI'
            self.dataset = None
            self.dataset = gdal.Open(self.file_path)
            if self.dataset is None:
                QMessageBox.warning(self, '错误', '无法打开影像文件')
                return
            self.image = self.read_image_data(self.dataset)
            block_size = 10000  # 分块大小
            height, width, _ = self.image.shape
            image_output = np.zeros((height, width), dtype=np.uint8)
            for row in range(0, height, block_size):
                for col in range(0, width, block_size):
                    end_row = min(row + block_size, height)
                    end_col = min(col + block_size, width)
                    block = self.image[row:end_row, col:end_col, :]
                    green_band = block[:, :, 1].astype(np.float32)  # 绿光波段索引为1
                    nir_band = block[:, :, 4].astype(np.float32)  # 短波红外波段索引为4
                    mndwi = (green_band - nir_band) / (green_band + nir_band)
                    # 标准化
                    normalized = (mndwi - mndwi.min()) / \
                        (mndwi.max()-mndwi.min())
                    scaled = normalized*255
                    scaled = scaled.astype(np.uint8)
                    image_output[row:end_row, col:end_col] = scaled
                    self.image_raw = mndwi
            self.image_output = image_output
            self.display_image(self.image_output)
            self.bina_t_num_textbox.setText('0.3')  # 设置默认阈值
            QMessageBox.information(self, '成功', 'MNDWI提取完成')

            # 保存MNDWI结果为TIFF文件
            output_file = 'MNDWI_output.tiff'  # 输出文件路径
            driver = gdal.GetDriverByName('GTiff')  # 获取TIFF驱动程序
            output_dataset = driver.Create(
                output_file, width, height, 1, gdal.GDT_Float32)  # 创建输出数据集
            output_dataset.SetGeoTransform(self.dataset.GetGeoTransform())
            output_dataset.SetProjection(self.dataset.GetProjection())
            output_band = output_dataset.GetRasterBand(1)
            for row in range(0, height, block_size):
                for col in range(0, width, block_size):
                    end_row = min(row + block_size, height)
                    end_col = min(col + block_size, width)
                    block_ndbi = mndwi[row:end_row, col:end_col]
                    output_band.WriteArray(block_ndbi, col, row)
            output_band.FlushCache()
            self.dataset = None  # 关闭数据集
        except Exception as e:
            QMessageBox.warning(self, '错误', '发生错误: {}'.format(str(e)))

    # 二值化计算
    def get_binarization(self):
        if self.file_path == '':
            QMessageBox.warning(self, '错误', '请选择影像文件')
            return
        try:
            image = self.image_raw
            t = self.t
            try:
                t_str = self.bina_t_num_textbox.text()
                t = float(t_str)
                print(t)
            except Exception:
                t = self.t
            image_mask = np.where(image > t, 255, 0).astype(np.uint8)
            self.image_output = image_mask
            self.display_image(self.image_output)

            # 计算区域面积
            num_pixels = np.count_nonzero(self.image_output)
            area = num_pixels * 900 / 1000000
            self.area_label.setText(f'{self.now_text}提取面积：{area} 平方千米')
            self.save_area_to_db('vegetation', area)
        except Exception as e:
            QMessageBox.warning(self, '错误', '发生错误: {}'.format(str(e)))
        pass

    # 保存
    def save_image(self):
        if self.image_label.pixmap() is not None:
            file_dialog = QFileDialog()
            file_dialog.setDefaultSuffix('.tiff')
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilter('TIFF Files (*.tiff)')

            if file_dialog.exec_():
                save_path = file_dialog.selectedFiles()[0]
                if save_path != '':
                    image_data = None
                    if self.NDVI_image is not None:
                        image_data = self.NDVI_image
                    elif self.MNDWI_image is not None:
                        image_data = self.MNDWI_image
                    elif self.NDBI_image is not None:
                        image_data = self.NDBI_image
                    elif self.image_output is not None:
                        image_data = self.image_output

                    if image_data is not None:
                        driver = gdal.GetDriverByName('GTiff')
                        height, width = image_data.shape
                        dataset = driver.Create(
                            save_path, width, height, 1, gdal.GDT_Byte)
                        dataset.GetRasterBand(1).WriteArray(image_data)
                        dataset.FlushCache()

                        QMessageBox.information(self, '成功', '图像保存成功')
                    else:
                        QMessageBox.warning(self, '错误', '没有可保存的图像')
        else:
            QMessageBox.warning(self, '错误', '没有可保存的图像')

    # 面积入库
    def save_area_to_db(self, category, area):
        self.cursor.execute(
            "INSERT INTO areas (category, area_km2) VALUES (?, ?)", (category, area))
        self.conn.commit()
        QMessageBox.information(self, '成功', '面积保存成功')


# 主程序入口
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
