import cv2
import numpy as np
import mediapipe as mp
import os

# MediaPipe 초기화
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

def extract_66_keypoints(frame, pose_model, hands_model):
    keypoints = np.zeros((66, 2), dtype=np.float32)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pose_result = pose_model.process(frame_rgb)
    hands_result = hands_model.process(frame_rgb)

    if hands_result and hands_result.multi_hand_landmarks:
        for hand_idx, hand_landmarks in enumerate(hands_result.multi_hand_landmarks):
            for i, lm in enumerate(hand_landmarks.landmark[:21]):
                if hand_idx == 0:
                    keypoints[i] = [lm.x, lm.y]
                elif hand_idx == 1:
                    keypoints[21 + i] = [lm.x, lm.y]

    if pose_result and pose_result.pose_landmarks:
        for i, lm in enumerate(pose_result.pose_landmarks.landmark[:24]):
            keypoints[42 + i] = [lm.x, lm.y]

    return keypoints

def extract_keypoints_from_url(video_url):
    cap = cv2.VideoCapture(video_url)
    pose = mp_pose.Pose()
    hands = mp_hands.Hands(max_num_hands=2)
    keypoints_all = []

    if not cap.isOpened():
        print("❌ 영상 열기 실패:", video_url)
        return None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        keypoints = extract_66_keypoints(frame, pose, hands)
        keypoints_all.append(keypoints)

    cap.release()
    return np.array(keypoints_all)

def extract_keypoints_from_file(filepath, duration_sec=5, fps=10):
    import cv2
    from posetest2.test_from_video import extract_pose_from_video
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        print("❌ 영상 열기 실패:", filepath)
        return None
    return extract_pose_from_video(filepath)

def record_webcam_keypoints(duration_sec=5, fps=10):
    cap = cv2.VideoCapture(0)
    pose = mp_pose.Pose()
    hands = mp_hands.Hands(max_num_hands=2)
    all_keypoints = []

    for i in range(3, 0, -1):
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.putText(frame, str(i), (250, 250), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 10)
        cv2.imshow('준비 중...', frame)
        cv2.waitKey(1000)

    for _ in range(10):
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.putText(frame, "동작 시작!", (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 8)
        cv2.imshow('준비 중...', frame)
        cv2.waitKey(50)

    interval = int(1000 / fps)
    start = cv2.getTickCount()
    frames_recorded = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        elapsed = (cv2.getTickCount() - start) / cv2.getTickFrequency() * 1000
        if elapsed < interval:
            continue

        keypoints = extract_66_keypoints(frame, pose, hands)
        all_keypoints.append(keypoints)
        frames_recorded += 1
        start = cv2.getTickCount()

        for (x, y) in keypoints:
            if x > 0 and y > 0:
                h, w, _ = frame.shape
                cx, cy = int(x * w), int(y * h)
                cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

        cv2.imshow('웹캠 녹화 중...', frame)
        if cv2.waitKey(1) & 0xFF == 27 or frames_recorded >= duration_sec * fps:
            break

    cap.release()
    cv2.destroyAllWindows()
    return np.array(all_keypoints)

def resize_keypoints(seq, target_len):
    if len(seq) == target_len:
        return seq
    indices = np.linspace(0, len(seq) - 1, target_len).astype(np.int32)
    return seq[indices]

def score_similarity_by_frame(user_seq, target_seq):
    if len(user_seq) == 0 or len(target_seq) == 0:
        return 0.0

    min_len = min(len(user_seq), len(target_seq))
    user_seq = resize_keypoints(user_seq, min_len)
    target_seq = resize_keypoints(target_seq, min_len)

    total_distance = 0
    for u, t in zip(user_seq, target_seq):
        total_distance += np.mean(np.linalg.norm(u - t, axis=1))

    avg_distance = total_distance / min_len

    MAX_DISTANCE = 2.3
    MIN_SCORE = 50
    MAX_SCORE = 100

    if avg_distance >= MAX_DISTANCE:
        score = MIN_SCORE
    else:
        score = MAX_SCORE - ((avg_distance / MAX_DISTANCE) * (MAX_SCORE - MIN_SCORE))

    return round(score, 2)

def run_score_comparison_from_url(video_url, user_video_path=None, duration_sec=5, fps=10):
    print("🎥 정답 수어 영상 URL → 키포인트 추출 중...")
    target_seq = extract_keypoints_from_url(video_url)
    if target_seq is None:
        return -1, "❌ 정답 수어 영상을 불러올 수 없습니다."

    if user_video_path is not None:
        print("📁 업로드된 사용자 영상 → 키포인트 추출 중...")
        user_seq = extract_keypoints_from_file(user_video_path, duration_sec=duration_sec, fps=fps)
    else:
        print("🟢 사용자 웹캠 캡처 시작...")
        user_seq = record_webcam_keypoints(duration_sec=duration_sec, fps=fps)

    print("📊 정확도 비교 중...")
    score = score_similarity_by_frame(user_seq, target_seq)
    return score, "🎯 비교 완료"