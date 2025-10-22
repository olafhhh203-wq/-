import glob
import cv2
import torch
from PIL import Image
from torchvision import transforms
import matplotlib.pyplot as plt
import json
import os
from model import model

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 读取大图进行检测
test_img_path = os.path.join(current_dir, "data/test/1.bmp")
if not os.path.exists(test_img_path):
    test_img_path = os.path.join(current_dir, "data/Img/1.bmp")

src = cv2.imread(test_img_path)
if src is None:
    raise FileNotFoundError(f"无法找到或读取图像文件: {test_img_path}")

src.shape
# src = img1[1000:7000,1000:7000]
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
ret, binary = cv2.threshold(gray, 39, 255, cv2.THRESH_BINARY_INV)
se = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3), (-1, -1))
binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, se)

binary = cv2.erode(binary,se,iterations=2)
binary = cv2.dilate(binary,se,iterations=3)
binary = cv2.dilate(binary,se,iterations=1)
binary = cv2.erode(binary,se,iterations=2)
binary = cv2.dilate(binary,se,iterations=1)

# 保存二值化图像到独立文件夹
binary_dir = os.path.join(current_dir, "data/binary")
os.makedirs(binary_dir, exist_ok=True)
binary_path = os.path.join(binary_dir, "binary.bmp")
cv2.imwrite(binary_path, binary)
print(f"二值化图像已保存到: {binary_path}")

contours, hierarchy = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
height, width = src.shape[:2]
rects = []
# 轮廓筛选
index = 1
for c in range(len(contours)):
    # 轮廓外接矩形
    x, y, w, h = cv2.boundingRect(contours[c])
    # 轮廓面积
    area = cv2.contourArea(contours[c])
    if h > (height//2):
        continue
    if area < 800:
        continue
    if area > 150000:
        continue
    if w/h > 3:
        continue
    if h/w >3:
        continue
    rects.append([x, y, w, h])
    # 保存检测到的区域
    detect_dir = os.path.join(current_dir, "data/detect")
    os.makedirs(detect_dir, exist_ok=True)
    recimg = src[y:y + h, x:x + w]
    cv2.imwrite(os.path.join(detect_dir, f"region_{index}.png"), recimg)
    index += 1

print(f"检测到 {len(rects)} 个可能的缺陷区域")

# 设置检测图像路径
image_path = os.path.join(current_dir, "data/detect")
filepath = glob.glob(os.path.join(image_path, "*.png"))
print(f"待分类的区域图像数量: {len(filepath)}")
filepath = sorted(filepath, key=os.path.getctime)

# 预处理 - 调整为EfficientNet的标准预处理
data_transform = transforms.Compose(
    [transforms.Resize((224, 224)),
     transforms.ToTensor(),
     transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))  # ImageNet标准化
    ])

# read class_indict
try:
    json_file = open(os.path.join(current_dir, 'class_indices.json'), 'r')
    class_indict = json.load(json_file)
except Exception as e:
    print(f"读取类别索引文件失败: {e}")
    exit(-1)

def predict_MN(file_path):
    img = Image.open(file_path)
    img = data_transform(img)
    img = torch.unsqueeze(img, dim=0)
    with torch.no_grad():
        result = model_instance(img)
        result = torch.squeeze(result)
        predict = torch.softmax(result, dim=0)
        predict_cla = torch.argmax(predict).numpy()
    return predict_cla, predict[predict_cla].item()

# 获取模型
model_instance = model()
model_weight_path = os.path.join(current_dir, "EfficientNet_self1.pth")
# 加载模型文件
model_instance.load_state_dict(torch.load(model_weight_path, map_location='cpu'))
# 关闭 Dropout
model_instance.eval()

defect_count = 0
for i in range(0, len(filepath)):
    predict_cla, prob = predict_MN(filepath[i])
    class_name = class_indict[str(predict_cla)]
    print(f"区域 {i+1}: 预测类别 = {class_name}, 置信度 = {prob:.4f}")
    
    # 如果是NG类别，在原图上标注
    if "NG" in class_name:
        defect_count += 1
        color = (0, 0, 255) if "5NG" in class_name else (0, 255, 0)  # 5NG红色，7NG绿色
        cv2.rectangle(src, (rects[i][0], rects[i][1]),
                     (rects[i][0] + rects[i][2], rects[i][1] + rects[i][3]), 
                     color, 2, 8, 0)

print(f"\n检测到 {defect_count} 个缺陷")

# 保存结果
output_dir = os.path.join(current_dir, "output")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "detection_result.png")
cv2.imwrite(output_path, src)
print(f"\n检测结果已保存到: {output_path}")
