import parser
import unittest
import sys


class TestStringMethods(unittest.TestCase):

    def test_match_video(self):
        if sys.platform.startswith('win'):
            path = '\\server\\Movies\\Brave (2007)\\Brave (2006).mkv'
        else:
            path = '/server/Movies/Brave (2007)/Brave (2006).mkv'
        video_info = parser.parse_video(path)
        self.assertEqual(video_info['name'], 'Brave')
        self.assertEqual(video_info['container'], 'mkv')
        self.assertEqual(video_info['year'], 2006)

if __name__ == '__main__':
    unittest.main()
