import joblib
import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# 加载数据
file_path = 'pedestrian_counts_dataset.csv'
data = pd.read_csv(file_path)

# 将数据转换为合适的格式
features = data.columns[2:]
X = []
y = []

for index, row in data.iterrows():
    for hour, count in enumerate(row[features]):
        X.append([hour])
        y.append(count)

X = np.array(X)
y = np.array(y)
# 标准化数据
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X = scaler_X.fit_transform(X)
y = y.reshape(-1, 1)
y = scaler_y.fit_transform(y).flatten()


joblib.dump(scaler_X, 'scaler_X.pkl')
joblib.dump(scaler_y, 'scaler_y.pkl')

# 转换为PyTorch的Tensor
X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32)

# 创建数据集和数据加载器
dataset = TensorDataset(X_tensor, y_tensor)
data_loader = DataLoader(dataset, batch_size=32, shuffle=True)

# 检查是否有可用的GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# 定义模型
class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(1, 64)
        self.bn1 = nn.BatchNorm1d(64)
        '''它通過對每一個小批量輸入進行標準化，從而幫助加速訓練過程，減少梯度消失問題，並且對初始化的敏感度較低。'''
        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.fc3 = nn.Linear(32, 1)

    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.fc3(x)
        return x


model = SimpleNN().to(device)
criterion = nn.MSELoss()#均方误差
optimizer = optim.SGD(model.parameters(), lr=0.0001)#随机梯度下降

# 训练模型
num_epochs = 200
losses = []

for epoch in range(num_epochs):
    epoch_loss = 0
    for batch_X, batch_y in data_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)

        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y.view(-1, 1))
        '''
             outputs = model(batch_X)                           预测              
             loss = criterion(outputs, batch_y.view(-1, 1))     求损失函数
        '''
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()

    epoch_loss /= len(data_loader)
    losses.append(epoch_loss)

    print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {epoch_loss:.4f}')

# 可视化训练过程
plt.plot(range(1, num_epochs + 1), losses, label='Training Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss over Epochs')
plt.legend()
plt.show()
plt.savefig('my_plot.png')
# 评估模型
model.eval()
with torch.no_grad():
    outputs = model(X_tensor.to(device))
    loss = criterion(outputs, y_tensor.view(-1, 1).to(device))
    print('Mean Squared Error:', loss.item())

# 保存模型
model_save_path = 'trained_model.pth'
torch.save(model.state_dict(), model_save_path)
print(f'Model saved to {model_save_path}')

# 做一些预测
predictions = model(X_tensor[:10].to(device)).detach()
print('Predictions:', scaler_y.inverse_transform(predictions.view(-1).cpu().numpy().reshape(-1, 1)).flatten())
print('Actual:', scaler_y.inverse_transform(y_tensor[:10].numpy().reshape(-1, 1)).flatten())



