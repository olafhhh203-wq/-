import os
from shutil import copy, rmtree
import random


def mk_file(file_path: str):
    if os.path.exists(file_path):
        # 如果文件夹存在，则先删除原文件夹在重新创建
        rmtree(file_path)
    os.makedirs(file_path)


def main():
    # 保证随机可复现
    random.seed(0)

    # 将数据集中10%的数据划分到验证集中
    split_rate = 0.1

    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置数据根目录
    data_root = os.path.join(current_dir, "data")
    if not os.path.exists(data_root):
        os.makedirs(data_root)
        
    # 原始图像路径
    origin_flower_path = os.path.join(data_root, "Train_images")
    print(f"正在处理数据，原始数据路径: {origin_flower_path}")
    
    if not os.path.exists(origin_flower_path):
        print(f"错误：原始数据目录 {origin_flower_path} 不存在！")
        print("请确保您的原始图像数据放在 data/Train_images 目录下")
        return

    # 获取所有类别文件夹
    flower_class = [cla for cla in os.listdir(origin_flower_path)
                    if os.path.isdir(os.path.join(origin_flower_path, cla))]

    # 建立保存训练集的文件夹
    train_root = os.path.join(data_root, "train")
    mk_file(train_root)
    for cla in flower_class:
        # 建立每个类别对应的文件夹
        mk_file(os.path.join(train_root, cla))

    # 建立保存验证集的文件夹
    val_root = os.path.join(data_root, "val")
    mk_file(val_root)
    for cla in flower_class:
        # 建立每个类别对应的文件夹
        mk_file(os.path.join(val_root, cla))

    # 建立保存测试集的文件夹
    tes_root = os.path.join(data_root, "tes")
    mk_file(tes_root)
    for cla in flower_class:
        # 建立每个类别对应的文件夹
        mk_file(os.path.join(tes_root, cla))

    for cla in flower_class:
        cla_path = os.path.join(origin_flower_path, cla)
        images = os.listdir(cla_path)
        num = len(images)
        
        for index, image in enumerate(images):
            try:
                if index < num * 0.7:
                    # 将分配至训练集中的文件复制到相应目录
                    image_path = os.path.join(cla_path, image)
                    new_path = os.path.join(train_root, cla, image)
                    copy(image_path, new_path)
                elif index >= num * 0.7 and index < num * 0.9:
                    # 将分配至验证集中的文件复制到相应目录
                    image_path = os.path.join(cla_path, image)
                    new_path = os.path.join(val_root, cla, image)
                    copy(image_path, new_path)
                else:
                    # 将分配至测试集中的文件复制到相应目录
                    image_path = os.path.join(cla_path, image)
                    new_path = os.path.join(tes_root, cla, image)
                    copy(image_path, new_path)
            except Exception as e:
                print(f"\n复制文件时出错: {e}")
                print(f"源文件: {image_path}")
                print(f"目标文件: {new_path}")
                continue

            print("\r[{}] 正在处理: [{}/{}]".format(cla, index + 1, num), end="")
        print()

    print("数据处理完成！")


if __name__ == '__main__':
    main()
