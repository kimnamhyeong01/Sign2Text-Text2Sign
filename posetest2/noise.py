import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from model import PoseFormer  # 네 모델 클래스

# ✅ 모델 정의 및 로드
model = PoseFormer()
model.load_state_dict(torch.load("E:/pose/pose_transformer_finetuned.pt", map_location='cpu'))
model.eval()

# ✅ Mediapipe 설정
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
pose = mp_pose.Pose(static_image_mode=False)
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)

TARGET_FRAMES = 30
TOTAL_KEYPOINTS = 66

# ✅ Keypoint 추출 함수
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
def predict_from_keypoints(kp_array):
    keypoints = torch.tensor(kp_array, dtype=torch.float32).view(1, 30, -1)
    with torch.no_grad():
        output = model(keypoints)
        prob = F.softmax(output, dim=1)
        return torch.argmax(prob, dim=1).item()

# ✅ 경로 설정
video_path = "E:/video/KETI_SL_0000000217.avi"
npy_path = "E:/pose/217.npy"

# ✅ 추출 → 예측
pose_from_video = extract_pose_from_video(video_path)
pred_from_video = predict_from_keypoints(pose_from_video)

# ✅ 기존 npy → 예측
pose_from_npy = np.load(npy_path)
pred_from_npy = predict_from_keypoints(pose_from_npy)

# ✅ 결과 비교
print(f"🎥 영상 추출 예측 결과   → {pred_from_video}")
print(f"📁 기존 NPY 예측 결과   → {pred_from_npy}")
print("✅ 일치 여부:", "✔️ 동일" if pred_from_video == pred_from_npy else "❌ 다름")
