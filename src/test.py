import configparser
from datetime import datetime
import os.path
import subprocess
import sys
import zoneinfo
import _pickle as pickle
from zoneinfo import ZoneInfo

index_path = ".journal_index.pkl"

def main():
    pass

def load_indexes(path: str) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            dict_a = pickle.load(f)
            dict_b = pickle.load(f)
            return (dict_a, dict_b)
    else:
        return ({}, {})

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
    
    a, b = load_indexes(path_to_index)
    if log_name in b.keys():
        print(f'log {log_name} already exists')
    else:
        b[log_name] = []

        print(f"Added new log {log_name}")
        subprocess.run(['touch', log_name])
        subprocess.run(['open', '-e', log_name])
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

if __name__ == "__main__":
    main()