import os
import sys
import re

movie_db_api_key = 'aff5c411d31602d0f54a97b4b677d524'


def is_media_file(filepath):
    pass


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Missing path in arguments')
    path = sys.argv[1]
    for root, dirs, files in os.walk(path):
        for f in files:
            print(os.path.join(path, f))
            match = re.search(clean_date_time_expr, os.path.join(path, f))
            if match:
                if match.group(1):
                    print(match.group(1))
                if match.group(2):
                    print(match.group(2))

    sys.stdout.flush()


if __name__ == '__main__':
    main()
