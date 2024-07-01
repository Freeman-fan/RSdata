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
# 输入：文件路径
# 输出：包含各波段值的数组
def open_envi(file_path=""):
    band_group = []
    if file_path == "":
        return -1
    if not os.path.isfile(file_path):
        return -1
    band_index = 0
    with rasterio.open(file_path) as file:
        while True:
            band_index += 1
            try:
                band_group.append(file.read(band_index))
            except IndexError:
                break

    return band_group


# 两波段的提取运算
# 输入：两个波段值为b1，b2
# 输出：运算结果的图像
def band_math1(b1, b2):
    output = (b1 - b2) / (b1 + b2)
    return output


# 创建主窗体
def create_main_window():
    # 按钮事件：打开文件
    def open_file_dialog():
        filepath = filedialog.askopenfilename()
        if filepath:
            entry_var.set(filepath)
            status_label.config(text="文件已选择: " + filepath)

    # 按钮事件：NDVI计算
    def calculate_ndvi():
        pass

    # 按钮事件：NDBI计算
    def calculate_ndbi():
        pass

    # 按钮事件：MNDWI计算
    def calculate_mndwi():
        pass

    # 按钮事件：显示图像
    def show_image(image_data):
        pass

    # 控件事件：更新状态标签文本
    def show_status(message):
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
    main_window = create_main_window()
    main_window.mainloop()
    


# 程序入口
if __name__ == "__main__":
    main()
