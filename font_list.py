import matplotlib.font_manager as fm

# 시스템에 설치된 폰트 목록 출력
font_list = [f.name for f in fm.fontManager.ttflist]
for font in sorted(font_list):
    print(font) 