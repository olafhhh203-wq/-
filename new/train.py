import torch
import torch.nn as nn
from torchvision import transforms, datasets, utils
import matplotlib.pyplot as plt
import numpy as np
import torch.optim as optim

import os
import json
import time

from model import model, get_model_summary

# 使用GPU训练
device = torch.device("cpu")  # 改为使用CPU
with open(os.path.join("train.log"), "a") as log:
    log.write(str(device) + "\n")

# 数据预处理 - 调整为EfficientNet的标准预处理
data_transform = {
    "train": transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.RandomHorizontalFlip(p=0.5),  # 水平方向随机翻转，概率为 0.5
        transforms.RandomVerticalFlip(p=0.5),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))  # ImageNet标准化
    ]),

    "val": transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))  # ImageNet标准化
    ])
}

image_path = os.path.join(os.path.dirname(__file__), "data")
# 导入训练集并进行预处理
train_dataset = datasets.ImageFolder(root=image_path + "/train",
                                     transform=data_transform["train"])
train_num = len(train_dataset)
print(train_num)
# 按batch_size分批次加载训练集
train_loader = torch.utils.data.DataLoader(train_dataset,  # 导入的训练集
                                           batch_size=16,  # 每批训练的样本数
                                           shuffle=True,  # 是否打乱训练集
                                           num_workers=0)  # 使用线程数，在windows下设置为0

# 导入、加载 验证集
# 导入验证集并进行预处理
validate_dataset = datasets.ImageFolder(root=image_path + "/val",
                                        transform=data_transform["val"])
val_num = len(validate_dataset)
print(val_num)
# 加载验证集
validate_loader = torch.utils.data.DataLoader(validate_dataset,  # 导入的验证集
                                              batch_size=16,
                                              shuffle=True,
                                              num_workers=0)

lm_list = train_dataset.class_to_idx

cla_dict = dict((val, key) for key, val in lm_list.items())

json_str = json.dumps(cla_dict, indent=4)
with open('class_indices.json', 'w') as json_file:
    json_file.write(json_str)

# 获取模型
net = model()

# 打印模型信息
model_info = get_model_summary()
print(f"模型: {model_info['model_name']}")
print(f"总参数: {model_info['total_parameters']:,}")
print(f"可训练参数: {model_info['trainable_parameters']:,}")

net.to(device)  # 分配网络到指定的设备（GPU/CPU）训练

loss_function = nn.CrossEntropyLoss()  # 交叉熵损失
optimizer = optim.Adam(net.parameters(), lr=0.0001)  # 优化器（训练参数，学习率）

save_path = './EfficientNet_self1.pth'
best_acc = 0.0
acc_tra = []
acc_val = []
loss_tra = []
loss_val = []

epoch_num = 20

for epoch in range(epoch_num):
    net.train()  # 训练过程中开启 Dropout
    train_loss = 0.0  # 每个 epoch 都会对 running_loss  清零
    time_start = time.perf_counter()  # 对训练一个 epoch 计时

    acc_train = 0.0

    for step, data in enumerate(train_loader, start=0):  # 遍历训练集，step从0开始计算
        images, labels = data  # 获取训练集的图像和标签
        optimizer.zero_grad()  # 清除历史梯度

        outputs = net(images.to(device))  # 正向传播
        loss = loss_function(outputs, labels.to(device))  # 计算损失
        loss.backward()  # 反向传播
        optimizer.step()  # 优化器更新参数
        train_loss += loss.item()

        # 打印训练进度（使训练过程可视化）
        rate = (step + 1) / len(train_loader)  # 当前进度 = 当前step / 训练一轮epoch所需总step
        a = "*" * int(rate * 50)
        b = "." * int((1 - rate) * 50)
        #         with open(os.path.join("train.log"), "a") as log:     #写入日志
        #               log.write(str("\rtrain loss: {:^3.0f}%[{}->{}]{:.3f}".format(int(rate * 100), a, b, loss))+"\n")
        print("\rtrain loss: {:^3.0f}%[{}->{}]{:.3f}".format(int(rate * 100), a, b, loss), end="")
    print()
    with open(os.path.join("train.log"), "a") as log:
        log.write(str('%f s' % (time.perf_counter() - time_start)) + "\n")
    print('%f s' % (time.perf_counter() - time_start))

    val_loss = 0.0
    for step1, val_data in enumerate(validate_loader, start=0):
        val_images, val_labels = val_data
        outputs = net(val_images.to(device))
        loss1 = loss_function(outputs, val_labels.to(device))  # 计算损失
        val_loss += loss1.item()

    net.eval()  # 验证过程中关闭 Dropout
    acc = 0.0
    acc1 = 0.0

    with torch.no_grad():
        for step1, val_data in enumerate(validate_loader, start=0):
            val_images, val_labels = val_data
            outputs = net(val_images.to(device))
            #             loss1 = loss_function(outputs, val_labels.to(device))    # 计算损失
            #             val_loss += loss1.item()

            predict_y = torch.max(outputs, dim=1)[1]  # 以output中值最大位置对应的索引（标签）作为预测输出
            acc += (predict_y == val_labels.to(device)).sum().item()
        val_accurate = acc / val_num

        for train_data in train_loader:
            train_images, train_labels = train_data
            outputs = net(train_images.to(device))
            predict_y = torch.max(outputs, dim=1)[1]  # 以output中值最大位置对应的索引（标签）作为预测输出
            acc1 += (predict_y == train_labels.to(device)).sum().item()
        train_accurate = acc1 / train_num

        print('[epoch %d]  train_accuracy: %.3f \n' %
              (epoch + 1, train_accurate))

        # 保存准确率最高的那次网络参数
        if val_accurate > best_acc:
            best_acc = val_accurate
            torch.save(net.state_dict(), save_path)
        #         with open(os.path.join("train.log"), "a") as log:
        #               log.write(str('[epoch %d] train_loss: %.3f  test_accuracy: %.3f \n' %
        #               (epoch + 1, train_loss / step, val_accurate))+"\n")
        print('[epoch %d] train_loss: %.3f  val_accuracy: %.3f  val_loss: %.3f\n' %
              (epoch + 1, train_loss / step, val_accurate, val_loss / step1))

        loss_tra.append(train_loss / step)
        loss_val.append(val_loss / step1)
        acc_tra.append(train_accurate)
        acc_val.append(val_accurate)

with open(os.path.join("train.log"), "a") as log:
    log.write(str('Finished Training') + "\n")
print('Finished Training')
print('best_val_acc: %.3f' % (best_acc))

x1 = range(0, epoch_num)
plt.subplot(221)
plt.plot(x1, acc_tra, "b")
plt.plot(x1, acc_val)
plt.legend(['tra_acc', 'val_acc'])
plt.title("acc vs epoch")
plt.ylabel("acc")
plt.show()
x2 = range(0, epoch_num)
plt.subplot(222)
plt.plot(x2, loss_tra, "b")
plt.plot(x2, loss_val)
plt.legend(['tra_loss', 'val_loss'])
plt.title("loss vs epoch")
plt.ylabel("loss")
plt.show()

