import os, uuid, tempfile, subprocess, json
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from posetest2.test_from_video import predict_sign_from_video
from video.huggingFace import sentence_to_gloss
from .models import SignVideo
from django.db.models import Q

# 1) 녹화 UI
def index(request):
    return render(request, 'video/index.html')

def sign2text(request):
    return render(request, 'video/Sign2Text.html')

def text2sign(request):
    return render(request, 'video/Text2Sign.html')

# 2) WebM → MP4 변환 후 저장
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_and_convert(request):
    webm = request.FILES.get('video')
    if not webm:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    # 임시 디렉토리
    temp_dir = settings.MEDIA_ROOT / 'C:/Users/유준혁/PycharmProjects/Sign2Speech/media/temp'
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 임시 WebM 파일
    tmp_in = tempfile.NamedTemporaryFile(suffix='.webm', dir=temp_dir, delete=False)
    for chunk in webm.chunks():
        tmp_in.write(chunk)
    tmp_in.close()
    input_path = tmp_in.name

    # 임시 MP4 출력
    tmp_out = tempfile.NamedTemporaryFile(suffix='.mp4', dir=temp_dir, delete=False)
    tmp_out.close()
    output_path = tmp_out.name

    # FFmpeg 호출 (경로를 실제로 설치한 위치로 변경)
    ffmpeg = str(Path(settings.BASE_DIR) / 'C:/Users/유준혁/PycharmProjects/Sign2Speech/ffmpeg/bin/ffmpeg.exe')
    cmd = [ffmpeg, '-y', '-i', input_path, '-c:v', 'libx264', output_path]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        os.remove(input_path)
        os.remove(output_path)
        return JsonResponse({'error': 'FFmpeg 변환 실패'}, status=500)

    # 최종 저장
    mp4_dir = settings.MEDIA_ROOT / 'mp4'
    mp4_dir.mkdir(parents=True, exist_ok=True)
    saved_name = f"{uuid.uuid4()}.mp4"
    final_path = mp4_dir / saved_name
    os.replace(output_path, final_path)

    # 임시 WebM 삭제
    os.remove(input_path)
    pred_idx, word = predict_sign_from_video("C:/Users/유준혁/PycharmProjects/pose_transformer_finetuning/media/mp4/" + saved_name)

    # JSON 응답
    return JsonResponse({'status': 'saved',
                         'filename': saved_name,
                         'idx': pred_idx,
                         'word': word
                         })


@api_view(['POST'])
def text_to_video(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    text = payload.get('text', '')
    gloss_list = sentence_to_gloss(text)
    all_videos = []
    for gloss in gloss_list:
        match = SignVideo.objects.filter(gloss__icontains=gloss)
        for video in match:
            all_videos.append(video)
    seen_ids = set()
    unique_videos = []
    for v in all_videos:
        if v.id not in seen_ids:
            unique_videos.append(v)
            seen_ids.add(v.id)
    # 결과를 리스트로 직렬화
    results = []
    for video in unique_videos:
        results.append({
            'gloss': video.gloss,
            'signVideoUrl': video.sign_video_url,
            'signDescription': video.sign_description,
            'signImages': video.sign_images,
        })
    return JsonResponse({'results': results})
