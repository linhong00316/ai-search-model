from __future__ import print_function, division
import torch
import torch.nn as nn
from torch.autograd import Variable
import torchvision.models as models
import torch.nn.functional as F
import torch.nn as nn
import torch.utils.model_zoo as model_zoo

from .apply_model import new_structure_2,SpatialAttention,ChannelAttention


model_pretrained_path = {
    'resnet18': '/home/czd-2019/model_pretrained/resnet18-5c106cde.pth',
    'resnet34': "/home/czd-2019/model_pretrained/resnet34-333f7ec4.pth",
    'googlenet': "/home/czd-2019/model_pretrained/inception_v3_google-1a9a5a14.pth"
}

class StructureCheck(nn.Module):
    '''
    Just for test.
    '''

    def __init__(self,isPretrained=False):
        super(StructureCheck, self).__init__()
        self.net = new_structure_2()
        # self.net = nn.Sequential(*list(self.net.children())[:-2])

        if isPretrained:
            init_pretrained_weights(self.net, model_pretrained_path['resnet18'])

        # self.subTask = SubStructureCheck(10)

        # #for the first exp of structure2 with 640 dims output.
        # self.HairPart = SubStructureCheck(10,input_dims=640)
        # self.EyesPart = SubStructureCheck(5,input_dims=640)
        # self.NosePart = SubStructureCheck(2,input_dims=640)
        # self.CheekPart = SubStructureCheck(4,input_dims=640)
        # self.MouthPart = SubStructureCheck(5,input_dims=640)
        # self.ChinPart = SubStructureCheck(3,input_dims=640)
        # self.NeckPart = SubStructureCheck(2,input_dims=640)
        # self.HolisticPart = SubStructureCheck(9,input_dims=640)

        self.HairPart = SubStructureCheck(10)
        self.EyesPart = SubStructureCheck(5)
        self.NosePart = SubStructureCheck(2)
        self.CheekPart = SubStructureCheck(4)
        self.MouthPart = SubStructureCheck(5)
        self.ChinPart = SubStructureCheck(3)
        self.NeckPart = SubStructureCheck(2)
        self.HolisticPart = SubStructureCheck(9)

    def forward(self, x):
        x = self.net(x)
        hair = self.HairPart(x)
        eyes = self.EyesPart(x)
        nose = self.NosePart(x)
        cheek = self.CheekPart(x)
        mouth = self.MouthPart(x)
        chin = self.ChinPart(x)
        neck = self.NeckPart(x)
        holistic = self.HolisticPart(x)

        return hair, eyes, nose, cheek, mouth, chin, neck, holistic

class SubStructureCheck(nn.Module):
    def __init__(self,output_dims,input_dims=512):
        super(SubStructureCheck, self).__init__()
        self.ca = ChannelAttention(input_dims)
        self.sa = SpatialAttention(3)
        self.relu = nn.ReLU(inplace=True)
        self.aap = nn.AdaptiveAvgPool2d((1,1))

        self.fc = nn.Sequential(
            nn.Linear(input_dims, 512),
            nn.ReLU(True),
            nn.Dropout(p=0.5),
            nn.Linear(512, 128),
            nn.ReLU(True),
            nn.Dropout(p=0.5),
            nn.Linear(128, output_dims),
        )


    def forward(self, x):
        residual = x

        x = self.ca(x)*x
        x = self.sa(x)*x

        x += residual
        x = self.relu(x)
        x = self.aap(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)


        return x


def init_pretrained_weights(model, pretrain_dict_path):
    """
    Initialize model with pretrained weights.
    Layers that don't match with pretrained layers in name or size are kept unchanged.
    """
    pretrain_dict = torch.load(pretrain_dict_path)
    model_dict = model.state_dict()
    pretrain_dict = {k: v for k, v in pretrain_dict.items() if k in model_dict and model_dict[k].size() == v.size()}
    model_dict.update(pretrain_dict)
    model.load_state_dict(model_dict)
    print("Initialized model with pretrained weights from {}".format(pretrain_dict_path))
