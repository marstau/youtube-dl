# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    urlencode_postdata,
    ExtractorError,
)


class PornTrexIE(InfoExtractor):
    _NETRC_MACHINE = 'porntrex'
    _VALID_URL = r'https?://(?:www\.)?porntrex\.com/video/(?P<id>[0-9]+)/'
    _TEST = {
        'url': 'https://www.porntrex.com/video/350451/naomi-woods-the-list',
        'info_dict': {
            'id': '350451',
            'ext': 'mp4',
            'title': 'Naomi Woods - The List in 4k',
            'uploader': 'delman',
            'description': 'Naomi Woods The List',
            'url': 'https://www.porntrex.com/get_file/7/5223e8c2d6a378f22eccc8fd8e881746005ebc9d40/350000/350451/350451_2160p.mp4'
        }
    }

    def _login(self):
        username, password = self._get_login_info()
        if username is None:
            return

        login_page = self._download_webpage(
            'https://www.porntrex.com/login/', None, 'Downloading login page')

        login_form = self._hidden_inputs(login_page)

        login_form.update({
            'username': username.encode('utf-8'),
            'pass': password.encode('utf-8'),
            'remember_me': str(1).encode('utf-8'),
        })

        login_page = self._download_webpage(
            'https://www.porntrex.com/ajax-login/', None,
            note='Logging in',
            data=urlencode_postdata(login_form))

        if re.search(r'generic-error hidden', login_page):
            raise ExtractorError(
                'Unable to login, incorrect username and/or password',
                expected=True)

    def _real_initialize(self):
        self._login()

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        private_string = 'Only active members can watch private videos.'
        is_video_private_regex = re.compile(private_string)
        if re.findall(is_video_private_regex, webpage):
            self.raise_login_required()

        title = self._html_search_regex(
            r'<title>(.+?)</title>', webpage, 'title',)
        url2_regex = re.compile("'(https://www.porntrex.com/get_file/.*?)/'")
        url2 = re.findall(url2_regex, webpage)
        uploader_regex = re.compile(
            r'<a href="https://www.porntrex.com/members/[0-9]+?/">(.+?)</a>',
            re.DOTALL)
        uploader = re.findall(uploader_regex, webpage)[0].strip()
        thumbnails_regex = re.compile(r'href="(http.*?/screenshots/\d+.jpg/)"')
        thumbnails_list = re.findall(thumbnails_regex, webpage)
        thumbnails = []
        for thumbs in thumbnails_list:
            thumbnails.append({'url': thumbs})
        formats = []
        for x, _ in enumerate(url2):
            formats.append({'url': url2[x],
                            'ext': url2[x].split('.')[-1],
                            'protocol': url2[x].split(':')[0],
                            })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': self._og_search_description(webpage),
            'uploader': uploader,
            'thumbnails': thumbnails,
            'formats': formats,
        }


class PornTrexPlayListIE(InfoExtractor):
    _NETRC_MACHINE = 'porntrex'
    _VALID_URL = \
        r'https?://(?:www\.)?porntrex\.com/playlists/(?P<id>[0-9]+)/'
    _TEST = {
        'url': 'https://www.porntrex.com/playlists/31075/2016-collection/',
        'id': '31075',
        'title': 'FTVGirls 2016 Collection',
        'info_dict': {
            'id': '345462',
            'ext': 'mp4',
            'uploader': 'publicgirls',
            'title': 'FTVGirls.16.05 - Adria Part 2',
            'description': 'https://www.indexxx.com/models/121033/adria-rae/',
        }
    }

    def _login(self):
        username, password = self._get_login_info()
        if username is None:
            return

        login_page = self._download_webpage(
            'https://www.porntrex.com/login/', None, 'Downloading login page')

        login_form = self._hidden_inputs(login_page)

        login_form.update({
            'username': username.encode('utf-8'),
            'pass': password.encode('utf-8'),
            'remember_me': str(1).encode('utf-8'),
        })

        login_page = self._download_webpage(
            'https://www.porntrex.com/ajax-login/', None,
            note='Logging in',
            data=urlencode_postdata(login_form))

        if re.search(r'generic-error hidden', login_page):
            raise ExtractorError(
                'Unable to login, incorrect username and/or password',
                expected=True)

    def _real_initialize(self):
        self._login()

    def _real_extract(self, url):
        playlist_id = self._match_id(url)
        webpage = self._download_webpage(url, playlist_id)

        get_all_urls_regex = re.compile('data-playlist-item="(.*?)"')
        all_urls = re.findall(get_all_urls_regex, webpage)

        entries = []
        for this_url in all_urls:
            entries.append({'_type': 'url',
                            'id': this_url.split('/')[4],
                            'url': this_url,
                            })

        return {
            '_type': 'playlist',
            'id': url.split('/')[4],
            'title': self._html_search_regex(
                r'<title>(.+?)</title>',
                webpage,
                'title',),
            'entries': entries,
        }
