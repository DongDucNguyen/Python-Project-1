import os
import tracemalloc
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

PLAYER_KEYS = [
    'name', 'nationality', 'position', 'team', 'age', 'games', 'games_starts',
    'minutes', 'goals', 'assist', 'cards_yellow', 'cards_red', 'xg', 'xg_assist',
    'progressive_carries', 'progressive_passes', 'progressive_passes_received', 'goals_per90',
    'assists_per90', 'xg_per90', 'xg_assist_per90', 'gk_goals_against_per90', 'gk_save_pct',
    'gk_clean_sheets_pct', 'gk_pens_save_pct', 'shots_on_target_pct', 'shots_on_target_per90',
    'goals_per_shot', 'average_shot_distance', 'passes_completed', 'passes_pct', 'passes_total_distance',
    'passes_pct_short', 'passes_pct_medium', 'passes_pct_long', 'assisted_shots',
    'passes_into_final_third', 'passes_into_penalty_area', 'crosses_into_penalty_area',
    'sca', 'sca_per90', 'gca', 'gca_per90', 'tackles', 'tackles_won', 'challenges',
    'challenges_lost', 'blocks', 'blocked_shots', 'blocked_passes', 'interceptions', 'touches',
    'touches_def_pen_area', 'touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd',
    'touches_att_pen_area', 'take_ons', 'take_ons_won_pct', 'take_ons_tackled_pct', 'carries',
    'carries_progressive_distance',
    'carries_into_final_third', 'carries_into_penalty_area', 'miscontrols',
    'dispossessed', 'passes_received',
    'fouls', 'fouled', 'offsides', 'crosses',
    'ball_recoveries', 'aerials_won', 'aerials_lost', 'aerials_won_pct'
]

def create_default_player_dict():
    """Tạo một dictionary cầu thủ với giá trị mặc định 'N/a'."""
    return {key: 'N/a' for key in PLAYER_KEYS}

def export_player_data(player_dict):
    """Trích xuất dữ liệu từ dictionary cầu thủ thành list theo đúng thứ tự."""
    export_order_keys = [
        'name', 'nationality', 'team', 'position', 'age', 'games', 'games_starts', 'minutes', 'goals', 'assist',
        'cards_yellow', 'cards_red', 'xg', 'xg_assist', 'progressive_carries', 'progressive_passes', 'progressive_passes_received',
        'goals_per90', 'assists_per90', 'xg_per90', 'xg_assist_per90', 'gk_goals_against_per90', 'gk_save_pct', 'gk_clean_sheets_pct',
        'gk_pens_save_pct', 'shots_on_target_pct', 'shots_on_target_per90', 'goals_per_shot', 'average_shot_distance', 'passes_completed',
        'passes_pct', 'passes_total_distance', 'passes_pct_short', 'passes_pct_medium', 'passes_pct_long', 'assisted_shots',
        'passes_into_final_third', 'passes_into_penalty_area', 'crosses_into_penalty_area', 'progressive_passes',
        'sca', 'sca_per90', 'gca', 'gca_per90',
        'tackles', 'tackles_won', 'challenges', 'challenges_lost', 'blocks', 'blocked_shots', 'blocked_passes', 'interceptions',
        'touches', 'touches_def_pen_area', 'touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd', 'touches_att_pen_area',
        'take_ons', 'take_ons_won_pct', 'take_ons_tackled_pct', 'carries', 'carries_progressive_distance', 'progressive_carries',
        'carries_into_final_third',  
        'carries_into_penalty_area', 'miscontrols', 'dispossessed', 'passes_received', 'progressive_passes_received',
        'fouls', 'fouled', 'offsides', 'crosses',
        'ball_recoveries', 'aerials_won', 'aerials_lost', 'aerials_won_pct'
    ]
    nationality = player_dict.get('nationality', 'N/a')
    age = player_dict.get('age', 'N/a')
    nationality_processed = nationality.split()[1] if ' ' in nationality else nationality
    age_processed = age.split('-')[0] if '-' in age else age

    exported_list = []
    for key in export_order_keys:
        if key == 'nationality':
            exported_list.append(nationality_processed)
        elif key == 'age':
             exported_list.append(age_processed)
        else:
            exported_list.append(player_dict.get(key, 'N/a'))

    return exported_list


