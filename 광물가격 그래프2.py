import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import matplotlib.font_manager as fm
import numpy as np
import seaborn as sns
import platform
import matplotlib as mpl
import firebase_admin
from firebase_admin import credentials, storage
import os

# Firebase 초기화
cred = credentials.Certificate('mineralpricetracking-firebase-adminsdk-fbsvc-b070c56929.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'mineralpricetracking.appspot.com'
})

# Graph style settings
plt.style.use('default')  # Use default style
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'grid.alpha': 0.3,
    'grid.color': '#cccccc',
    'figure.constrained_layout.use': True  # 자동 레이아웃 조정
})

def upload_to_firebase(local_file_path, period):
    """Firebase Storage에 파일 업로드"""
    try:
        bucket = storage.bucket()
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        destination_blob_name = f'mineral_prices/{period}_{current_time}.png'
        
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)
        
        # 파일의 공개 URL 생성
        blob.make_public()
        url = blob.public_url
        
        # URL을 파일로 저장
        with open('mineral_prices_urls.txt', 'a', encoding='utf-8') as f:
            f.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {period} - {url}\n')
        
        print('\n=== 그래프 공유 정보 ===')
        print(f'업로드 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'기간: {period}')
        print(f'공개 URL: {url}')
        print('이 URL을 통해 누구나 그래프를 볼 수 있습니다.')
        print('========================\n')
        
        return url
    except Exception as e:
        print(f'업로드 중 오류 발생: {e}')
        return None

def show_recent_urls():
    """최근 업로드된 URL들을 보여줌"""
    try:
        if os.path.exists('mineral_prices_urls.txt'):
            print('\n=== 최근 업로드된 그래프 목록 ===')
            with open('mineral_prices_urls.txt', 'r', encoding='utf-8') as f:
                urls = f.readlines()
                # 최근 5개만 표시
                for url in urls[-5:]:
                    print(url.strip())
            print('================================\n')
    except Exception as e:
        print(f'URL 목록 읽기 오류: {e}')

def get_date_range(period):
    end_date = datetime.now()
    
    if period == '1W':
        start_date = end_date - timedelta(days=7)
    elif period == '1M':
        start_date = end_date - timedelta(days=30)
    elif period == '1Y':
        start_date = end_date - timedelta(days=365)
    elif period == '5Y':
        start_date = end_date - timedelta(days=365*5)
    else:
        raise ValueError("Please select a valid period")
    
    return start_date, end_date

def get_metal_symbol(metal):
    # Yahoo Finance symbols
    symbols = {
        'Copper': 'HG=F',      # Copper Futures
        'Aluminium': 'ALI=F',  # Aluminium Futures
        'Gold': 'GC=F',        # Gold Futures
        'Silver': 'SI=F',      # Silver Futures
        'Platinum': 'PL=F',    # Platinum Futures
        'Palladium': 'PA=F',   # Palladium Futures
        'Rare Earth ETF': 'REMX',  # VanEck Rare Earth ETF
        'Lynas Corp': 'LYSDY',     # Lynas Corporation
        'MP Materials': 'MP'       # MP Materials Corp
    }
    return symbols.get(metal)

def plot_metal_prices(period):
    # Calculate date range
    start_date, end_date = get_date_range(period)
    
    # List of metals and rare earth related symbols
    metals = [
        'Copper', 'Aluminium', 'Gold', 'Silver', 'Platinum', 'Palladium',
        'Rare Earth ETF', 'Lynas Corp', 'MP Materials'
    ]
    data = {}

    # Fetch real data
    for metal in metals:
        symbol = get_metal_symbol(metal)
        if symbol:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)
                if not df.empty:
                    data[metal] = df['Close']
            except Exception as e:
                print(f"Failed to fetch data for {metal}: {e}")
                continue

    if not data:
        print("Failed to fetch any data.")
        return

    # Create DataFrame
    df = pd.DataFrame(data)

    # 그래프 크기와 간격 조정
    fig = plt.figure(figsize=(25, 25))  # 크기를 25x25로 증가
    
    # 제목을 위한 별도의 subplot 생성 - 간격 축소
    gs = fig.add_gridspec(4, 3, height_ratios=[0.2, 1, 1, 1], hspace=0.1, wspace=0.11
    )
    
    # 메인 타이틀용 subplot
    title_ax = fig.add_subplot(gs[0, :])
    title_ax.axis('off')  # 축 숨기기
    title_ax.text(0.5, 0.5, f'Metal and Rare Earth Prices ({period})',
                 horizontalalignment='center',
                 fontsize=20, fontweight='bold')  # 제목 폰트 크기도 증가

    # 나머지 그래프들을 3x3 그리드로 배치
    axes = []
    for i in range(3):
        for j in range(3):
            if i * 3 + j < len(metals):
                ax = fig.add_subplot(gs[i+1, j])
                axes.append(ax)

    # Set color palette
    colors = sns.color_palette("husl", n_colors=len(metals))

    # Plot individual graphs for each metal
    for idx, metal in enumerate(metals):
        if metal in df.columns:
            ax = axes[idx]
            df[metal].plot(ax=ax, label=metal, linewidth=2, color=colors[idx])
            ax.set_title(f'{metal} Price ({period})', pad=15, fontsize=12, fontweight='bold')
            ax.set_xlabel('Date', fontsize=10)
            
            # y축 단위 설정
            if metal in ['Gold', 'Platinum', 'Palladium']:
                ax.set_ylabel('Price (USD/oz)', fontsize=10)
            elif metal in ['Copper', 'Aluminium']:
                ax.set_ylabel('Price (USD/lb)', fontsize=10)
            else:
                ax.set_ylabel('Price (USD)', fontsize=10)
            
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.legend(fontsize=10, loc='upper left')
            
            # 천 단위 구분자 추가
            def format_price(x, p):
                if x >= 1000:
                    return f'${x/1000:,.1f}K'
                return f'${x:,.0f}'
            
            ax.yaxis.set_major_formatter(plt.FuncFormatter(format_price))
            
            # y축 여백 조정
            ymin, ymax = ax.get_ylim()
            ax.set_ylim(ymin - (ymax-ymin)*0.05, ymax + (ymax-ymin)*0.05)

    # Save and show plot
    filename = f'metal_and_rare_earth_prices_{period}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0.3)
    
    # Firebase에 업로드
    url = upload_to_firebase(filename, period)
    if url:
        print(f'그래프가 Firebase에 업로드되었습니다: {url}')
    
    plt.show()
    
    # 로컬 파일 삭제
    try:
        os.remove(filename)
        print('로컬 파일이 삭제되었습니다.')
    except Exception as e:
        print(f'파일 삭제 중 오류 발생: {e}')

# Package installation notice
print("Note: Please install required packages using the following command:")
print("pip install yfinance pandas matplotlib seaborn")

# Get user input
while True:
    print("\n메뉴를 선택하세요:")
    print("1. 새로운 그래프 생성")
    print("2. 최근 업로드된 그래프 URL 보기")
    print("3. 종료")
    
    menu_choice = input("선택 (1-3): ")
    
    if menu_choice == '1':
        print("\n기간을 선택하세요:")
        print("1. 1주일")
        print("2. 1개월")
        print("3. 1년")
        print("4. 5년")
        
        choice = input("선택 (1-4): ")
        period_map = {'1': '1W', '2': '1M', '3': '1Y', '4': '5Y'}
        
        if choice in period_map:
            plot_metal_prices(period_map[choice])
        else:
            print("올바른 선택지를 입력해주세요 (1-4)")
    
    elif menu_choice == '2':
        show_recent_urls()
    
    elif menu_choice == '3':
        print("프로그램을 종료합니다.")
        break
    
    else:
        print("올바른 메뉴를 선택해주세요 (1-3)")
