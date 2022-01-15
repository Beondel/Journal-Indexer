import configparser
from datetime import datetime
import os.path
from os import makedirs
import subprocess
import sys
import zoneinfo
import _pickle as pickle
from zoneinfo import ZoneInfo

index_path = ".journal_index.pkl"

month_map = {
    'Jan': '01.January',
    'Feb': '02.February',
    'Mar': '03.March',
    'Apr': '04.April',
    'May': '05.May',
    'Jun': '06.June',
    'Jul': '07.July',
    'Aug': '08.August',
    'Sep': '09.September',
    'Oct': '10.October',
    'Nov': '11.November',
    'Dec': '12.December'
}

def main():
    create_log(index_path)

def load_indexes(path: str) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            dict_a = pickle.load(f)
            dict_b = pickle.load(f)
            return dict_a, dict_b
    else:
        return {}, {}

# dictionary a: mappings from tag to filenames
# dictionary b: mappings from filename to tags
def return_indexes(path: str, dict_a: dict[str, list[str]], dict_b: dict[str, list[str]]) -> None:
    with open(path, 'wb+') as f:
        pickle.dump(dict_a, f)
        pickle.dump(dict_b, f)

def create_log(path_to_index: str) -> None:
    config = configparser.ConfigParser()
    config.read(".config.ini")
    log_name = datetime.now(ZoneInfo(config['datetime']['timezone'])).strftime("%b-%d-%Y")
    log_location = get_location_from_log_name(log_name)
    
    a, b = load_indexes(path_to_index)
    if log_name not in b.keys():
        b[log_name] = []
    
    makedirs(log_location, exist_ok=True)
    subprocess.run(['touch', f'{log_location}/{log_name}'])
    print(f"Added new log {log_name}")
    subprocess.run(['open', '-e', f'{log_location}/{log_name}'])
    return_indexes(index_path, a, b)

def help():
    pass

def set_timezone(timezone: str) -> None:
    if timezone not in zoneinfo.available_timezones():
        print(f'{timezone} is not a valid timezone by the IANA standard. Please refer to https://en.wikipedia.org/w/index.php?title=List_of_tz_database_time_zones for a list of valid timezones (use one from the "TZ database name" column)')
    else:
        config = configparser.ConfigParser()
        config.read(".config.ini")
        config['datetime']['timezone'] = timezone

        with open('.config.ini', 'w') as config_file:
            config.write(config_file)

        print(f'Local timezone set to {timezone}')

def get_location_from_log_name(log_name: str) -> str:
    year = log_name[-4:]
    month = month_map[log_name[0:3]]
    return f'{year}/{month}'

if __name__ == "__main__":
    main()