def get_player_name_from_dict(player_dict):
    """Hàm helper để lấy tên cầu thủ cho việc sắp xếp."""
    return player_dict.get('name', '')

def create_Set_Players():
    driver = webdriver.Chrome()
    url = 'https://fbref.com/en/comps/9/stats/Premier-League-Stats'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    x = soup.find('table', attrs={'id': 'stats_standard'})
    cnt = 0
    player_set = {} # Sử dụng dictionary thay vì set of objects
    for i in range(600):
        cnt+=1
        if cnt==26:
            cnt=0
            continue
        table = x.find('tr', attrs={'data-row':f'{str(i)}'})
        if not table: continue # Bỏ qua nếu không tìm thấy hàng

        # Tạo dictionary mới cho mỗi cầu thủ
        player_data = create_default_player_dict()

        player_data['name'] = table.find('td', attrs={'data-stat':'player'}).text.strip()
        player_data['nationality'] = table.find('td', attrs={'data-stat':'nationality'}).text.strip()
        player_data['position'] = table.find('td', attrs={'data-stat':'position'}).text.strip()
        player_data['team'] = table.find('td', attrs={'data-stat':'team'}).text.strip()
        player_data['age'] = table.find('td', attrs={'data-stat':'age'}).text.strip()
        player_data['games'] = table.find('td', attrs={'data-stat':'games'}).text.strip()
        player_data['games_starts'] = table.find('td', attrs={'data-stat':'games_starts'}).text.strip()
        minutes_str = table.find('td', attrs={'data-stat':'minutes'}).text.strip()
        player_data['minutes'] = minutes_str
        # Kiểm tra minutes giống như code gốc
        minutes_str_cleaned = minutes_str.replace(',', '') # Loại bỏ dấu phẩy nếu có
        if int(minutes_str_cleaned) <= 90: continue


        player_data['goals'] = table.find('td', attrs={'data-stat':'goals'}).text.strip()
        player_data['assist'] = table.find('td', attrs={'data-stat':'assists'}).text.strip() # Sửa key 'assists' thành 'assist' cho nhất quán
        player_data['cards_yellow'] = table.find('td', attrs={'data-stat':'cards_yellow'}).text.strip()
        player_data['cards_red'] = table.find('td', attrs={'data-stat':'cards_red'}).text.strip()
        player_data['xg'] = table.find('td', attrs={'data-stat':'xg'}).text.strip()
        player_data['xg_assist'] = table.find('td', attrs={'data-stat':'xg_assist'}).text.strip()
        player_data['progressive_carries'] = table.find('td', attrs={'data-stat':'progressive_carries'}).text.strip()
        player_data['progressive_passes'] = table.find('td', attrs={'data-stat':'progressive_passes'}).text.strip()
        player_data['progressive_passes_received'] = table.find('td', attrs={'data-stat':'progressive_passes_received'}).text.strip()
        player_data['goals_per90'] = table.find('td', attrs={'data-stat':'goals_per90'}).text.strip()
        player_data['assists_per90'] = table.find('td', attrs={'data-stat':'assists_per90'}).text.strip()
        player_data['xg_per90'] = table.find('td', attrs={'data-stat':'xg_per90'}).text.strip()
        player_data['xg_assist_per90'] = table.find('td', attrs={'data-stat':'xg_assist_per90'}).text.strip()

        # Sử dụng 'name' + 'team' làm key cho dictionary ngoài
        player_key = str(player_data['name']) + str(player_data['team'])
        player_set[player_key] = player_data
    driver.quit() # Đóng trình duyệt sau khi hoàn tất
    return player_set

