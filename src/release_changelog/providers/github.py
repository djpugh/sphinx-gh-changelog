import urllib

import requests

from release_changelog.providers._base import Provider, Release


class GitHubRelease(Release):

    def __init__(self, tag, body, url, previous_release=None):
        super().__init__(tag, body, url)
        self.previous_release = previous_release
        self.issue_url = url.split('releases')[0]+'issues/'
        self.author_url = 'https://www.github.com/'

    def parse_line(self, line):
        line = super().parse_line(line)
        line = ' '.join([self.convert_issue(self.convert_user(word)) for word in line.split(' ')])
        return line

    def convert_user(self, word):
        if word.startswith('@'):
            author = word[1:]
            word = f'`{word} <{self.author_url}{author}>`_'
        return word

    def convert_issue(self, word):
        if word.startswith('(#'):
            issue = word[2:-1]
            word = f'(`#{issue} <{self.issue_url}{issue}>`_)'
        return word

    def get_rst(self):
        rst = super().get_rst()
        # Add on the compare link
        if self.previous_release:
            rst = rst.rstrip('\n') + f" | `Full Changelog <https://github.com/djpugh/docserver/compare/{self.previous_release}...{self.tag}>`_\n"
        return rst


class GitHubProvider(Provider):

    @classmethod
    def convert(cls, url):
        releases = cls.get(url)
        return cls.get_rst(releases)

    @staticmethod
    def get(url):
        owner, repo = urllib.parse.urlparse(url).path.split('/')[1:3]
        repo_name = repo.split('.git')[0]
        uri = f"https://api.github.com/repos/{owner}/{repo_name}/releases"
        response = requests.get(uri)
        response.raise_for_status()
        releases = response.json()
        return releases

    @staticmethod
    def get_rst(releases):
        rst = []
        for i, release in enumerate(releases):
            previous_release = None
            try:
                previous_release = releases[i+1]['tag_name']
            except IndexError:
                pass
            rst.append(GitHubRelease(release['tag_name'], release['body'], release['html_url'], previous_release).get_rst())
        return '\n\n'.join(rst)

    @staticmethod
    def check_url(url):
        return 'github.com' in url
