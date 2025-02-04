import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import matplotlib.font_manager as fm
import numpy as np
import seaborn as sns
import os

# 이미지 저장 디렉토리 생성
if not os.path.exists('images'):
    os.makedirs('images')

# Graph style settings
plt.style.use('default')
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'grid.alpha': 0.3,
    'grid.color': '#cccccc',
    'figure.constrained_layout.use': True
})

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
    print(f"\n{period} 기간 그래프 생성 중...")
    
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
                print(f"- {metal} 데이터 가져오기 성공")
            except Exception as e:
                print(f"- {metal} 데이터 가져오기 실패: {e}")
                continue

    if not data:
        print("데이터를 가져오는데 실패했습니다.")
        return

    # Create DataFrame
    df = pd.DataFrame(data)

    # 그래프 크기와 간격 조정
    fig = plt.figure(figsize=(25, 25))
    
    # 제목을 위한 별도의 subplot 생성
    gs = fig.add_gridspec(4, 3, height_ratios=[0.2, 1, 1, 1], hspace=0.1, wspace=0.11)
    
    # 메인 타이틀용 subplot
    title_ax = fig.add_subplot(gs[0, :])
    title_ax.axis('off')
    title_ax.text(0.5, 0.5, f'Metal and Rare Earth Prices ({period})',
                 horizontalalignment='center',
                 fontsize=20, fontweight='bold')

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
            
            def format_price(x, p):
                if x >= 1000:
                    return f'${x/1000:,.1f}K'
                return f'${x:,.0f}'
            
            ax.yaxis.set_major_formatter(plt.FuncFormatter(format_price))
            
            ymin, ymax = ax.get_ylim()
            ax.set_ylim(ymin - (ymax-ymin)*0.05, ymax + (ymax-ymin)*0.05)

    # Save plot
    filename = f'metal_and_rare_earth_prices_{period}.png'
    save_path = os.path.join('images', filename)
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0.3)
    print(f"- {period} 그래프가 {save_path}에 저장되었습니다.")
    plt.close()

def main():
    print("광물 가격 그래프 생성을 시작합니다...")
    periods = ['1W', '1M', '1Y', '5Y']
    for period in periods:
        plot_metal_prices(period)
    print("\n모든 그래프 생성이 완료되었습니다.")

if __name__ == "__main__":
    main() 