def update_Set_Goalkeeping(player_set):
    driver = webdriver.Chrome()
    url = 'https://fbref.com/en/comps/9/keepers/Premier-League-Stats'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    x = soup.find('table', attrs={'id': 'stats_keeper'})
    for i in range (43):
        if i == 25: continue
        table = x.find('tr', attrs={'data-row':f'{str(i)}'})
        if not table: continue

        name = table.find('td', attrs={'data-stat':'player'}).text.strip()
        team = table.find('td', attrs={'data-stat':'team'}).text.strip()
        player_key = str(name) + str(team)

        if player_key in player_set:
            player_set[player_key]['gk_goals_against_per90'] = table.find('td', attrs={'data-stat':'gk_goals_against_per90'}).text.strip()
            player_set[player_key]['gk_save_pct'] = table.find('td', attrs={'data-stat':'gk_save_pct'}).text.strip()
            player_set[player_key]['gk_clean_sheets_pct'] = table.find('td', attrs={'data-stat':'gk_clean_sheets_pct'}).text.strip()
            player_set[player_key]['gk_pens_save_pct'] = table.find('td', attrs={'data-stat':'gk_pens_save_pct'}).text.strip()
    driver.quit()

def update_Set_Shooting(player_set):
    driver = webdriver.Chrome()
    url = 'https://fbref.com/en/comps/9/shooting/Premier-League-Stats'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    x = soup.find('table', attrs={'id': 'stats_shooting'})
    cnt = 0
    for i in range(600):
        cnt+=1
        if cnt==26:
            cnt=0
            continue
        table = x.find('tr', attrs={'data-row':f'{str(i)}'})
        if not table: continue

        name = table.find('td', attrs={'data-stat':'player'}).text.strip()
        team = table.find('td', attrs={'data-stat':'team'}).text.strip()
        player_key = str(name) + str(team)

        if player_key in player_set:
            player_set[player_key]['shots_on_target_pct'] = table.find('td', attrs={'data-stat':'shots_on_target_pct'}).text.strip()
            player_set[player_key]['shots_on_target_per90'] = table.find('td', attrs={'data-stat':'shots_on_target_per90'}).text.strip()
            player_set[player_key]['goals_per_shot'] = table.find('td', attrs={'data-stat':'goals_per_shot'}).text.strip()
            player_set[player_key]['average_shot_distance'] = table.find('td', attrs={'data-stat':'average_shot_distance'}).text.strip()
    driver.quit()

def update_Set_Passing(player_set):
    driver = webdriver.Chrome()
    url = 'https://fbref.com/en/comps/9/passing/Premier-League-Stats'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    x = soup.find('table', attrs={'id': 'stats_passing'})
    cnt = 0
    for i in range(600):
        cnt+=1
        if cnt==26:
            cnt=0
            continue
        table = x.find('tr', attrs={'data-row':f'{str(i)}'})
        if not table: continue

        name = table.find('td', attrs={'data-stat':'player'}).text.strip()
        team = table.find('td', attrs={'data-stat':'team'}).text.strip()
        player_key = str(name) + str(team)

        if player_key in player_set:
            player_set[player_key]['passes_completed'] = table.find('td', attrs={'data-stat':'passes_completed'}).text.strip()
            player_set[player_key]['passes_pct'] = table.find('td', attrs={'data-stat':'passes_pct'}).text.strip()
            player_set[player_key]['passes_total_distance'] = table.find('td', attrs={'data-stat':'passes_total_distance'}).text.strip()
            player_set[player_key]['passes_pct_short'] = table.find('td', attrs={'data-stat':'passes_pct_short'}).text.strip()
            player_set[player_key]['passes_pct_medium'] = table.find('td', attrs={'data-stat':'passes_pct_medium'}).text.strip()
            player_set[player_key]['passes_pct_long'] = table.find('td', attrs={'data-stat':'passes_pct_long'}).text.strip()
            player_set[player_key]['assisted_shots'] = table.find('td', attrs={'data-stat':'assisted_shots'}).text.strip()
            player_set[player_key]['passes_into_final_third'] = table.find('td', attrs={'data-stat':'passes_into_final_third'}).text.strip()
            player_set[player_key]['passes_into_penalty_area'] = table.find('td', attrs={'data-stat':'passes_into_penalty_area'}).text.strip()
            player_set[player_key]['crosses_into_penalty_area'] = table.find('td', attrs={'data-stat':'crosses_into_penalty_area'}).text.strip()
            # Ghi đè giá trị progressive_passes từ bảng này (như class cũ)
            player_set[player_key]['progressive_passes'] = table.find('td', attrs={'data-stat':'progressive_passes'}).text.strip()
    driver.quit()


