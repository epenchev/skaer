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

    def test_parse_video_stack(self):
        files = [
            'Bad Boys (2006) part1.mkv',
            'Bad Boys (2006) part2.mkv',
            'Bad Boys (2006) part3.mkv',
            'Bad Boys (2006) part4.mkv',
            'Bad Boys (2006)-trailer.mkv',
        ]
        stack = parser.parse_video_stack(files)
        self.assertEqual(len(stack), 1)

    def test_parse_dual_video_stacks(self):
        files = [
            'Bad Boys (2006) part1.mkv',
            'Bad Boys (2006) part2.mkv',
            'Bad Boys (2006) part3.mkv',
            'Bad Boys (2006) part4.mkv',
            'Bad Boys (2006)-trailer.mkv',
            '300 (2006) part1.mkv',
            '300 (2006) part2.mkv',
            '300 (2006) part3.mkv',
            '300 (2006)-trailer.mkv'
        ]
        stack = parser.parse_video_stack(files)
        print(stack)
        self.assertEqual(len(stack), 2)


if __name__ == '__main__':
    unittest.main()
