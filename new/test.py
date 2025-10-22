import torch
import torch.nn as nn
from torchvision import transforms, datasets
# import matplotlib.pyplot as plt
# import numpy as np
# import torch.optim as optim
from draw_matrix import plot_confusion_matrix

import os
from model import model

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 使用绝对路径确保能找到数据目录
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "data")

data_transform = transforms.Compose(
    [
        transforms.Resize([224, 224]),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))  # ImageNet标准化
    ])

test_dataset = datasets.ImageFolder(root=os.path.join(image_path, "tes"),
                                    transform=data_transform)

test_num = len(test_dataset)
print(test_num)
test_loader = torch.utils.data.DataLoader(test_dataset,  # 导入的训练集
                                          batch_size=1,  # 每批训练的样本数
                                          shuffle=True,  # 是否打乱训练集
                                          num_workers=0)  # 使用线程数，在windows下设置为0

# 获取模型
model_instance = model()

model_weight_path = os.path.join(current_dir, "EfficientNet_self1.pth")  # 使用绝对路径
# 加载模型文件
model_instance.load_state_dict(torch.load(model_weight_path, map_location='cpu'))

model_instance.eval()
acc = 0.0
predict_list = []
conf_matrix = torch.zeros(8, 8)  # 修改为8x8的混淆矩阵
# 更新混淆矩阵
def confusion_matrix(preds, labels, conf_matrix):
    conf_matrix[labels, preds] += 1
    return conf_matrix


with torch.no_grad():
    for test_data in test_loader:
        test_images, test_labels = test_data

        # 扩大维度

        output = torch.squeeze(model_instance(test_images))  # 将输出压缩，即压缩掉 batch 这个维度
        predict = torch.softmax(output, dim=0)
        predict_cla = torch.argmax(predict).numpy()
        print(str(predict_cla), (test_labels).item())
        #         if predict_cla==int((test_labels).item()):
        #             acc += 1
        conf_matrix = confusion_matrix(predict_cla, labels=test_labels, conf_matrix=conf_matrix)
        if predict_cla == int((test_labels).item()):
            acc += 1

test_accurate = acc / test_num

print(test_accurate)
print(conf_matrix)

attack_types = ['class1OK', 'class2OK', 'class3OK', 'class4OK', 'class5NG', 'class6OK', 'class7NG', 'class8OK']  # 更新类别标签
plot_confusion_matrix(conf_matrix.numpy(), classes=attack_types, normalize=True,
                                title='Normalized confusion matrix')