def update_Set_Goal_And_Shot_Creation_Data(player_set):
    driver = webdriver.Chrome()
    url = 'https://fbref.com/en/comps/9/gca/Premier-League-Stats'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    x = soup.find('table', attrs={'id': 'stats_gca'})
    cnt = 0
    for i in range(600):
        cnt+=1
        if cnt==26:
            cnt=0
            continue
        table = x.find('tr', attrs={'data-row':f'{str(i)}'})
        if not table: continue

        name = table.find('td', attrs={'data-stat':'player'}).text.strip()
        team = table.find('td', attrs={'data-stat':'team'}).text.strip()
        player_key = str(name) + str(team)

        if player_key in player_set:
            player_set[player_key]['sca'] = table.find('td', attrs={'data-stat':'sca'}).text.strip()
            player_set[player_key]['sca_per90'] = table.find('td', attrs={'data-stat':'sca_per90'}).text.strip()
            player_set[player_key]['gca'] = table.find('td', attrs={'data-stat':'gca'}).text.strip()
            player_set[player_key]['gca_per90'] = table.find('td', attrs={'data-stat':'gca_per90'}).text.strip()
    driver.quit()

def update_Set_Defensive_Actions_Data(player_set):
    driver = webdriver.Chrome()
    url = 'https://fbref.com/en/comps/9/defense/Premier-League-Stats'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    x = soup.find('table', attrs={'id': 'stats_defense'})
    cnt = 0
    for i in range(600):
        cnt+=1
        if cnt==26:
            cnt=0
            continue
        table = x.find('tr', attrs={'data-row':f'{str(i)}'})
        if not table: continue

        name = table.find('td', attrs={'data-stat':'player'}).text.strip()
        team = table.find('td', attrs={'data-stat':'team'}).text.strip()
        player_key = str(name) + str(team)

        if player_key in player_set:
            player_set[player_key]['tackles'] = table.find('td', attrs={'data-stat':'tackles'}).text.strip()
            player_set[player_key]['tackles_won'] = table.find('td', attrs={'data-stat':'tackles_won'}).text.strip()
            player_set[player_key]['challenges'] = table.find('td', attrs={'data-stat':'challenges'}).text.strip()
            player_set[player_key]['challenges_lost'] = table.find('td', attrs={'data-stat':'challenges_lost'}).text.strip()
            player_set[player_key]['blocks'] = table.find('td', attrs={'data-stat':'blocks'}).text.strip()
            player_set[player_key]['blocked_shots'] = table.find('td', attrs={'data-stat':'blocked_shots'}).text.strip()
            player_set[player_key]['blocked_passes'] = table.find('td', attrs={'data-stat':'blocked_passes'}).text.strip()
            player_set[player_key]['interceptions'] = table.find('td', attrs={'data-stat':'interceptions'}).text.strip()
    driver.quit()

