import os
import re
from . import expressions as expr


class VideoFileParser(object):
    def __init__(self):
        pass

    @staticmethod
    def is_video_file(filename):
        for ext in expressions.video_file_extensions:
            if filename.endswith(ext):
                return True
        return False


    @staticmethod
    def parse_video_file(path):
        if not path:
            raise RuntimeError('missing path')
        name = None
        container = None
        year = None
        if not os.path.isdir(path):
            fname, fext = os.path.splitext(path)
            if fext not in expressions.video_file_extensions:
                return None
            container = fext.strip('.')
            try:
                name, year = expr.extract_date_time(path)
            else:
                for expr in expressions.clean_string_expr:
                    found = re.search(expr, path)
                    if found:
                        clean_path = path[0:path.find(found.group(1))]


    def parse_dir(self, path):
        pass
