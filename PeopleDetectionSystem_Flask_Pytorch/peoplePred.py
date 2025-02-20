import torch
import torch.nn as nn
import numpy as np
import joblib

# 定义模型架构（与训练时一致）
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

# 封装为函数
def load_and_predict(model_path, scaler_X_path, scaler_y_path, data):
    # 加载模型
    model = SimpleNN()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # 检查是否有可用的GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # 加载标准化器
    scaler_X = joblib.load(scaler_X_path)
    scaler_Y = joblib.load(scaler_y_path)

    X = scaler_X.transform(np.array(data).reshape(-1, 1))

    X_tensor = torch.tensor(X, dtype=torch.float32).to(device)
    with torch.no_grad():
        prediction = model(X_tensor).cpu().numpy()

    prediction = scaler_X.inverse_transform(prediction)
    prediction[:6] = 0
    prediction[-2:] = 0
    prediction = np.abs(prediction)
    prediction = np.ceil(prediction)

    return prediction.flatten()


if __name__ == '__main__':

    # 使用封装的函数进行预测
    model_path = 'my_weight/trained_model_Berlin.pth'
    scaler_X_path = 'my_weight/scaler_X.pkl'
    scaler_y_path = 'my_weight/scaler_y.pkl'

    # 准备输入数据
    data = [0, 0, 0, 0, 0, 0, 3000, 305, 400, 405, 500, 550, 600, 650, 700, 705, 8080, 8005, 890, 885, 1800, 1805, 0, 0]

    # 进行预测
    predictions = load_and_predict(model_path, scaler_X_path, scaler_y_path, data)

    # 输出预测结果
    print('Predicted count for each hour:', predictions)
