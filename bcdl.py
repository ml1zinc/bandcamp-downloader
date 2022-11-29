#!/usr/bin/env python3
import sys
import os
import json
import argparse

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


def album_download(download_dir: str, url: URL, num: bool = False):
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


    directory_path = os.path.join(download_dir, album_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    download(directory_path, files_names, files_links, cover, num=num)


def main():
    '''Main take args from cli and setup app work

    '''

    default_num = False
    download_dir = _DEFAULT_DIR

    parser = argparse.ArgumentParser(prog='bcdl.py',
                                     description='Simple Bandcamp cli downloader')
    parser.add_argument('url', help='Url of album, discography or musician profile')
    parser.add_argument('-a', '--all', action='store_true', dest='is_discography', help='download discography of musician')
    parser.add_argument('-n', '--num', action='store_true', dest='is_enumerate', help='enumerate songs in albums')
    parser.add_argument('-p', '--path', nargs=1, type=str, help='download discography of musician')

    args = parser.parse_args()

    main_url: URL = args.url

    is_discography = args.is_discography
    default_num = args.is_enumerate
    path = args.path[0]

    if path is not None:
        download_dir = path


    if is_discography:
        domain = '.com'
        main_url = main_url[:main_url.rfind(domain) + len(domain)]

        discography_page = requests.get(main_url)
        soup = bs(discography_page.text, features="html.parser")
        urls = soup.findAll('li', {'data-band-id': True})
        band_name_loc = soup.find('p', {'id': "band-name-location"})

        if band_name_loc is None:
            print('[Error] Not found band info on page. May be invalide url')
            sys.exit()

        band_name = band_name_loc.find('span', {'class': 'title'}).text
        download_dir = os.path.join(download_dir, band_name)

        # main_url = main_url[:main_url.rfind('/')] if main_url.rfind('/') > main_url.rfind('.') else main_url

        for url in urls:
            album_download(download_dir, (f"{main_url}{url.find('a').attrs['href']}"), num=default_num)

    else:
        album_download(download_dir, main_url, num=default_num)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
