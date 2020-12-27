import json
import requests
import os
import urllib3.request
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 '
                         'Safari/537.36',
           'Accept': '*/*',
           'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
           'Accept-Encoding': 'identity;q=1, *;q=0',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
           'Connection': 'keep-alive',
           'Cache-Control': 'max-age=0',
           'Sec - Fetch - Mode': 'no - cors',
           'Sec - Fetch - Site': 'same - site',
           'Referer': 'https://yesmangas1.com/mangas/'}

NON_FOLDER_SAFE = ['\\', '/', '|', '"', '<', '>', '*', '?', ':']
TRANSlATE_TABLE = {ord(char): u'' for char in NON_FOLDER_SAFE}


def _slugify2(text):
    text = text.translate(TRANSlATE_TABLE)
    text = u''.join(text)
    return text


class MangaScraper:
    def __init__(self):
        self.base_url = 'https://yesmangas1.com/mangas/page/'
        self.all_mangas = []
        self.all_chapters = []
        self.quantidade = 309
        self.browser = requests.session()
        self.browser.headers.update(HEADERS)

    def init(self, is_data_dumped):
        if is_data_dumped:
            self.all_mangas = self.get_data('all_mangas')
            self.all_chapters = self.get_data('all_chapters')
        else:
            self.set_all_mangas()
            self.set_manga_chapters()

        return self

    def set_manga_chapters(self):
        restante = len(self.all_mangas)

        for manga in self.all_mangas:
            chapters = []

            try:
                chapters = reversed(BeautifulSoup(self.browser.get(manga.get('url')).content, 'html5lib').
                                    find('div', attrs={'id': 'capitulos'}).find_all('a', attrs={'class': 'button'}))
            except AttributeError:
                print('ERRO NO INDEX: %d' % manga.get('index'))

            list_chapter = []

            for a in chapters:
                list_chapter.append({'chapter': a.text.capitalize(),
                                     'url': a.get('href')})

            self.all_chapters.append({'manga_index': manga.get('index'),
                                      'chapters': list_chapter})

            print('RESTANTES: %d' % restante)

            restante -= 1

    def set_all_mangas(self):
        index = 1

        for i in range(self.quantidade):
            mangas = BeautifulSoup(self.browser.get(self.base_url + str(i + 1)).content, 'html5lib'). \
                find_all('div', attrs={'class': 'two columns'})

            for item in mangas:
                btn = item.find('a', attrs={'class': 'button'})

                self.all_mangas.append({'index': index,
                                        'name': btn.get('title'),
                                        'image': item.find('img').get('data-path'),
                                        'url': btn.get('href')})
                index += 1

            print('PÁGINA: %d ' % (i + 1))

    def download_all_mangas(self, tamanho, paginated):
        for manga_chapter in self.all_chapters:
            if manga_chapter.get('manga_index') < tamanho * paginated:
                list_chapters = manga_chapter.get('chapters')

                path = 'C:\\Users\\artur\\Downloads\\MangaScraper\\' + _slugify2(
                    self.get_manga_by_index(manga_chapter.get('manga_index'))
                        .get('name')).strip()

                if not os.path.exists(path):
                    os.makedirs(path)

                for chapter in list_chapters:
                    chap_path = path + '\\' + chapter.get('chapter')

                    if not os.path.exists(chap_path):
                        os.makedirs(chap_path)

                    images = BeautifulSoup(requests.get(chapter.get('url'), headers=HEADERS).content, 'html5lib') \
                        .find('div', attrs={'class': 'read-slideshow'}).find_all('img')

                    i = 0
                    for item in images:
                        file_path = chap_path + '\\' + str(i).rjust(3, '0') + '.' + item.get('src').split('.')[-1]
                        i += 1

                        self.download_file(file_path, item.get('src'))

    def dump_all_mangas(self):
        assert len(self.all_mangas) > 0

        with open('all_mangas.json', 'w', encoding='utf-8') as f:
            json.dump({'array': self.all_mangas}, f, indent=2)

    def dump_all_chapters(self):
        assert len(self.all_chapters) > 0

        with open('all_chapters.json', 'w', encoding='utf-8') as f:
            json.dump({'array': self.all_chapters}, f, indent=2)

    def get_manga_by_index(self, index):
        for item in self.all_mangas:
            if item.get('index') == index:
                return item

    @staticmethod
    def get_data(name):
        with open(name + '.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get('array')

    @staticmethod
    def download_file(path, url):
        if not os.path.exists(path):
            r = requests.get(url, headers=HEADERS)

            with open(path, 'wb') as f:
                f.write(r.content)

            print('CONCLUIDO %s' % path)


if __name__ == '__main__':
    sc = MangaScraper().init(True)
    sc.download_all_mangas(30, 1)
