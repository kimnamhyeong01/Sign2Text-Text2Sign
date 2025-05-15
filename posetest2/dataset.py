import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
import os

class FullPoseDataset(Dataset):
    def __init__(self, csv_path, pose_dir):
        self.data = pd.read_csv(csv_path)
        self.pose_dir = pose_dir

    def normalize_pose(self, pose):
        mean = pose.mean(axis=(0, 1), keepdims=True)
        std = pose.std(axis=(0, 1), keepdims=True) + 1e-6
        return (pose - mean) / std

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        npy_path = os.path.join(self.pose_dir, f"{int(row['번호'])}.npy")
        pose = np.load(npy_path).astype(np.float32)  # (30, 66, 2)
        pose = pose.reshape(30, -1)  # (30, 132)
        pose = self.normalize_pose(pose)
        label = int(row['label'])
        return torch.tensor(pose), label
