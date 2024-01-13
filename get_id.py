import os
import requests
import json
from datetime import datetime, timedelta
import time

def get_month_range(year, month):
    # 计算月份的开始和结束日期时间
    start_date = datetime(year, month, 1, 0, 0, 0)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
    
    return start_date, end_date

def get_game_data(start_time, end_time, game_mode):
    api_url = f"https://5-data.amae-koromo.com/api/v2/pl4/games/{int(end_time.timestamp()) * 1000}/{int(start_time.timestamp()) * 1000}?limit=1000&descending=true&mode={game_mode}"
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit exceeded. Waiting for 100 seconds...")
        time.sleep(100)  # 出现429错误时等待100秒
        return get_game_data(start_time, end_time, game_mode)
    else:
        print(f"Error: Unable to fetch game data. Status code: {response.status_code}")
        return None

def save_to_json(data, filename, folder_path):
    # 创建文件夹
    os.makedirs(folder_path, exist_ok=True)

    # 保存为JSON文件
    with open(os.path.join(folder_path, filename), 'w') as json_file:
        json.dump(data, json_file, indent=4)

def calculate_matches(game_data):
    return len(game_data)

def timestamp_to_readable(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d_%H-%M-%S')

def main():
    # 读取配置文件
    with open("config.json", 'r') as config_file:
        config = json.load(config_file)

    # 计算月份的开始和结束日期时间
    start_date, end_date = get_month_range(config["input_year"], config["input_month"])

    # 循环遍历每一天
    current_date = start_date
    while current_date <= end_date:
        # 循环遍历每一天的四个时间段
        for quarter_day in range(4):
            # 计算每个四分之一天的开始和结束时间
            start_time = current_date + timedelta(days=quarter_day / 4)
            end_time = current_date + timedelta(days=(quarter_day + 1) / 4)

            # 获取游戏数据
            game_data = get_game_data(start_time, end_time, config["game_mode"])

            if game_data:
                # 计算对局数量
                matches_count = calculate_matches(game_data)

                # 转换时间戳为人类可读格式
                start_time_readable = timestamp_to_readable(start_time.timestamp() * 1000)
                end_time_readable = timestamp_to_readable(end_time.timestamp() * 1000)

                # 生成文件名，包含游戏模式、日期和对局数量
                filename = f"{start_time_readable}-{end_time_readable}-mode{config['game_mode']}-{matches_count}.json"

                # 生成文件夹路径（按日）
                folder_path = f"./sapk_data/{config['input_year']}/{config['input_month']:02d}/{current_date.day:02d}"

                # 检查文件是否已存在，如果存在则跳过获取数据的步骤
                if os.path.exists(os.path.join(folder_path, filename)):
                    print(f"File already exists: {filename} in {folder_path}")
                    continue

                # 保存为JSON文件，并放入相应文件夹
                save_to_json(game_data, filename, folder_path)

                print(f"Number of matches on {start_time.date()} (Quarter {quarter_day+1}/4): {matches_count}")
                print(f"Saved as {filename} in {folder_path}")
            else:
                print(f"Failed to fetch game data for {start_time.date()} (Quarter {quarter_day+1}/4).")

            time.sleep(10)  # 每次请求之间等待10秒

        # 移动到下一天
        current_date += timedelta(days=1)

if __name__ == "__main__":
    main()