def update_Set_Possession(player_set):
    driver = webdriver.Chrome()
    url = 'https://fbref.com/en/comps/9/possession/Premier-League-Stats'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    x = soup.find('table', attrs={'id': 'stats_possession'})
    cnt = 0
    for i in range(600):
        cnt+=1
        if cnt==26:
            cnt=0
            continue
        table = x.find('tr', attrs={'data-row':f'{str(i)}'})
        if not table: continue

        name = table.find('td', attrs={'data-stat':'player'}).text.strip()
        team = table.find('td', attrs={'data-stat':'team'}).text.strip()
        player_key = str(name) + str(team)

        if player_key in player_set:
            player_set[player_key]['touches'] = table.find('td', attrs={'data-stat':'touches'}).text.strip()
            player_set[player_key]['touches_def_pen_area'] = table.find('td', attrs={'data-stat':'touches_def_pen_area'}).text.strip()
            player_set[player_key]['touches_def_3rd'] = table.find('td', attrs={'data-stat':'touches_def_3rd'}).text.strip()
            player_set[player_key]['touches_mid_3rd'] = table.find('td', attrs={'data-stat':'touches_mid_3rd'}).text.strip()
            player_set[player_key]['touches_att_3rd'] = table.find('td', attrs={'data-stat':'touches_att_3rd'}).text.strip()
            player_set[player_key]['touches_att_pen_area'] = table.find('td', attrs={'data-stat':'touches_att_pen_area'}).text.strip()
            player_set[player_key]['take_ons'] = table.find('td', attrs={'data-stat':'take_ons'}).text.strip()
            player_set[player_key]['take_ons_won_pct'] = table.find('td', attrs={'data-stat':'take_ons_won_pct'}).text.strip()
            player_set[player_key]['take_ons_tackled_pct'] = table.find('td', attrs={'data-stat':'take_ons_tackled_pct'}).text.strip()
            player_set[player_key]['carries'] = table.find('td', attrs={'data-stat':'carries'}).text.strip()
            player_set[player_key]['carries_progressive_distance'] = table.find('td', attrs={'data-stat':'carries_progressive_distance'}).text.strip()
            player_set[player_key]['carries_into_final_third'] = table.find('td', attrs={'data-stat':'carries_into_final_third'}).text.strip()
            player_set[player_key]['carries_into_penalty_area'] = table.find('td', attrs={'data-stat':'carries_into_penalty_area'}).text.strip()
            player_set[player_key]['miscontrols'] = table.find('td', attrs={'data-stat':'miscontrols'}).text.strip()
            player_set[player_key]['dispossessed'] = table.find('td', attrs={'data-stat':'dispossessed'}).text.strip()
            player_set[player_key]['passes_received'] = table.find('td', attrs={'data-stat':'passes_received'}).text.strip()
            # Ghi đè progressive_carries từ bảng này (theo logic export của class cũ)
            # Thực tế class cũ export 'progressive_carries' lấy từ bảng standard và một giá trị nữa từ bảng possession
            # Code này sẽ ghi đè giá trị 'progressive_carries' ban đầu bằng giá trị mới tìm thấy ở đây nếu logic cũ là vậy.
            # Tuy nhiên, nhìn vào class thì có vẻ cả 'progressive_carries' và 'carries_progressive_distance' đều được lưu riêng.
            # Giả sử không có ghi đè ở đây, nếu cần, hãy cập nhật logic.
    driver.quit()


def update_Set_Miscellaneous_Data(player_set):
    driver = webdriver.Chrome()
    url = 'https://fbref.com/en/comps/9/misc/Premier-League-Stats'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    x = soup.find('table', attrs={'id': 'stats_misc'})
    cnt = 0
    for i in range(600):
        cnt+=1
        if cnt==26:
            cnt=0
            continue
        table = x.find('tr', attrs={'data-row':f'{str(i)}'})
        if not table: continue

        name = table.find('td', attrs={'data-stat':'player'}).text.strip()
        team = table.find('td', attrs={'data-stat':'team'}).text.strip()
        player_key = str(name) + str(team)

        if player_key in player_set:
            player_set[player_key]['fouls'] = table.find('td', attrs={'data-stat':'fouls'}).text.strip()
            player_set[player_key]['fouled'] = table.find('td', attrs={'data-stat':'fouled'}).text.strip()
            player_set[player_key]['offsides'] = table.find('td', attrs={'data-stat':'offsides'}).text.strip()
            player_set[player_key]['crosses'] = table.find('td', attrs={'data-stat':'crosses'}).text.strip()
            player_set[player_key]['ball_recoveries'] = table.find('td', attrs={'data-stat':'ball_recoveries'}).text.strip()
            player_set[player_key]['aerials_won'] = table.find('td', attrs={'data-stat':'aerials_won'}).text.strip()
            player_set[player_key]['aerials_lost'] = table.find('td', attrs={'data-stat':'aerials_lost'}).text.strip()
            player_set[player_key]['aerials_won_pct'] = table.find('td', attrs={'data-stat':'aerials_won_pct'}).text.strip()
            # Ghi đè progressive_passes_received từ bảng này (theo logic export của class cũ)
            # Tương tự progressive_carries, cần xem xét lại logic nếu cần.
            # Giả sử không ghi đè ở đây.
    driver.quit()

