import rasterio
from matplotlib import pyplot as plt
import numpy as np
import rasterio
from rasterio.plot import show
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


# 读入envi图像
# 输入：文件路径file_path
# 输出：包含各波段值的数组band_group
def open_envi(file_path=""):
    if file_path == "":
        return -1
    if not os.path.isfile(file_path):
        return -1
    band_index = 0
    with rasterio.open(file_path) as file:
        while True:
            band_index += 1
            try:
                band_group.append(file.read(band_index).astype(np.float16))
            except IndexError:
                break
    return band_group


# 两波段的提取运算
# 输入：两个波段值为b1，b2
# 输出：运算结果的图像output
def band_math1(b1, b2):
    output = (b1 - b2) / (b1 + b2)

    return output


# 创建主窗体
def create_main_window():

    def open_file_dialog():  # 按钮事件：打开文件
        global band_group
        filepath = tk.filedialog.askopenfilename()
        if filepath:
            entry_var.set(filepath)
            file_path = filepath
        try:
            band_group = open_envi(file_path=filepath)
            status_label.config(text="文件已加载，共" + str(len(band_group)) + "波段")
        except Exception as e:
            messagebox.showerror("错误", e)
            status_label.config(text="错误：文件路径有误或不是envi文件")
            file_path = ''

    def calculate_ndvi():  # 按钮事件：NDVI计算
        # 初始化变量
        global band_group
        global output_photo
        output_photo = None
        # 运算
        band1 = band_group[4]
        band2 = band_group[3]
        try:
            data = band_math1(b1=band1, b2=band2)
            output_photo = np.where(data > -0.3, 1, 0)
            status_label.config(text="NDVI运算完成")
            return
        except Exception as e:
            messagebox.showerror("Unknown Error", e)
            status_label.config(text="出现未知错误")

    def calculate_ndbi():  # 按钮事件：NDBI计算
        # 初始化变量
        global band_group
        global output_photo
        output_photo = None
        # 运算
        band1 = band_group[5]
        band2 = band_group[4]
        try:
            data = band_math1(b1=band1, b2=band2)
            output_photo = np.where(data > -0.3, 1, 0)
            status_label.config(text="NDBI运算完成")
        except Exception as e:
            messagebox.showerror("Unknown Error", e)
            status_label.config(text="出现未知错误")

    def calculate_mndwi():  # 按钮事件：MNDWI计算
        # 初始化变量
        global band_group
        global output_photo
        output_photo = None
        # 运算
        band1 = band_group[2]
        band2 = band_group[5]
        try:
            data = band_math1(b1=band1, b2=band2)
            output_photo = np.where(data > 0.3, 1, 0)
            status_label.config(text="MNDWI运算完成")
        except Exception as e:
            messagebox.showerror("Unknown Error", e)
            status_label.config(text="出现未知错误")

    def show_image():  # 按钮事件：显示图像
        global output_photo
        show(output_photo, cmap='gray')  # 使用适合NDVI的色图

    def show_status(message):  # 控件事件：更新状态标签文本
        status_label.config(text=message)

    # 创建主窗体
    main_window = tk.Tk()
    main_window.title("遥感图像处理")

    # 创建文本框变量
    entry_var = tk.StringVar()

    # 创建文本框和按钮
    entry = tk.Entry(main_window, textvariable=entry_var, width=50)
    entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    browse_button = tk.Button(
        main_window, text="选择输入文件", command=open_file_dialog)
    browse_button.grid(row=0, column=1, padx=5, pady=5)

    # 创建一个Frame来放置四个按钮
    button_frame = tk.Frame(main_window)
    button_frame.grid(row=1, column=0, columnspan=2, pady=5)

    # 创建按钮
    button_width = 12  # 按钮宽度
    calculate_ndvi_button = tk.Button(
        button_frame, text="NDVI计算", command=calculate_ndvi, width=button_width)
    calculate_ndvi_button.pack(side=tk.LEFT, padx=2)

    calculate_ndbi_button = tk.Button(
        button_frame, text="NDBI计算", command=calculate_ndbi, width=button_width)
    calculate_ndbi_button.pack(side=tk.LEFT, padx=2)

    calculate_mndwi_button = tk.Button(
        button_frame, text="MNDWI计算", command=calculate_mndwi, width=button_width)
    calculate_mndwi_button.pack(side=tk.LEFT, padx=2)

    show_image_button = tk.Button(
        button_frame, text="显示图像", command=show_image, width=button_width)
    show_image_button.pack(side=tk.LEFT, padx=2)

    # 创建状态标签
    status_label = tk.Label(main_window, text="")
    status_label.grid(row=2, column=0, columnspan=2, pady=5)

    return main_window


# 主程序
def main():
    # 创建窗体
    main_window = create_main_window()
    main_window.mainloop()


# 程序入口
if __name__ == "__main__":
    # 全局变量
    file_path = ''
    band_group = []
    output_photo = None

    # 启动主程序
    main()
