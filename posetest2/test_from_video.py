import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import mediapipe as mp
import json
from posetest2.model import PoseFormer

# 📘 라벨 매핑 불러오기
with open("C:/Users/유준혁/PycharmProjects/pose_transformer_finetuning/posetest2/index_to_word.json", "r", encoding="utf-8") as f:
    index_to_word = json.load(f)

# 🧠 모델 로드
model = PoseFormer()
model.load_state_dict(torch.load("C:/Users/유준혁/PycharmProjects/pose_transformer_finetuning/posetest2/pose_transformer_finetuning.pt", map_location='cpu'))
model.eval()

# 🎯 Mediapipe 설정
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
pose = mp_pose.Pose(static_image_mode=False)
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)

TARGET_FRAMES = 30
TOTAL_KEYPOINTS = 66

# ✅ Normalize 함수 추가 (학습과 동일하게!)
def normalize_pose(pose):  # pose: (30, 132)
    mean = pose.mean(axis=(0, 1), keepdims=True)
    std = pose.std(axis=(0, 1), keepdims=True) + 1e-6
    return (pose - mean) / std

# ✅ keypoint 추출
def extract_pose_from_video(video_path):
    def extract_landmarks(results_pose, results_hands):
        keypoints = []
        if results_pose.pose_landmarks:
            keypoints.extend([[l.x, l.y] for i, l in enumerate(results_pose.pose_landmarks.landmark) if i <= 23])
        else:
            keypoints.extend([[0.0, 0.0]] * 24)

        lh, rh = [[0.0, 0.0]] * 21, [[0.0, 0.0]] * 21
        if results_hands.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
                label = handedness.classification[0].label
                if label == 'Left':
                    lh = [[l.x, l.y] for l in hand_landmarks.landmark]
                elif label == 'Right':
                    rh = [[l.x, l.y] for l in hand_landmarks.landmark]
        keypoints.extend(lh + rh)
        return keypoints

    def sample_or_pad_sequence(seq, target_len):
        n = len(seq)
        if n == 0:
            return np.zeros((target_len, TOTAL_KEYPOINTS, 2))
        if n == target_len:
            return np.array(seq)
        elif n > target_len:
            idxs = np.linspace(0, n - 1, target_len).astype(int)
            return np.array([seq[i] for i in idxs])
        else:
            pad_len = target_len - n
            return np.array(seq + [seq[-1]] * pad_len)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"❌ 영상 열기 실패: {video_path}")

    frame_keypoints = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_pose = pose.process(frame_rgb)
        results_hands = hands.process(frame_rgb)
        keypoints = extract_landmarks(results_pose, results_hands)
        frame_keypoints.append(keypoints)

    cap.release()
    if not frame_keypoints:
        raise ValueError("❌ 유효한 keypoint를 추출하지 못했습니다.")

    return sample_or_pad_sequence(frame_keypoints, TARGET_FRAMES)

# ✅ 예측 함수
def predict_sign_from_video(video_path, save_npy_path=None):
    print(f"\n🎥 입력 영상: {video_path}")
    
    # 1. Keypoint 추출 및 reshape + normalize
    keypoints = extract_pose_from_video(video_path)      # (30, 66, 2)
    keypoints = keypoints.reshape(30, -1)                # (30, 132)
    keypoints = normalize_pose(keypoints)                # 정규화 추가!!

    # 2. 저장 (선택)
    if save_npy_path:
        np.save(save_npy_path, keypoints.reshape(30, 66, 2))  # 저장 시 다시 (30, 66, 2)
        print(f"💾 NPY 저장 완료: {save_npy_path}")

    # 3. 예측
    tensor_input = torch.tensor(keypoints, dtype=torch.float32).view(1, 30, -1)
    with torch.no_grad():
        output = model(tensor_input)
        prob = F.softmax(output, dim=1)
        pred_idx = torch.argmax(prob, dim=1).item()

    # 4. 결과 출력
    word = index_to_word.get(str(pred_idx), "[Unknown]")
    print(f"🎯 예측된 수어 인덱스: {pred_idx}")
    print(f"📛 예측된 수어 단어: {word}")
    return pred_idx, word

# ✅ 실행
if __name__ == "__main__":
    predict_sign_from_video("C:/Users/유준혁/PycharmProjects/Sign2Speech/media/mp4/0a572adb-83b8-48b7-b98f-f2b1ff0fac7d.mp4", save_npy_path="C:/Users/유준혁/PycharmProjects/Sign2Speech/media/mp4/0a572adb-83b8-48b7-b98f-f2b1ff0fac7d.npy")
