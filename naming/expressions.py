import re

explanation_words = (
    'ac3','dts','custom','dc','divx','divx5','dsr','dsrip','dutch','dvd','dvdrip','dvdscr',
    'dvdscreener','screener','dvdivx','cam','fragment','fs','hdtv','hdrip','hdtvrip','internal',
    'limited','multisubs','ntsc','ogg','ogm','pal','pdtv','proper','repack','rerip','retail',
    'cd[1-9]','r3','r5','bd5','se','svcd','swedish','german','read.nfo','nfofix','unrated','ws',
    'telesync','ts','telecine','tc','brrip','bdrip','480p','480i','576p','576i','720p','720i','1080p',
    '1080i','2160p','hrhd','hrhdtv','hddvd','bluray','x264','h264','xvid','xvidvd','xxx','www.www'
)

clean_string_expr = (
    re.compile(r'[ _\,\.\(\)\[\]\-]' + '(' + r'|'.join(explanation_words) + r'|\[.*\])' + r'([ _\,\.\(\)\[\]\-]|$)'),
    re.compile('[ _\,\.\(\)\[\]\-](3d|sbs|tab|hsbs|htab|mvc|\[.*\])([ _\,\.\(\)\[\]\-]|$)'),
    re.compile('(\[.*\])')
)

video_file_stack_expr = (
    re.compile(r'(.*?)([ _.-]*(?:cd|dvd|p(?:ar)?t|dis[ck])[ _.-]*[0-9]+)(.*?)(\\.[^.]+)$'),
    re.compile(r'(.*?)([ _.-]*(?:cd|dvd|p(?:ar)?t|dis[ck])[ _.-]*[a-d])(.*?)(\\.[^.]+)$'),
    re.compile(r'(.*?)([ ._-]*[a-d])(.*?)(\\.[^.]+)$')
)

year_expr = re.compile(r'(.+[^ _\,\.\(\)\[\]\-])'\
                        '[ _\.\(\)\[\]\-]+'\
                        '(19[0-9][0-9]|20[0-1][0-9])'\
                        '([ _\,\.\(\)\[\]\-][^0-9]|$)')

# Video file extensions
video_extensions = (
    '.m4v', '.3gp','.nsv','.ts','.ty','.strm','.rm','.rmvb','.m3u','.ifo','.mov','.qt','.divx','.xvid','.bivx',
    '.vob','.nrg','.img','.iso','.pva','.wmv','.asf','.asx','.ogm','.m2v','.avi','.bin','.dat','.dvr-ms',
    '.mpg','.mpeg','.mp4','.mkv','.avc','.vp3','.svq3','.nuv','.viv','.dv','.fli','.flv','.rar','.001','.wpl','.zip'
)

# Audio file extensions
audio_extensions = (
    '.nsv','.m4a','.flac','.aac','.strm','.pls','.rm','.mpa','.wav',
    '.wma','.ogg','.opus','.mp3','.mp2','.m3u','.mod','.amf','.669','.dmf','.dsm','.far','.gdm','.imf','.it',
    '.m15','.med','.okt','.s3m','.stm','.sfx','.ult','.uni','.xm','.sid','.ac3','.dts','.cue','.aif',
    '.aiff','.wpl','.ape','.mac','.mpc','.mp+','.mpp','.shn','.zip','.rar','.wv','.nsf','.spc','.gym',
    '.adplug','.adx','.dsp','.adp','.ymf','.ast','.afc','.hps','.xsp','.acc','.m4b','.oga','.dsf','.mka'
)

stub_extensions = ( '.disc', )

subtitle_file_extensions = ('.srt', '.ssa', '.ass', '.sub')

video_stub_types = {
    'dvd'   : 'dvd',
    'hddvd' : 'hddvd',
    'bluray': 'bluray',
    'brrip' : 'bluray',
    'bd25'  : 'bluray',
    'bd50'  : 'bluray',
    'vhs'   : 'vhs',
    'HDTV'  : 'tv',
    'PDTV'  : 'tv',
    'DSR'   : 'tv'
}

album_stacking_prefixes = ('disc', 'cd', 'disk', 'vol', 'volume')

video_extra_types = {
    r'(?:^|-|\.|_|\s)trailer': 'trailer',
    r'(?:^|-|\.|_|\s)sample' : 'sample',
}

video_3d_types = {
    'hsbs' : '3d',
    'sbs'  : '3d',
    'htab' : '3d',
    'tab'  : '3d'
}

def clean_year(path):
    """ Extract the year from the filename if present. """
    try:
        match = re.search(year_expr, path)
        name, year = match.group(1), int(match.group(2))
        return name, year
    except Exception as err:
        return tuple()


def clean_string(path):
    """ Clean the filename out. """
    for expr in clean_string_expr:
        try:
            found = re.search(expr, path)
            return path[0:path.find(found.group(1))]
        except Exception as err:
            continue
    return path
