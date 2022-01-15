import configparser
from datetime import datetime
import os.path
from os import makedirs
import subprocess
import sys
import zoneinfo
import _pickle as pickle
from zoneinfo import ZoneInfo
import argparse

INDEX_PATH = ".journal_index.pkl"
CONFIG_PATH = ".journal_config.ipi"
TODAY = ""

def main():
    try:
        load_config()
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        TODAY = datetime.now(ZoneInfo(config['datetime']['timezone'])).strftime("%b-%d-%Y")

        parser = argparse.ArgumentParser()
        parser.add_argument('action', type=str)
        parser.add_argument('--log', type=str)
        parser.add_argument('--tags', type=str, nargs='+')
        args = parser.parse_args()

        if args.action == 'create':
            create_log()
            exit()
        if args.action == 'delete':
            delete_log(args.log if args.log else TODAY)
            exit()
        if args.action == 'open':
            open_log(args.log if args.log else TODAY)
            exit()
        if args.action == 'find':
            if not args.tags:
                help()
                exit()
            find_logs(args.tags)
            exit()
        if args.action == 'get':
            get_tags(args.log if args.log else TODAY)
            exit()
        if args.action == 'add-tags':
            if not args.tags:
                help()
                exit()
            add_tags(args.log if args.log else TODAY, args.tags)
            exit()
        if args.action == 'remove-tags':
            if not args.tags:
                help()
                exit()
            remove_tags(args.log if args.log else TODAY, args.tags)
            exit()
        if args.action == 'help':
            help()
            exit()
        else:
            help()
    except Exception as e:
        help()
        raise(e)

def help():
    print('Available commands (log names are the in the form of Month-Day-Year and use the 3 letter month convention, e.g: Aug-04-1997)')
    print('journal create - creates a new journal entry for the day')
    print('journal delete <logname> - deletes the specified log')
    print('journal open <logname> - opens the specified log for reading and editing')
    print('journal find <tag1> <tag2> <tag3> ... - finds journals which contain ALL of the specified tags; tags can be numerous')
    print('journal get <logname> - prints the log and its associated tags')
    print('journal add-tags [--log <logname>] <tag1> <tag2> <tag3> ... - adds the specified tags to today\'s log, can optionally specify a particular log with --log; tags can be numerous')
    print('journal remove-tags [--log <logname>] <tag1> <tag2> <tag3> ... - removes the specified tags from today\'s log, can optionally specify a particular log with --log; tags can be numerous')
    print('journal help - print this')

def load_indexes() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    if os.path.isfile(INDEX_PATH):
        with open(INDEX_PATH, 'rb') as f:
            dict_a = pickle.load(f)
            dict_b = pickle.load(f)
            return dict_a, dict_b
    else:
        return {}, {}

def return_indexes(dict_a: dict[str, list[str]], dict_b: dict[str, list[str]]) -> None:
    with open(INDEX_PATH, 'wb+') as f:
        pickle.dump(dict_a, f)
        pickle.dump(dict_b, f)

def load_config():
    if not os.path.isfile(CONFIG_PATH):
        subprocess.run(['touch', f'{CONFIG_PATH}'])
        config = configparser.ConfigParser()
        config['datetime'] = {'timezone': 'America/New_York'}
        
        with open(CONFIG_PATH, 'w') as config_file:
            config.write(config_file)

def create_log() -> None:
    
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    log_name = datetime.now(ZoneInfo(config['datetime']['timezone'])).strftime("%b-%d-%Y")
    log_location = get_location_from_log_name(log_name)
    
    a, b = load_indexes()
    if log_name not in b.keys():
        b[log_name] = set()
        print(f"Added new log {log_name}")
    else:
        print(f'Opening existing log {log_name}')
    
    makedirs(log_location, exist_ok=True)
    subprocess.run(['touch', f'{log_location}/{log_name}'])
    subprocess.run(['open', '-e', f'{log_location}/{log_name}'])
    return_indexes(a, b)

def delete_log(log_name: str) -> None:
    a, b = load_indexes()
    if log_name not in b.keys():
        print(f'{log_name} doesn\'t exist')
    else:
        tags = b[log_name]
        for tag in tags:
            if tag in a.keys():
                a[tag].remove(log_name)
        del b[log_name]

        subprocess.run(['rm', f'{get_location_from_log_name(log_name)}/{log_name}'])

        print(f'Deleted log {log_name}')
    
    return_indexes(a, b)

def open_log(log_name: str) -> None:
    log_location = get_location_from_log_name(log_name)
    path = f'{log_location}/{log_name}'
    if not os.path.isfile(path):
        print(f'Path {log_name} doesn\'t exist, the log was either moved or does not exist')
    else:
        print(f'Opening log at {path}')
        subprocess.run(['open', '-e', f'{path}'])

def get_tags(log: str) -> None:
    a, b = load_indexes()
    if log not in b.keys():
        print(f'{log} doesn\'t exist')
        return
    
    print(f'{log} --| {tags_list_string(list(b[log]))}')

def remove_tags(log: str, tags: list[str]) -> None:
    a, b = load_indexes()
    if log not in b.keys():
        print(f'{log} doesn\'t exist')
        return
    
    for tag in tags:
        b[log].discard(tag)
        if tag in a.keys():
            a[tag].discard(log)

    return_indexes(a, b)
    print(f'{log} --| {tags_list_string(list(b[log]))}')

def add_tags(log: str, tags: list[str]) -> None:
    a, b = load_indexes()
    if log not in b.keys():
        print(f'{log} doesn\'t exist')
        return
    
    for tag in tags:
        b[log].add(tag)
        if tag not in a.keys():
            a[tag] = set()
        a[tag].add(log)
    
    return_indexes(a, b)
    print(f'{log} --| {tags_list_string(list(b[log]))}')

def find_logs(tags: list[str]) -> None:
    a, b = load_indexes()
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

    for log in res:
        print(f'{log} --| {tags_list_string(list(b[log]))}')

def set_timezone(timezone: str) -> None:
    load_config()
    if timezone not in zoneinfo.available_timezones():
        print(f'{timezone} is not a valid timezone by the IANA standard. Please refer to https://en.wikipedia.org/w/index.php?title=List_of_tz_database_time_zones for a list of valid timezones (use one from the "TZ database name" column)')
    else:
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        config['datetime']['timezone'] = timezone

        with open(CONFIG_PATH, 'w') as config_file:
            config.write(config_file)

        print(f'Local timezone set to {timezone}')

def tags_list_string(tags: list[str]) -> str:
    if len(tags) == 0:
        return ''

    res = f'[{tags[0]}]'
    for tag in tags[1:]:
        res += f' [{tag}]'
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