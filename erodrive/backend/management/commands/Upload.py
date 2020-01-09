from django.core.management.base import BaseCommand
from repositories.OneDrive import OneDrive
import os


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('mode', type=str)
        parser.add_argument('local_path', type=str)
        parser.add_argument('remote_path', type=str)

    def handle(self, *args, **options):
        mode = options.get('mode')
        local_path = options.get('local_path')
        remote_path = options.get('remote_path')
        if mode == 'file':
            self.upload_file(local_path, remote_path)
        elif mode == 'folder':
            self.upload_folder(local_path, remote_path)
        else:
            print("ERROR:Argument [path] must be 'file' or 'folder'.")
            return None

    def upload_file(self, local_path: str, remote_path: str):
        one = OneDrive()
        res = one.upload(local_path, remote_path)
        print(res)

    def upload_folder(self, local_path: str, remote_path: str):
        if os.path.isfile(local_path):
            print('Please use upload file command.')
            exit()
        dir_list = os.listdir(local_path)
        folder_name = local_path.split('/').pop()

        for dir_item in dir_list:
            full_path = local_path + '/' + dir_item
            upload_path = remote_path + '/' + folder_name

            if os.path.isfile(full_path):
                self.upload_file(full_path, upload_path)
            else:
                self.upload_folder(full_path, upload_path)





