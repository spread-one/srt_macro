# srt_macro
srt_macro(edge 브라우저용)

chrome은 드라이버 오류가 자주 발생해서 edge로 변경



# 라이브러리 설치
pip install -r requirements.txt # 라이브러리 설치


# exe 파일 패킹 방법
pip install pyinstaller

pyinstaller --onefile --windowed --add-data "success_sound.wav;." srt_macro_edge.py

