from django.core.management.base import BaseCommand
from repositories.OneDrive import OneDrive


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
            print('Upload folder.')
        else:
            print("ERROR:Argument [path] must be 'file' or 'folder'.")
            return None

    def upload_file(self, local_path: str, remote_path: str):
        one = OneDrive()
        res = one.upload(local_path, remote_path)
        print(res)
