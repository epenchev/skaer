import os
import re
import expressions


def parse_video_stub_type(path):
    # Check for stub type (dvd, bluray ..)
    filename, ext = os.path.splitext(path)
    if ext in expressions.stub_extensions:
        stbext = os.path.splitext(filename)[1].strip('.')
        for token in iter(expressions.video_stub_types):
            if token == stbext:
                return expressions.video_stub_types[token]
    return None


def parse_video_extra_type(path):
    # Check for extra type (trailer or sample)
    filename, ext = os.path.split(path)
    for re_token in iter(expressions.video_extra_types):
        if re.search(re_token, filename):
            return expressions.video_extra_types[re_token]
    return None


def parse_video_3d_type(path):
    # Check if video is 3D
    filename, ext = os.path.split(path)
    for token in expressions.video_3d_types:
        if filename.find(token):
            return expressions.video_3d_types[token]
    return None


def is_video_file(path):
    return os.path.splitext(path)[1].lower() in expressions.video_extensions


def is_stub_file(path):
    return os.path.splitext(path)[1].lower() in expressions.stub_extensions


def parse_video(path):
    if not path:
        raise RuntimeError('Missing path')
    if os.path.isdir(path):
        return None
    filename, ext = os.path.splitext(path)
    stubtype = None
    if ext not in expressions.video_extensions:
        stubtype = parse_video_stub_type(path)
    container = ext.strip('.')
    name, year = expressions.clean_year(path)
    format3D = parse_video_stub_type(path)
    xtype = parse_video_extra_type(path)
    # Do a second pas to extract name and year after cleaning the path string
    if not name or not year:
        name, year = expressions.clean_year(expressions.clean_string(path))
    name = os.path.split(name)[1]
    return {
        'name'      : name,
        'container' : container,
        'year'      : year,
        'path'      : path,
        'stubtype'  : stubtype,
        'format3D'  : format3D,
        'xtype'     : xtype
    }

def parse_video_stack(files):
    # Directories are skiped
    filelist = [f for f in files if is_video_file(f) or is_stub_file(f)]
    filelist.sort()
    stacks = []
    fidx_offset = 0
    stack_expressions = expressions.video_file_stack_expr

    for fidx in range(len(filelist)):
        fname = filelist[fidx]
        if fidx_offset:
            fidx += (fidx_offset - 1)
            if fidx == (len(filelist) - 1):
                break
        expr_index = 0

        while expr_index < len(stack_expressions):
            file_stack = {
                'name'  : None,
                'files' : []
            }
            expr = stack_expressions[expr_index]
            match = re.search(expr, fname)
            if not match:
                expr_index += 1
                continue
            fnext = fidx + 1

            while fnext < len(filelist):
                stack_files = []
                match_next = re.search(expr, filelist[fnext])
                if not match_next:
                    expr_index += 1
                    break
                title, volume, ignore = match.group(1), match.group(2), match.group(3)
                title_next, volume_next, ignore_next = match_next.group(1), match_next.group(2), match_next.group(3)

                if title == title_next \
                    and volume != volume_next and ignore == ignore_next \
                    and os.path.splitext(fname)[1] == os.path.splitext(filelist[fnext])[1]:

                    if not (file_stack['name']):
                        file_stack['name'] = title
                        file_stack['files'].append(fname)
                    file_stack['files'].append(filelist[fnext])
                else:
                    expr_index += 1
                    break
                fnext += 1

            if len(file_stack['files']):
                stacks.append(file_stack)
                fidx_offset += len(file_stack['files']) - 1
                break
    return stacks


def parse_video_list(files):
    pass


