import asyncio

class AsyncYouTubeDl(object):
    """ Async youtube-dl subprocess exec wrapper """
    def __init__(self, app, ffmpeg, youtubedl):
        self._app = app
        self._ffmpeg = ffmpeg
        self._youtubedl = ydl


    async def exec_youtubedl(self, opts):
        """ Execute youtube-dl in async subprocess """
        p = await asyncio.create_subprocess_shell(self._youtubedl + opts,
                                                  stdout=asyncio.subprocess.PIPE,
                                                  stderr=asyncio.subprocess.PIPE,
                                                  shell=True,
                                                  loop=self._app.loop)
        out, err = await p.communicate()
        return out.decode('utf-8'), err.decode('utf-8'), p.returncode


    async def get_download_url(self, url):
        """ Get the resource's url without downloading it. """
        return await self.exec_youtubedl(' -g %s' % url)


    async def download(self, url, extract_audio=False, audio_quality=9, out_name=None):
        """ Download target resource. """
        if extract_audio:
            opts = ' -x --audio-format mp3 --audio-quality %s' % audio_quality
            opts += '--ffmpeg-location %s' % self._ffmpeg
        if out_name:
            opts += ' -o %s' % out_name
        opts += ' %s' % url
        # Todo extract out the result filename in case out_name is not specfied
        return await self.exec_youtubedl(opts)
