import torch
import torch.nn as nn
import torchvision.models as models

def model():
    """
    创建EfficientNet模型用于锂电池隔膜缺陷检测
    返回修改后的EfficientNet模型，输出8个类别
    """
    # 加载预训练的EfficientNet-B0，使用新的weights参数
    efficientnet = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    
    # 冻结特征提取层参数
    for param in efficientnet.parameters():
        param.requires_grad = False

    # 修改分类器以适应我们的任务
    # EfficientNet的最后一层是classifier，输入特征维度是1280
    efficientnet.classifier = nn.Sequential(
        nn.Dropout(p=0.2, inplace=False),  # 改为inplace=False
        nn.Linear(1280, 512),
        nn.ReLU(inplace=False),  # 改为inplace=False
        nn.Dropout(p=0.2, inplace=False),  # 改为inplace=False
        nn.Linear(512, 256),
        nn.ReLU(inplace=False),  # 改为inplace=False
        nn.Linear(256, 8),  # 8个输出类别
    )
    
    return efficientnet

def get_model_summary():
    """获取模型结构摘要"""
    model_instance = model()
    total_params = sum(p.numel() for p in model_instance.parameters())
    trainable_params = sum(p.numel() for p in model_instance.parameters() if p.requires_grad)
    
    return {
        'model_name': 'EfficientNet-B0',
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'input_size': (3, 224, 224),
        'output_classes': 8
    }