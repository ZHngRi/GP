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
file_path = 'rearranged_data.csv'
data = pd.read_csv(file_path)

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