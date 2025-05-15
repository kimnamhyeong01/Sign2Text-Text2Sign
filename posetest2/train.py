import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import accuracy_score
from dataset import FullPoseDataset
from model import PoseFormer

# 설정
pose_dir = "E:/pose"
train_csv = os.path.join(pose_dir, "train_metadata.csv")
val_csv = os.path.join(pose_dir, "val_metadata.csv")
BATCH_SIZE = 32
EPOCHS = 150
LR = 1e-4
NUM_CLASSES = len(pd.read_csv(train_csv)['label'].unique())

# 데이터 로드
train_dataset = FullPoseDataset(train_csv, pose_dir)
val_dataset = FullPoseDataset(val_csv, pose_dir)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

# 모델
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = PoseFormer(num_classes=NUM_CLASSES).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=5, verbose=True)

# 학습
train_loss_list, val_loss_list = [], []
train_acc_list, val_acc_list = [], []
best_val_acc, best_epoch = 0, 0

for epoch in range(EPOCHS):
    model.train()
    total_loss, preds, targets = 0, [], []

    for x, y in train_loader:
        x, y = x.to(device), y.to(device)
        output = model(x)
        loss = criterion(output, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        preds.extend(torch.argmax(output, 1).cpu().numpy())
        targets.extend(y.cpu().numpy())

    train_loss_list.append(total_loss / len(train_loader))
    train_acc_list.append(accuracy_score(targets, preds))

    model.eval()
    val_loss, val_preds, val_targets = 0, [], []
    with torch.no_grad():
        for x, y in val_loader:
            x, y = x.to(device), y.to(device)
            output = model(x)
            loss = criterion(output, y)
            val_loss += loss.item()
            val_preds.extend(torch.argmax(output, 1).cpu().numpy())
            val_targets.extend(y.cpu().numpy())

    val_loss_list.append(val_loss / len(val_loader))
    val_acc_list.append(accuracy_score(val_targets, val_preds))
    scheduler.step(val_acc_list[-1])

    if val_acc_list[-1] > best_val_acc:
        best_val_acc = val_acc_list[-1]
        best_epoch = epoch + 1
        torch.save(model.state_dict(), "E:/pose/pose_transformer_full.pt")

    print(f"[{epoch+1}/{EPOCHS}] Train Loss: {train_loss_list[-1]:.4f}, Acc: {train_acc_list[-1]:.4f} | Val Loss: {val_loss_list[-1]:.4f}, Acc: {val_acc_list[-1]:.4f}")

# 시각화
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(train_loss_list, label="Train Loss")
plt.plot(val_loss_list, label="Val Loss")
plt.xlabel("Epoch"); plt.ylabel("Loss"); plt.legend()
plt.title("Loss per Epoch")

plt.subplot(1, 2, 2)
plt.plot(train_acc_list, label="Train Acc")
plt.plot(val_acc_list, label="Val Acc")
plt.xlabel("Epoch"); plt.ylabel("Accuracy"); plt.legend()
plt.title("Accuracy per Epoch")

plt.tight_layout()
plt.savefig("E:/pose/fullkeypoint_training_plot.png")
plt.show()

print(f"\n🎯 Best Validation Accuracy: {best_val_acc:.4f} at Epoch {best_epoch}")
print("✅ Best Transformer model saved to: E:/pose/pose_transformer_full.pt")
