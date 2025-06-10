import os

# "C:/Users/유준혁/PycharmProjects/pose_transformer_finetuning/ffmpeg/bin"
FFMPEG_DIR = "C:/Users/유준혁/PycharmProjects/pose_transformer_finetuning/ffmpeg/bin"
os.environ["Path"] = FFMPEG_DIR + ";" + os.environ["Path"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'signdb',             # 생성한 DB 이름
        'USER': 'root',            # MySQL 사용자
        'PASSWORD': 'dbwnsgur',    # 비밀번호
        'HOST': 'localhost',           # 원격일 경우 IP 또는 도메인
        'PORT': '3306',                # 기본 MySQL 포트
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
