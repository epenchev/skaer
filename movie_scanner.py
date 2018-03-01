import os
import sys
import re

movie_db_api_key = 'aff5c411d31602d0f54a97b4b677d524'

clean_date_time_expr = \
    re.compile('(.+[^ _\,\.\(\)\[\]\-])[ _\.\(\)\[\]\-]+(19[0-9][0-9]|20[0-1][0-9])([ _\,\.\(\)\[\]\-][^0-9]|$)')

clean_string_expr = (
    re.compile('[ _\,\.\(\)\[\]\-](ac3|dts|custom|dc|divx|divx5|dsr|dsrip|dutch|dvd|dvdrip|dvdscr|dvdscreener|screener|dvdivx|cam|fragment|fs|hdtv|hdrip|hdtvrip|internal|limited|multisubs|ntsc|ogg|ogm|pal|pdtv|proper|repack|rerip|retail|cd[1-9]|r3|r5|bd5|se|svcd|swedish|german|read.nfo|nfofix|unrated|ws|telesync|ts|telecine|tc|brrip|bdrip|480p|480i|576p|576i|720p|720i|1080p|1080i|2160p|hrhd|hrhdtv|hddvd|bluray|x264|h264|xvid|xvidvd|xxx|www.www|\[.*\])([ _\,\.\(\)\[\]\-]|$)'),
    re.compile('[ _\,\.\(\)\[\]\-](3d|sbs|tab|hsbs|htab|mvc|\[.*\])([ _\,\.\(\)\[\]\-]|$)'),
    re.compile('(\[.*\])')
)


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
