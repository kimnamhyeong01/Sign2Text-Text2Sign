import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
from dataset import FullPoseDataset
from model import PoseFormer

# 설정
pose_dir = "E:/pose"
test_csv = os.path.join(pose_dir, "test_metadata.csv")
model_path = os.path.join(pose_dir, "pose_transformer_finetuned.pt")
BATCH_SIZE = 32
NUM_CLASSES = len(pd.read_csv(test_csv)['label'].unique())

# 데이터 로드
test_dataset = FullPoseDataset(test_csv, pose_dir)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# 모델 로드
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = PoseFormer(num_classes=NUM_CLASSES).to(device)
model.load_state_dict(torch.load(model_path))
model.eval()

# 테스트
all_preds, all_targets = [], []
with torch.no_grad():
    for x, y in test_loader:
        x, y = x.to(device), y.to(device)
        output = model(x)
        preds = torch.argmax(output, dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_targets.extend(y.cpu().numpy())

# 정확도 측정
test_acc = accuracy_score(all_targets, all_preds)
print(f"\n✅ Test Accuracy: {test_acc * 100:.2f}%")

