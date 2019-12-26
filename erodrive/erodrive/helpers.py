import configparser
from configparser import NoOptionError, NoSectionError
from django.conf import settings
import json
import hashlib
import time
import random
import os


def config(key: str, value: str = None, section: str = 'APP', file_name: str = 'base', default = None):
    """
    get/write configure file
    GET MODE: only passing key
    SET MODE: key and value
    If section doesn't exists,it will automatic create an "APP" section.
    :param key:
    :param value:
    :param section:
    :param file_name:
    :param default:
    :return:
    """
    if key is '':
        return None

    config_path = settings.PROJECT_ROOT + '/config/'
    config_file_full_path = config_path + file_name + '.ini'
    parser = configparser.RawConfigParser()
    parser.read(config_file_full_path)

    if section not in parser.sections():
        if value is None:
            # In last version will throw an exception there,
            # but it will make thing more complicated.
            # So i decide to create a default section if doesn't exists.
            # raise NoSectionError(section)
            return config(key='foo', value='bar', section=section)
        else:
            # 创建新Section+
            parser.add_section(section)

    # 如果只有key的话就是获取配置
    if value is None:
        try:
            return parser.get(section, key)
        except NoOptionError:
            return default

    # 写入
    if not os.path.exists(config_path):
        os.makedirs(config_path)
        
    parser.set(section, key, value)
    with open(config_file_full_path, 'w') as config_file:
        parser.write(config_file)

    return None


def batch_store_config(data: dict = {}):
    """
    批量更改配置
    :param data:
    :return:
    """
    if not data:
        return None
    for c in data:
        config(key=c, value=data[c])
    return None


def list_format(data: list):
    """
    format the file list
    :param data:
    :return:
    """
    if not data:
        return []

    show_suffix_configure = eval(config('show'))
    show_suffix_list = []
    for val in show_suffix_configure:
        for t in val['suffix']:
            show_suffix_list.append(t)

    for val in data:
        if val.get('@microsoft.graph.downloadUrl'):
            val.update({'downloadUrl': val.get('@microsoft.graph.downloadUrl')})

        if val.get('folder'):
            val.update({'type': 'folder'})
            val.update({'show': False})
        else:
            val.update({'type': 'file'})
            suffix = val.get('name').split('.').pop()
            val.update({'show': True if suffix in show_suffix_list else False})

    return data


def path_format(path):
    """
    path format use by breadcrumbs
    :param path:
    :return:
    """
    if not path or path == '/':
        return [{'name': '/', 'path': '/'}]
    path_chain = ''
    path_list = []
    for p in path.split('/'):
        name = p if p else '/'
        if path_chain == '/':
            path_chain = path_chain + p
        else:
            path_chain = path_chain + '/' + p

        path_list.append({
            'name': name,
            'path': path_chain
        })
    return path_list


def md5(encrypt_string: str):
    return hashlib.md5(encrypt_string.encode('utf8')).hexdigest()


def generate_token(val: str, timestamp=None):
    salt = config('salt')
    if not timestamp:
        timestamp = str(int(time.time()))

    token = md5(md5(md5(val) + salt) + timestamp)
    return token, timestamp


def compare_web_token(auth_info: dict):
    access_code = str(config('access_code'))
    token, timestamp = generate_token(val=access_code, timestamp=auth_info.get('time'))
    return token == auth_info.get('token')


def compare_admin_token(auth_info: dict):
    password = str(config('password'))
    token, timestamp = generate_token(val=password, timestamp=auth_info.get('time'))
    return token == auth_info.get('token')


def rand_str(num: int = 1):
    timestamp = str(int(time.time()))
    string = 'zxcvbnmasdfghjklqwertyuiop?&^%$#@!_.' + timestamp
    random_string = ''
    if num <= 0:
        return random.choice(string)
    for i in range(0, num):
        random_string += random.choice(string)
    return random_string


def get_file_name(path: str):
    file_name = path.split('/').pop()
    return file_name
