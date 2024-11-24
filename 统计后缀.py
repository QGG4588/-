import os
import zipfile
import rarfile
import py7zr
import tarfile
from collections import Counter
from tkinter import Tk, filedialog, scrolledtext, Button, Label, messagebox


def count_file_extensions_in_folder(directory):
    """统计文件夹内文件的后缀数量。"""
    extension_counter = Counter()
    for root, _, files in os.walk(directory):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension:
                extension_counter[extension] += 1
            else:
                extension_counter["无后缀"] += 1
    return extension_counter


def count_extensions_in_compressed_files(directory):
    """统计文件夹内压缩包中的文件后缀数量。"""
    compressed_counter = Counter()

    def process_zip(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            for file in zip_file.namelist():
                if file.endswith('/'):
                    continue
                _, extension = os.path.splitext(file)
                compressed_counter[extension if extension else "无后缀"] += 1

    def process_rar(rar_path):
        with rarfile.RarFile(rar_path, 'r') as rar_file:
            for file in rar_file.namelist():
                if file.endswith('/'):
                    continue
                _, extension = os.path.splitext(file)
                compressed_counter[extension if extension else "无后缀"] += 1

    def process_7z(archive_path):
        with py7zr.SevenZipFile(archive_path, 'r') as archive:
            for file in archive.getnames():
                _, extension = os.path.splitext(file)
                compressed_counter[extension if extension else "无后缀"] += 1

    def process_tar(tar_path):
        with tarfile.open(tar_path, 'r') as tar_file:
            for member in tar_file.getmembers():
                if member.isdir():
                    continue
                _, extension = os.path.splitext(member.name)
                compressed_counter[extension if extension else "无后缀"] += 1

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.endswith('.zip'):
                    process_zip(file_path)
                elif file.endswith('.rar'):
                    process_rar(file_path)
                elif file.endswith('.7z'):
                    process_7z(file_path)
                elif file.endswith(('.tar', '.gz', '.bz2', '.xz')):
                    process_tar(file_path)
            except Exception:
                compressed_counter["损坏或无法处理的文件"] += 1

    return compressed_counter


def select_directory():
    """选择文件夹并统计后缀。"""
    directory = filedialog.askdirectory(title="选择一个文件夹")
    if directory:
        dir_path_label.config(text=f"统计目录：{directory}")
        global current_directory
        current_directory = directory

        # 显示文件夹内的文件后缀统计结果
        folder_results = count_file_extensions_in_folder(directory)
        display_results(folder_results, folder_result_text, "文件夹内文件后缀统计")

        # 统计并显示压缩包内文件后缀统计
        compressed_results = count_extensions_in_compressed_files(directory)
        display_results(compressed_results, compressed_result_text, "压缩包内文件后缀统计")

        # 合并文件夹内文件后缀与压缩包内的文件后缀，排除压缩包格式的后缀
        combined_results = combine_results(folder_results, compressed_results)
        display_results(combined_results, combined_result_text, "合并后缀统计")


def combine_results(folder_results, compressed_results):
    """将文件夹内后缀和压缩包内的文件后缀统计合并，排除压缩包格式。"""
    # 需要排除的压缩文件后缀
    compressed_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}

    # 合并文件夹内后缀和压缩包内文件后缀（排除压缩包格式）
    combined_counter = folder_results.copy()

    # 将压缩包内的后缀统计结果加到文件夹结果中
    for ext, count in compressed_results.items():
        if ext.lower() not in compressed_extensions:
            combined_counter[ext] += count

    # 计算总和并排除压缩包后缀的数量
    for ext in compressed_extensions:
        if ext in combined_counter:
            combined_counter[ext] -= combined_counter[ext]
            if combined_counter[ext] <= 0:
                del combined_counter[ext]

    return combined_counter


def display_results(results, text_widget, title):
    """在指定文本区域显示统计结果。"""
    text_widget.delete(1.0, "end")
    text_widget.insert("end", f"{title}：\n\n")
    if not results:
        text_widget.insert("end", "未找到文件或统计结果为空。\n")
        return
    for ext, count in results.items():
        text_widget.insert("end", f"{ext}: {count}\n")


# 初始化全局变量
current_directory = None

# 创建主窗口
root = Tk()
root.title("文件后缀统计工具")
root.geometry("800x700")

# 添加界面组件
dir_path_label = Label(root, text="选择一个文件夹进行统计：", wraplength=780)
dir_path_label.pack(pady=10)

Button(root, text="选择文件夹", command=select_directory).pack(pady=5)

# 文件夹内统计结果
folder_result_label = Label(root, text="文件夹内文件后缀统计结果：")
folder_result_label.pack(pady=5)
folder_result_text = scrolledtext.ScrolledText(root, width=90, height=12, wrap="word")
folder_result_text.pack(pady=5)

# 压缩包内统计结果
compressed_result_label = Label(root, text="压缩包内文件后缀统计结果：")
compressed_result_label.pack(pady=5)
compressed_result_text = scrolledtext.ScrolledText(root, width=90, height=12, wrap="word")
compressed_result_text.pack(pady=5)

# 合并统计结果
combined_result_label = Label(root, text="合并文件夹内及压缩包内文件后缀统计结果：")
combined_result_label.pack(pady=5)
combined_result_text = scrolledtext.ScrolledText(root, width=90, height=12, wrap="word")
combined_result_text.pack(pady=5)

# 启动主循环
root.mainloop()
