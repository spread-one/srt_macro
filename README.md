# srt_macro
srt_macro



# exe 파일 패킹 방법
pip install -r requirements.txt # 라이브러리 설치
pyinstaller --onefile --windowed --add-data "success_sound.wav;." srt_macro_edge.py

