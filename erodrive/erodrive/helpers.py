import configparser
from configparser import NoOptionError, NoSectionError
from django.conf import settings
import json


def config(key: str, value: str = None, section: str = 'APP', file_name: str = 'base'):
    """
    get/write configure file
    GET MODE: only passing key
    SET MODE: key and value
    If section doesn't exists,it will automatic create an "APP" section.
    :param key:
    :param value:
    :param section:
    :param file_name:
    :return: string
    """
    if key is '':
        return None

    config_file_path = settings.PROJECT_ROOT + '/config/' + file_name + '.ini'
    parser = configparser.RawConfigParser()
    parser.read(config_file_path)

    if section not in parser.sections():
        if value is None:
            # In last version will throw an exception there,
            # but it will make thing more complicated.
            # So i decide to create a default section if doesn't exists.
            # raise NoSectionError(section)
            return config(key='foo', value='bar', section=section)
        else:
            # 创建新Section
            parser.add_section(section)

    # 如果只有key的话就是获取配置
    if value is None:
        try:
            return parser.get(section, key)
        except NoOptionError:
            return None

    # 写入
    parser.set(section, key, value)
    with open(config_file_path, 'w') as config_file:
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