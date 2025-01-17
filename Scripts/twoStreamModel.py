import torch
from ML_DL_Project.Scripts.flow_resnet import *
from ML_DL_Project.Scripts.attentionModelLSTA import *
from ML_DL_Project.Scripts.objectAttentionModelConvLSTM import *
import torch.nn as nn


class twoStreamAttentionModel(nn.Module):
    def __init__(self, flowModel='', frameModel='', stackSize=5, memSize=512, num_classes=61, c_cam_classes=1000, LSTA=False):
        super(twoStreamAttentionModel, self).__init__()
        self.flowModel = flow_resnet34(False, channels=2*stackSize, num_classes=num_classes)
        if flowModel != '':
            self.flowModel.load_state_dict(torch.load(flowModel))

        if LSTA is True:
            self.frameModel = attentionModelLSTA(num_classes, memSize, c_cam_classes)
        else:
            self.frameModel = attentionModel(num_classes, memSize)
        
        if frameModel != '':
          self.frameModel.load_state_dict(torch.load(frameModel))

        self.fc2 = nn.Linear(512 * 2, num_classes, bias=True)
        self.dropout = nn.Dropout(0.5)
        self.classifier = nn.Sequential(self.dropout, self.fc2)

    def forward(self, inputVariableFlow, inputVariableFrame):
        _, flowFeats = self.flowModel(inputVariableFlow)
        _, rgbFeats = self.frameModel(inputVariableFrame)
        twoStreamFeats = torch.cat((flowFeats, rgbFeats), 1)
        return self.classifier(twoStreamFeats)