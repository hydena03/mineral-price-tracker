import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json

# 이미지 저장 디렉토리 생성
if not os.path.exists('images'):
    os.makedirs('images')

# 데이터 저장 디렉토리 생성
if not os.path.exists('data'):
    os.makedirs('data')

def get_date_range(period, base_date=None):
    if base_date is None:
        end_date = datetime.now()
    else:
        end_date = base_date
    
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

def save_price_data(data, period, base_date):
    """가격 데이터를 JSON 파일로 저장"""
    date_str = base_date.strftime("%Y%m%d") if base_date else "current"
    filename = f'data/metal_prices_{period}_{date_str}.json'
    
    # DataFrame을 JSON 형식으로 변환
    json_data = {}
    for metal in data.columns:
        json_data[metal] = {
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'prices': data[metal].tolist(),
            'unit': 'USD/oz' if metal in ['Gold', 'Silver', 'Platinum', 'Palladium'] else 'USD/lb' if metal in ['Copper', 'Aluminium'] else 'USD'
        }
    
    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"- 가격 데이터가 {filename}에 저장되었습니다.")

def plot_metal_prices(period, base_date=None):
    date_str = base_date.strftime("%Y-%m-%d") if base_date else "current"
    print(f"\n{period} 기간 그래프 생성 중... (기준일: {date_str})")
    
    # Calculate date range
    start_date, end_date = get_date_range(period, base_date)
    
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

    # Create DataFrame and save to JSON
    df = pd.DataFrame(data)
    save_price_data(df, period, base_date)

    # Create subplot grid
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=[f'{metal} Price ({period})' for metal in metals],
        vertical_spacing=0.12,
        horizontal_spacing=0.05
    )

    # Add title to the figure
    fig.update_layout(
        title_text=f'Metal and Rare Earth Prices ({period})',
        title_x=0.5,
        title_font_size=20,
        showlegend=False,
        width=1500,
        height=1500,
        template='plotly_white'
    )

    # Plot each metal in its subplot
    for idx, metal in enumerate(metals):
        if metal in df.columns:
            row = idx // 3 + 1
            col = idx % 3 + 1
            
            # Get unit for hover text
            unit = 'USD/oz' if metal in ['Gold', 'Silver', 'Platinum', 'Palladium'] else 'USD/lb' if metal in ['Copper', 'Aluminium'] else 'USD'
            
            # Create hover text
            hover_text = [
                f'날짜: {date.strftime("%Y-%m-%d")}<br>' +
                f'가격: ${price:.2f} {unit}'
                for date, price in zip(df.index, df[metal])
            ]
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[metal],
                    name=metal,
                    hovertext=hover_text,
                    hoverinfo='text',
                    line=dict(width=2)
                ),
                row=row,
                col=col
            )
            
            # Update y-axis label
            fig.update_yaxes(
                title_text=f'Price ({unit})',
                row=row,
                col=col,
                tickprefix='$',
                tickformat=',.2f'
            )

    # Update layout for each subplot
    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # Save plot with date in filename
    if base_date:
        date_suffix = base_date.strftime("_%Y%m%d")
        filename = f'metal_and_rare_earth_prices_{period}{date_suffix}.html'
    else:
        filename = f'metal_and_rare_earth_prices_{period}.html'
    
    save_path = os.path.join('images', filename)
    fig.write_html(save_path)
    print(f"- {period} 그래프가 {save_path}에 저장되었습니다.")

def generate_historical_graphs():
    # 2025년 1월 1일부터 2월 3일까지
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 2, 4)
    current_date = start_date
    
    while current_date <= end_date:
        print(f"\n=== {current_date.strftime('%Y년 %m월 %d일')} 그래프 생성 중 ===")
        for period in ['1W', '1M', '1Y', '5Y']:
            plot_metal_prices(period, current_date)
        current_date += timedelta(days=1)

def main():
    print("과거 데이터 그래프 생성을 시작합니다...")
    generate_historical_graphs()
    print("\n모든 그래프 생성이 완료되었습니다.")

if __name__ == "__main__":
    main() 