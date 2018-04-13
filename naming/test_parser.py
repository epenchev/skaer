import parser
import unittest
import sys


class TestVideoParser(unittest.TestCase):
    def test_parse_video(self):
        if sys.platform.startswith('win'):
            path = '\\server\\Movies\\Brave (2007)\\Brave (2006).mkv'
        else:
            path = '/server/Movies/Brave (2007)/Brave (2006).mkv'
        video_info = parser.parse_video(path)
        self.assertEqual(video_info['name'], 'Brave')
        self.assertEqual(video_info['container'], 'mkv')
        self.assertEqual(video_info['year'], 2006)


class TestVideoStackParser(unittest.TestCase):
    def test_parse_simple_stack(self):
        files = (
            'Bad Boys (2006) part1.mkv',
            'Bad Boys (2006) part2.mkv',
            'Bad Boys (2006) part3.mkv',
            'Bad Boys (2006) part4.mkv',
            'Bad Boys (2006)-trailer.mkv',
        )
        stack = parser.parse_video_stack(files)
        print(stack)
        self.assertEqual(len(stack), 1)

    def test_parse_dual_stacks(self):
        files = (
            'Bad Boys (2006) part1.mkv',
            'Bad Boys (2006) part2.mkv',
            'Bad Boys (2006) part3.mkv',
            'Bad Boys (2006) part4.mkv',
            'Bad Boys (2006)-trailer.mkv',
            '300 (2006) part1.mkv',
            '300 (2006) part2.mkv',
            '300 (2006) part3.mkv',
            '300 (2006)-trailer.mkv'
        )
        stacks = parser.parse_video_stack(files)
        for s in stacks:
            print(s)
        self.assertEqual(len(stacks), 2)
    
    def test_dirty_names(self):
        files = (
            "Bad Boys (2006).part1.stv.unrated.multi.1080p.bluray.x264-rough.mkv",
            "Bad Boys (2006).part2.stv.unrated.multi.1080p.bluray.x264-rough.mkv",
            "Bad Boys (2006).part3.stv.unrated.multi.1080p.bluray.x264-rough.mkv",
            "Bad Boys (2006).part4.stv.unrated.multi.1080p.bluray.x264-rough.mkv",
            "Bad Boys (2006)-trailer.mkv"
        )
        stack = parser.parse_video_stack(files)
        print(stack)
        self.assertEqual(len(stack), 1)
        #TestStackInfo(result.Stacks[0], "Bad Boys (2006).stv.unrated.multi.1080p.bluray.x264-rough", 4);

    
    def test_parse_mixed_expressions(self):
        files = (
            'Bad Boys (2006) part1.mkv',
            'Bad Boys (2006) part2.mkv',
            'Bad Boys (2006) part3.mkv',
            'Bad Boys (2006) part4.mkv',
            'Bad Boys (2006)-trailer.mkv',
            '300 (2006) parta.mkv',
            '300 (2006) partb.mkv',
            '300 (2006) partc.mkv',
            '300 (2006) partd.mkv',
            '300 (2006)-trailer.mkv',
            '300a.mkv',
            '300b.mkv',
            '300c.mkv',
            '300-trailer.mkv'
        )
        stacks = parser.parse_video_stack(files)
        for s in stacks:
            print(s)
        self.assertEqual(len(stacks), 3)


if __name__ == '__main__':
    unittest.main()
