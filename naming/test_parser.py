import names_parser as parser
import sys


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        print(parser.is_video('\\server\\Movies\\Brave (2007)\\Brave (2006).mkv'))
        print(parser.parse_video('\\server\\Movies\\Brave (2007)\\Brave (2006).mkv'))
    else:
        print(parser.is_video('/server/Movies/Brave (2007)/Brave (2006).mkv'))
        print(parser.parse_video('/server/Movies/Brave (2007)/Brave (2006).mkv'))
