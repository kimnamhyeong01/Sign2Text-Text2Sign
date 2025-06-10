import os, uuid, tempfile, subprocess, json, traceback
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from posetest2.test_from_video import predict_sign_from_video
from video.huggingFace import sentence_to_gloss, gloss_to_sentence
from .models import SignVideo
from video.skeleton_test import run_score_comparison_from_url
import whisper

model = whisper.load_model("base")

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

    # 쿠키에 글로스 저장(쿠키에 저장된 값이 없으면 빈 리스트 생성)
    stored_json = request.COOKIES.get('stored_glosses', '[]')
    try:
        stored = json.loads(stored_json)
    except json.JSONDecodeError:
        stored = []
    stored.append(word)

    # JSON 응답 작성 및 쿠키 설정
    response = JsonResponse({'status': 'saved',
                             'filename': saved_name,
                             'idx': pred_idx,
                             'word': word})
    response.set_cookie('stored_glosses', json.dumps(stored), httponly=False, path='/')
    return response

@api_view(['GET'])
def output_gloss(request):
    stored_json = request.COOKIES.get('stored_glosses')
    if not stored_json:
        return JsonResponse({'error': '저장된 글로스가 없습니다.'}, status=400)
    try:
        stored = json.loads(stored_json)
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 쿠키 데이터입니다.'}, status=400)
    final_sentence = gloss_to_sentence(stored)
    response = JsonResponse({'sentence': final_sentence})
    response.delete_cookie('stored_glosses')
    return response


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


@api_view(['POST'])
@parser_classes([MultiPartParser])
def audio_to_text(request):
    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'No audio uploaded'}, status=400)

    audio_temp_dir = Path('C:/Users/유준혁/PycharmProjects/pose_transformer_finetuning/media/temp')
    audio_temp_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        for chunk in audio_file.chunks():
            tmp.write(chunk)
        tmp.flush()
        tmp_path = tmp.name
        print(tmp_path)
    try:
        result = model.transcribe(tmp_path, language ='ko')
        text = result.get("text", "")

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': f"Whisper error: {str(e)}"}, status=500)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return JsonResponse({'text': text})


@api_view(['GET'])
def compare_sign_by_url(request):
    gloss = request.GET.get('gloss', '똑같다')
    video = SignVideo.objects.filter(gloss=gloss).first()
    if not video:
        return JsonResponse({'error': '해당 글로스에 대한 영상이 없습니다'}, status=404)

    video_url = video.sign_video_url
    score, message = run_score_comparison_from_url(video_url)
    return JsonResponse({'score': score, 'message': message})

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_and_compare(request):
    gloss = request.GET.get('gloss')
    video_file = request.FILES.get('video')
    if not video_file:
        return JsonResponse({'error': '비디오 파일이 없습니다'}, status=400)

    # 저장 경로
    save_path = os.path.join(settings.MEDIA_ROOT, 'compare_input.mp4')
    with open(save_path, 'wb') as f:
        for chunk in video_file.chunks():
            f.write(chunk)

    # 비교 대상 영상 URL (DB에서 해당 gloss 찾기)
    video = SignVideo.objects.filter(gloss=gloss).first()
    if not video:
        return JsonResponse({'error': '해당 글로스에 대한 정답 영상이 없습니다'}, status=404)

    # 유사도 평가 함수 실행
    score, message = run_score_comparison_from_url(video.sign_video_url, user_video_path=save_path)
    return JsonResponse({'score': score, 'message': message})
