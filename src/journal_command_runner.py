import configparser
from datetime import datetime
import os.path
from os import makedirs
import subprocess
import sys
import zoneinfo
import _pickle as pickle
from zoneinfo import ZoneInfo

INDEX_PATH = ".journal_index.pkl"

def main():
    a, b = load_indexes(INDEX_PATH)
    a['test tag'] = {'test1', 'test2'}
    a['test tag 2'] = {'test2', 'test1'}
    return_indexes(INDEX_PATH, a, b)


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

def create_log() -> None:
    config = configparser.ConfigParser()
    config.read(".config.ini")
    log_name = datetime.now(ZoneInfo(config['datetime']['timezone'])).strftime("%b-%d-%Y")
    log_location = get_location_from_log_name(log_name)
    
    a, b = load_indexes(INDEX_PATH)
    if log_name not in b.keys():
        b[log_name] = set()
        print(f"Added new log {log_name}")
    else:
        print(f'Opening existing log {log_name}')
    
    makedirs(log_location, exist_ok=True)
    subprocess.run(['touch', f'{log_location}/{log_name}'])
    subprocess.run(['open', '-e', f'{log_location}/{log_name}'])
    return_indexes(INDEX_PATH, a, b)

def delete_log(log_name: str) -> None:
    a, b = load_indexes(INDEX_PATH)
    if log_name not in b.keys():
        print(f'Log {log_name} doesn\'t exist')
    else:
        tags = b[log_name]
        for tag in tags:
            if tag in a.keys():
                a[tag].remove(log_name)
        del b[log_name]
        print(f'Deleted log {log_name}')
    
    return_indexes(INDEX_PATH, a, b)

def open_log(log_name: str) -> None:
    log_location = get_location_from_log_name(log_name)
    path = f'{log_location}/{log_name}'
    if not os.path.isfile(path):
        print(f'Path {log_name} doesn\'t exist, the log was either moved or does not exist')
    else:
        print(f'Opening log at {path}')
        subprocess.run(['open', '-e', f'{path}'])

def find_logs(tags: list[str]) -> None:
    a, b = load_indexes(INDEX_PATH)
    logs = []
    bad_tag = False
    for tag in tags:
        if tag not in a.keys():
            print('No logs exist with tag [' + tag + ']')
            bad_tag = True
        else:
            logs.append(a[tag])

    if bad_tag:
        return
    
    res = logs[0]
    for log in logs:
        res = res.intersection(log)

    print(f'Logs with tags {tags_list_string(tags)}:')
    for log in res:
        print(log)
    

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

def tags_list_string(tags: list[str]) -> str:
    res = f'[{tags[0]}]'
    for tag in tags[1:]:
        res += f', [{tag}]'
    return res

def get_location_from_log_name(log_name: str) -> str:
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

    if len(log_name) != 11 or log_name[0:3] not in month_map.keys() or not log_name[-4:].isdigit() or not log_name[4:6].isdigit():
        raise Exception(f'{log_name} is not in valid format. Example format: Aug-04-1997')

    year = log_name[-4:]
    month = month_map[log_name[0:3]]
    return f'{year}/{month}'

if __name__ == "__main__":
    main()