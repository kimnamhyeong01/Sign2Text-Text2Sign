# 양방향 수어 번역 서비스

## 👩🏻‍💻 팀원
|[김남형](https://github.com/kimnamhyeong01)|[유준혁](https://github.com/ericyoo0107)|[최우진](https://github.com/wxxwls)|
|:-:|:-:|:-:|
|<img src="https://avatars.githubusercontent.com/u/119601427?v=4" alt="김남형" width="150" height="150">|<img src="https://avatars.githubusercontent.com/u/65710954?v=4" alt="유준혁" width="150" height="150">|<img src="https://avatars.githubusercontent.com/u/131441769?v=4" alt="최우진" width="150" height="150">|

## 🛠 기술 스택
 ![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
 ![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
 ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript&logoColor=black) 
 ![HTML5](https://img.shields.io/badge/HTML5-%3E5-E34F26?logo=html5&logoColor=white)
 ![CSS3](https://img.shields.io/badge/CSS3-%3E3-1572B6?logo=css3&logoColor=white)
 ![MySQL](https://img.shields.io/badge/MySQL-8.0-005C84?logo=mysql&logoColor=white)

## ✅ 서비스 기능
### 1. 웹캠으로 수어를 녹화하면 수어 결과를 텍스트로 출력

https://github.com/user-attachments/assets/5fac238f-ed04-444c-b2fd-9f3595d6dc78

- 구현 방식
  1. JavaScript의 MediaRecorder API로 수어를 WebM 형식으로 녹화합니다.
  2. 녹화된 WebM 파일을 ffmpeg으로 MP4 형식으로 변환합니다.
  3. 생성된 MP4 파일을 파인튜닝된 Pose Transformer AI 모델에 입력합니다.
  4. AI가 출력한 글로스(단어)를 웹 화면에 표시합니다.
     
### 2. 텍스트를 입력하면 수어 영상 결과를 출력

https://github.com/user-attachments/assets/3b36fae7-8b23-416a-af9e-7068ae2afbff
   
- 구현 방식
  1. 사용자가 텍스트를 입력합니다.
  2. 입력된 텍스트를 HuggingFace API에 전달해 글로스(단어) 단위로 분리한 뒤 리스트로 반환받습니다.
  3. 반환된 글로스 리스트를 기반으로 VectorDB에서 매칭되는 영상 및 수어 설명을 조회합니다.
  4. 조회 결과(수어 영상 및 설명)를 사용자에게 출력합니다.
