import parser
import unittest
import sys


class TestStringMethods(unittest.TestCase):

    def test_match_video(self):
        if sys.platform.startswith('win'):
            path = '\\server\\Movies\\Brave (2007)\\Brave (2006).mkv'
        else:
            path = '/server/Movies/Brave (2007)/Brave (2006).mkv'
        result = parser.match_video(path)
        self.assertEqual(len(result), 1)
        info = result[0]
        self.assertEqual(info['name'], 'Brave')
        self.assertEqual(info['container'], 'mkv')
        self.assertEqual(info['year'], 2006)

if __name__ == '__main__':
    unittest.main()
