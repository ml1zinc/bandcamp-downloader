#!/usr/bin/env python3
import sys
import os
import json

import requests
from bs4 import BeautifulSoup as bs


URL = str
_DEFAULT_DIR = 'downloads/'


def download(directory_path: str, names: list[str], links: list[str], cover_url: URL, num: bool = False):
    '''Function download and save one song

    '''

    print(f'Downloading in "{directory_path}"')

    with open(f'{directory_path}/cover.jpg', 'wb') as cover_file:
        cover_file.write(requests.get(cover_url).content)

    if isinstance(names, str):
        names, links = [names], [links]

    for i, name in enumerate(names, start=1):

        if '/' in name:
            name = name.replace('/', '\\')

        if num:
            name = f'{i:0>2}. {name}'

        fname = f'{name}.mp3'
        file_path = os.path.join(directory_path, fname)

        with open(file_path, 'wb') as track:
            track.write(requests.get(links[i - 1]).content)
    print('Done')


def album_download(url: URL, num: bool = False):
    '''Function download full album page

    '''
    album_page = requests.get(url)
    soup = bs(album_page.text, features="html.parser")
    strings = json.loads(soup.findAll('script',
                                      {'type': "text/javascript",
                                       'data-tralbum': True}
                                      )[0].attrs['data-tralbum'])
    cover = soup.find('a', {'class': 'popupImage'}).attrs['href']

    album_info = strings['current']
    album_name = f"{album_info['release_date'].split()[2]} - {album_info['title']}"
    if '/' in album_name:
        album_name = album_name.replace('/', '\\')

    print(f'Album: {album_name}')

    files_names, files_links = [], []

    for string in strings['trackinfo']:
        files_names.append(string['title'])
        files_links.append(string['file']['mp3-128'])

    print(f'Songs: {files_names}')


    directory_path = os.path.join(_DEFAULT_DIR, album_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    download(album_name, files_names, files_links, cover, num=num)


def usage_help():
    '''Print help massage and exit

    '''
    print('bcdl.py [OPTIONS] [OPT_ARGUMENTS] [URL]\n',
          '-a         download all album, will slice url to <owner>.bandcamp.com\n',
          '-p         path, set directory, -p [PATH]\n',
          '-n         numbering files\n',
          )
    sys.exit(0)


def main():
    '''Main take args from cli and setup app work

    '''

    default_download = 'album'
    default_num = False

    if sys.argv[1].startswith('-') and len(sys.argv[1]) != 1:
        main_url: URL = sys.argv[-1]

        if 'a' in sys.argv[1] or '-a' in sys.argv[1:]:
            default_download = 'discography'
            index_of_domain_end = sys.argv[-1].index('.com') + 4  # 4 for adding lens of '.com'
            main_url = main_url[:index_of_domain_end]  # trim main_url to domain name

        if 'n' in sys.argv[1] or '-n' in sys.argv[1:]:
            default_num = True

        if '-p' in sys.argv[1:]:
            _DEFAULT_DIR = sys.argv[sys.argv.index('-p') + 1]

        if 'p' in sys.argv[1]:
            if sys.argv[2] != sys.argv[-1]:
                usage_help()
            _DEFAULT_DIR = sys.argv[2]

    else:
        usage_help()


    if default_download == 'album':
        album_download(main_url, num=default_num)

    elif default_download == 'discography':
        discography_page = requests.get(main_url)
        soup = bs(discography_page.text, features="html.parser")
        urls = soup.findAll('li', {'data-band-id': True})
        band_name = soup.find('p', {'id': "band-name-location"}).find('span', {'class': 'title'}).text
        _DEFAULT_DIR = os.path.join(_DEFAULT_DIR, band_name)

        main_url = main_url[:main_url.rfind('/')] if main_url.rfind('/') > main_url.rfind('.') else main_url

        for url in urls:
            album_download((f"{main_url}{url.find('a').attrs['href']}"), num=default_num)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
