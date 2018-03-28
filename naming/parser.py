import os
import expressions as expr


def _parse_video(path):
    if not path:
        raise RuntimeError('Missing path')
    name = None
    container = None
    year = None
    filename, ext = os.path.splitext(path)
    if (ext is None) or (ext not in expr.video_extensions):
        return None
    container = ext.strip('.')
    name, year = expr.clean_year(path)
    # Do a second pas to extract name and year after cleaning the path string
    if not name or not year:
        name, year = expr.clean_year(expr.clean_string(path))
    name = os.path.split(name)[1]
    return {
        'name': name,
        'container': container,
        'year': year,
        'path': path
    }


def _parse_video_stack(files):
    pass


def _parse_video_dir(path):
    pass


def match_video(path):
    if os.path.isdir(path):
        return _parse_video_dir(path)
    else:
        video_info = _parse_video(path)
        return (video_info,)

def match_audio(path, is_dir):
    pass


