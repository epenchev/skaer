import os
import sys


def get_bindir():
    """ Get the relative path to the bin directory. """
    bindir = 'bin'
    if not os.path.isdir(bindir):
        if sys.platform().startswith('linux'):
            bindir = r'../bin/'
        elif sys.platform().startswith('win'):
            bindir = r'..\bin'
    if os.path.isdir(bindir):
        return bindir
    raise RuntimeError('Invalid bin path')


def get_ffmpeg_path():
    """ Get the path to the ffmpeg binary. """
    ffmpeg_path = os.path.join(get_bindir(), 'ffmpeg-4.1-64bit', 'ffmpeg')
    if not os.path.isfile(ffmpeg_path):
        raise RuntimeError('Invalid ffmpeg path')
    return ffmpeg_path


def get_youtubedl_path():
    """ Get the path to the youtube-dl binary. """
    ydl_path = os.path.join(get_bindir(), 'youtube-dl')
    if not os.path.isfile(ydl_path):
        raise RuntimeError('Invalid youtube-dl path')
    return ydl_path


def get_tmpdir():
    """ Get the temporary dir storage path. """
    if sys.platform().startswith('linux'):
        return '/tmp'

