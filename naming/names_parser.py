import os
import re
import expressions as expr

def is_video(filename):
    for ext in expr.video_extensions:
        if filename.endswith(ext):
            return True
    return False


def parse_video(path, isdir=False):
    if not path:
        raise RuntimeError('missing path')
    name = None
    container = None
    year = None
    if not isdir:
        filename, ext = os.path.splitext(path)
        if ext not in expr.video_extensions:
            return None
        container = ext.strip('.')
        name, year = expr.clean_year(path)
        # Do a second pas to extract name and year after cleaning the path string
        if not name or not year:
            name, year = expr.clean_year(expr.clean_string(path))
    else:
        parse_dir(path)
    name = os.path.split(name)[1]
    return {
        'name': name,
        'container': container,
        'year': year,
        'path': path
    }


    def parse_dir(self, path):
        pass