def export(player_set_dict):
    playerlist = list(player_set_dict.values())
    playerlist.sort(key=get_player_name_from_dict)
    result = []
    for player_dict in playerlist:
        result.append(export_player_data(player_dict)) 
    column_names = ['Name', 'Nation', 'Team', 'Position', 'Age', 'Playing Time: matches played', 'Playing Time: starts', 'Playing Time: minutes', 'Performance: goals', 'Performance: assists',
                'Performance: yellow cards', 'Performance: red cards', 'Expected: expected goals (xG)', 'Expected: expedted Assist Goals (xAG)', 'Progression: PrgC', 'Progression: PrgP', 'Progression: PrgR',
                'Per 90 minutes: Gls', 'Per 90 minutes: Ast', 'Per 90 minutes: xG', 'Per 90 minutes: xGA', 'Performance: goals against per 90mins (GA90)', 'Performance: Save%', 'Performance: CS%',
                'Penalty Kicks: penalty kicks Save%', 'Standard: shoots on target percentage (SoT%)', 'Standard: Shoot on Target per 90min (SoT/90)', 'Standard: goals/shot (G/sh)',
                'Standard: average shoot distance (Dist)', 'Total: passes completed (Cmp)', 'Total: Pass completion (Cmp%)',
                'Total: progressive passing distance (TotDist)', 'Short: Pass completion (Cmp%)', 'Medium: Pass completion (Cmp%)', 'Long: Pass completion (Cmp%)', 'Expected: key passes (KP)',
                'Expected: pass into final third (1/3)', 'Expected: pass into penalty area (PPA)', 'Expected: CrsPA', 'Expected: PrgP', 'SCA: SCA', 'SCA: SCA90', 'GCA: GCA', 'GCA: GCA90',
                'Tackles: Tkl', 'Tackles: TklW', 'Challenges: Att', 'Challenges: Lost', 'Blocks: Blocks', 'Blocks: Sh', 'Blocks: Pass', 'Blocks: Int',
                'Touches: Touches', 'Touches: Def Pen', 'Touches: Def 3rd', 'Touches: Mid 3rd', 'Touches: Att 3rd', 'Touches: Att Pen',
                'Take-Ons: Att', 'Take-Ons: Succ%', 'Take-Ons: Tkld%', 'Carries: Carries', 'Carries: ProDist', 'Carries: ProgC', 'Carries: 1/3',
                'Carries: CPA', 'Carries: Mis', 'Carries: Dis', 'Receiving: Rec', 'Receiving: PrgR', 'Performance: Fls', 'Performance: Fld', 'Performance: Off', 'Performance: Crs',
                'Performance: Recov', 'Aerial Duels: Won', 'Aerial Duels: Lost', 'Aerial Duels: Won%'] 

    dataFrame = pd.DataFrame(result , columns=column_names) #
    print("DataFrame được tạo:")
    print(dataFrame.head()) # In ra vài dòng đầu để kiểm tra
    os.makedirs('P1_RES', exist_ok=True)
    file_path = os.path.join('P1_RES', 'results.csv')
    print(f"Đang lưu kết quả vào file {'results.csv'}...")
    dataFrame.to_csv(file_path, index=False, encoding='utf-8-sig') #
    print(f"Đã lưu thành công vào {'results.csv'}.")

def Problem_1():
    print("Starting to retrieve basic data...")
    player_set_dict = create_Set_Players()
    print(f"Retrieved basic data for {len(player_set_dict)} players.")

    print("Updating goalkeeping data...")
    update_Set_Goalkeeping(player_set_dict)
    print("Updating shooting data...")
    update_Set_Shooting(player_set_dict)
    print("Updating passing data...")
    update_Set_Passing(player_set_dict)
    print("Updating goal and shot creation data...")
    update_Set_Goal_And_Shot_Creation_Data(player_set_dict)
    print("Updating defensive actions data...")
    update_Set_Defensive_Actions_Data(player_set_dict)
    print("Updating possession data...")
    update_Set_Possession(player_set_dict)
    print("Updating miscellaneous data...")
    update_Set_Miscellaneous_Data(player_set_dict)
    print("Data update completed.")

    export(player_set_dict)
    print("Program completed.")

if __name__ == '__main__':
    tracemalloc.start()
    start = time.time()
    Problem_1() 
    end = time.time()
    print(f"Thời gian chạy: {end - start:.6f} giây")
    current, peak = tracemalloc.get_traced_memory()
    print(f"Bộ nhớ hiện tại: {current / 1024 ** 2:.2f} MB")
    print(f"Bộ nhớ đạt đỉnh: {peak / 1024 ** 2:.2f} MB")
    tracemalloc.stop()