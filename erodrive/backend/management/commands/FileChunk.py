from django.core.management.base import BaseCommand
from repositories.OneDrive import OneDrive
import os


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('local_path', type=str)

    def handle(self, *args, **options):
        local_path = options.get('local_path')
        # byte
        file_size = os.path.getsize(local_path)
        # byte 320k x 32 = 10MB
        each_chunk_size = 327680 * 32
        mod = file_size % each_chunk_size
        ccc = file_size - mod

        print('total size : %s' % str(file_size))
        print('each chunks size : %s' % str(each_chunk_size))
        print('mod : %s' % str(mod))
        print(str(ccc))
        print(str(ccc / each_chunk_size))

        exit()

        with open(local_path, 'rb') as f:
            f.seek(3)
            print(f.read(2))
