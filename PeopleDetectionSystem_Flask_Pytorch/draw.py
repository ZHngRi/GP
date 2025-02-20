import torch
import torch.nn as nn
import torchviz

class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(1, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.fc3 = nn.Linear(32, 1)

    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.fc3(x)
        return x

model = SimpleNN()

# 使用更大的批量大小，例如10
x = torch.randn(10, 1)
y = model(x)

# 使用torchviz进行可视化
dot = torchviz.make_dot(y, params=dict(model.named_parameters()))
dot.format = 'png'
dot.render('simple_nn')
