import os
import expressions as expr


def parse_video_stub_type(path):
    # Check for stub type
    filename, ext = os.path.splitext(path)
    if ext in expr.stub_extensions:
        stbext = os.path.splitext(filename)[1].strip('.')
        for token in iter(expr.stub_types):
            if token == stbext:
                return expr.stub_types[token]
    return None


def parse_video_extra_type(path):
    'dsfdsfsd'.find()
    pass

def parse_video(path):
    if not path:
        raise RuntimeError('Missing path')
    name = None
    container = None
    year = None
    stubtype = None
    filename, ext = os.path.splitext(path)
    if (ext is None) or (ext not in expr.video_extensions):
        stubtype = parse_video_stub_type(path)
    container = ext.strip('.')

    name, year = expr.clean_year(path)
    # Do a second pas to extract name and year after cleaning the path string
    if not name or not year:
        name, year = expr.clean_year(expr.clean_string(path))
    name = os.path.split(name)[1]
    return {
        'name'      : name,
        'container' : container,
        'year'      : year,
        'path'      : path,
        'stubtype'  : stubtype
    }


def parse_video_stack(files):
    pass


def parse_video_dir(path):
    pass


def match_video(path):
    if os.path.isdir(path):
        return parse_video_dir(path)
    else:
        video_info = parse_video(path)
        return (video_info,)

def match_audio(path, is_dir):
    pass


