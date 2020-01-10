from django.core.management.base import BaseCommand
from repositories.OneDrive import OneDrive
import os
import asyncio
import time


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
            start_time = time.time()
            print('START TIME : %s' % str(start_time))

            self.upload_folder(local_path, remote_path)

            end_time = time.time()

            print('END TIME : %s ' % str(end_time))

            print('COST TIME : %s' % str(int(end_time - start_time)))
        else:
            print("ERROR:Argument [path] must be 'file' or 'folder'.")
            return None

    @staticmethod
    def upload_file(local_path: str, remote_path: str):
        one = OneDrive()
        res = one.upload(local_path, remote_path)
        print(res)

    @staticmethod
    async def async_upload_file(local_path: str, remote_path: str):
        await asyncio.sleep(1)
        one = OneDrive()
        res = one.upload(local_path, remote_path)
        print(res)
        print('Upload File' + local_path)

    def upload_folder(self, local_path: str, remote_path: str):

        if os.path.isfile(local_path):
            print('Please use upload file command.')
            exit()
        dir_list = os.listdir(local_path)
        folder_name = local_path.split('/').pop()

        # use async
        event_loop = asyncio.get_event_loop()
        upload_tasks = []
        for dir_item in dir_list:
            full_path = local_path + '/' + dir_item
            upload_path = remote_path + '/' + folder_name

            if os.path.isfile(full_path):
                upload_tasks.append(self.async_upload_file(full_path, upload_path))
            else:
                self.upload_folder(full_path, upload_path)

        event_loop.run_until_complete(asyncio.gather(*upload_tasks))




