import time
import os
import pandas as pd
import tracemalloc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def estimate_player_value(file_path):
    # Load data
    df = pd.read_csv(file_path)
    
    # Clean minutes column if necessary
    if df['Playing Time: minutes'].dtype == object:
        df['Playing Time: minutes'] = df['Playing Time: minutes'].str.replace(',', '').astype(int)
    
    # Fix Transfer values format to int
    df = df.dropna(subset=['Transfer values'])
    df['Transfer values'] = df['Transfer values'].str.replace('€', '', regex=False).str.replace('M', '', regex=False).astype(float) * 1_000_000
    df['Transfer values'] = df['Transfer values'].astype(int)

    # Select features
    features = [
        'Age',
        'Position',
        'Playing Time: minutes',
        'Performance: goals',
        'Performance: assists',
        'GCA: GCA',
        'Progression: PrgR',
        'Tackles: Tkl'
    ]

    X = df[features]
    y = df['Transfer values']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Preprocessing: OneHot for categorical 'Position'
    categorical_features = ['Position']
    numeric_features = [col for col in features if col not in categorical_features]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough'  # Numeric features stay unchanged
    )
    
    # Model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # Pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    # Train
    pipeline.fit(X_train, y_train)
    
    # Predict and evaluate
    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error: {mae:,.0f} €")
    
    return pipeline

def get_data():
    # Load the CSV file
    file_path = os.path.join('P1_RES', 'results.csv')
    df = pd.read_csv(file_path)

    # Clean the 'Playing Time: minutes' column
    df['Playing Time: minutes'] = df['Playing Time: minutes'].str.replace(',', '').astype(int)

    # Filter players with more than 900 minutes
    filtered_df = df[df['Playing Time: minutes'] > 900]

    return filtered_df

def update_data(filtered_df):
    player_dic = {}
    for name in filtered_df['Name']:
        player_dic[name] = ''
    # Khởi tạo Chrome
    driver = webdriver.Chrome()
    # Vào trang cần crawl
    url = 'https://www.footballtransfers.com/us/players/uk-premier-league/'
    driver.get(url)
    names = []
    prices = []
    cnt = 0
    while cnt < 22:
        time.sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Tìm bảng cầu thủ
        table = soup.find('table', class_='table table-hover no-cursor table-striped leaguetable mvp-table similar-players-table mb-0')
        
        if table is None:
            print("Không tìm thấy bảng dữ liệu.")
            break

        # Lấy tên cầu thủ
        name_tags = table.find_all('div', class_='text')
        # Lấy giá trị cầu thủ
        price_tags = table.find_all('span', class_='player-tag')
        
        for n in name_tags:
            a_tag = n.find('a')
            if a_tag:
                names.append(a_tag.get('title'))

        for p in price_tags:
            prices.append(p.text.strip())
        
        print(f"Đã crawl {len(names)} cầu thủ")

        # Tìm nút Next để click
        try:
            cnt+=1
            next_button = driver.find_element(By.CLASS_NAME, 'pagination_next_button')
            next_button.click()
        except:
            print("Hết trang rồi! Dừng lại.")
            break

    # Đóng driver
    driver.quit()
    
    for i in range(len(names)):
        if names[i] in player_dic:
            player_dic[names[i]] = prices[i]

    return player_dic



def save_result(filtered_df, player_dic):

    filtered_df['Transfer values'] = player_dic.values()
    file_path = os.path.join('P4_RES', 'MoreThan900mins.csv')
    filtered_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print("Đã lưu vào MoreThan900mins.csv")

def Task_1():
    filtered_df = get_data()
    player_dic = update_data(filtered_df)
    save_result(filtered_df, player_dic)

def Task_2():
    # Example usage
    model = estimate_player_value('MoreThan900mins.csv')

    new_player = pd.DataFrame({
        'Age': [26],
        'Position': ['GK'],
        'Playing Time: minutes': [2250],
        'Performance: goals': [0],
        'Performance: assists': [0],
        'GCA: GCA': [0],
        'Progression: PrgR': [0],
        'Tackles: Tkl': [0]
    })

    # Dự đoán giá trị cầu thủ mới
    predicted_value = model.predict(new_player)
    print(f"Estimated player value: {predicted_value[0]:,.0f} €")

def Problem_4():
    Task_1()
    Task_2()

if __name__ == '__main__':
    tracemalloc.start()
    start = time.time()
    os.makedirs('P4_RES', exist_ok=True)
    Problem_4()
    end = time.time()   
    print(f"Thời gian chạy: {end - start:.6f} giây")
    current, peak = tracemalloc.get_traced_memory()
    print(f"Bộ nhớ hiện tại: {current / 1024 ** 2:.2f} MB")
    print(f"Bộ nhớ đạt đỉnh: {peak / 1024 ** 2:.2f} MB")
    tracemalloc.stop()