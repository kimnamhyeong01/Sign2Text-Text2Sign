# 양방향 수어 번역 서비스

## 👩🏻‍💻 팀원
- 김남형 : AI 파인 튜닝 (Text to Sign)
- 유준혁 : 웹 서버 및 프론트엔드 개발
- 최우진 : 수어 영상 인식 AI Pose Transformer 파인 튜닝 (Sign to Text)

## 🛠 기술 스택
 ![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
 ![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
 ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript&logoColor=black) 
 ![HTML5](https://img.shields.io/badge/HTML5-%3E5-E34F26?logo=html5&logoColor=white)
 ![CSS3](https://img.shields.io/badge/CSS3-%3E3-1572B6?logo=css3&logoColor=white)
 ![MySQL](https://img.shields.io/badge/MySQL-8.0-005C84?logo=mysql&logoColor=white)

## ✅ 서비스 기능
1. 웹캠으로 수어를 녹화하면 수어 결과를 텍스트로 출력
- 구현 방식
  1. 사용자가 Javascript의 MediaRecorder를 통해 수어를 녹화
  2. 녹화된 WebM 파일을 webm 파일을 ffmpeg을 통해 mp4 형식으로 변경
  3. 생성된 MP4 파일을 파인 튜닝된 Pose Transformer AI 모델에 입력
  4. AI가 결과로 출력한 글로스(단어)를 웹 화면에 표시
2. 텍스트를 입력하면 수어 영상 결과를 출력
- 구현 방식
  1. 사용자가 텍스트를 입력
  2. 입력받은 텍스트를 HuggingFace API에 전달하여 글로스(단어) 단위로 분리 → List로 반환
  3. 반환된 글로스 리스트를 이용하여 데이터베이스 내 저장된 매칭 영상, 수어 설명을 조회 (영상은 OpenAPI를 통해 저장)
  4. 조회된 수어 영상, 설명을 사용자에게 출력
