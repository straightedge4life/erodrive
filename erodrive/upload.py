import os
import hashlib


def send(path: str, receive_path: str):

    # 文件总大小(字节)
    file_size = os.path.getsize(path)
    # 文件名
    file_name = path.split('/').pop()
    # 每个文件块大小(10M)
    each_piece_size = 327680 * 32
    # 余数，作为最后一块写入
    remainder = file_size % each_piece_size
    # 合数，保证能被each_piece_size整除
    composite_num = file_size - remainder
    # 本次需要遍历的次数 (不算最后一块)
    times = int(composite_num / each_piece_size)
    # 指针
    pointer = 0

    # 简单判断下
    if file_size < each_piece_size:
        print('文件太小啦')
        exit()

    if os.path.exists(receive_path + file_name):
        print('文件已存在')

    with open(path, 'rb') as f:
        # 原文件MD5
        orig_file_md5 = hashlib.md5(f.read()).hexdigest()
        for t in range(0, times):
            f.seek(pointer)
            pointer += each_piece_size
            receive(f.read(each_piece_size), receive_path, file_name)

        # 最后一块
        f.seek(pointer)
        new_file_md5 = receive(f.read(remainder), receive_path, file_name, True)
        if orig_file_md5 == new_file_md5:
            print('写入完成，校验成功')
            exit()
        else:
            print('MD5校验失败 原文件MD5: %s  新写入文件MD5: %s' % (orig_file_md5, new_file_md5))


def receive(file, receive_path: str, file_name: str, end=None):
    if not os.path.exists(receive_path):
        os.makedirs(receive_path)
    with open(receive_path + file_name, 'ab') as f:
        f.write(file)
    if end:
        with open(receive_path + file_name, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    else:
        return None


if __name__ == '__main__':
    send('C:/Users/Rob/Desktop/upload_file/1.exe', 'C:/Users/Rob/Desktop/upload_file/receive/')
