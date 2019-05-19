#!/usr/bin/python3

import datetime
import pathlib
import re
import subprocess


def filedate(path: pathlib.Path) -> datetime.datetime:
    date_str = re.search(r'\d\d\d\d-\d\d-\d\d', str(path)).group()
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')

def compress_backups(directory: pathlib.Path):
    gz = directory / 'backups.7z'

    # add to archive
    #     $ 7za a <archive name> <filenames ...>
    args = ['7za', 'a', str(gz), str(directory / '*.pdf')]
    r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(r.stderr.decode())

    # delete old pdfs from the folder (they'll be kept in the archive though)
    *to_delete, most_recent = sorted(directory.glob('*pdf'), key=filedate) 
    for p in to_delete:
        p.unlink()

def convert_character_files(directory: pathlib.Path):
    def get_changed_files():
        args = ['git', 'status']
        r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for line in r.stdout.decode().split('\n'):
            match = re.search(r'modified:\s+(.*\.odt)', line)
            if match:
                yield pathlib.Path(match.group(1))

    def get_missing_files():
        """ yield any ODT files which don't have a PDF counterpart """
        for odt in directory.glob('*.odt'):
            if not odt.with_suffix('.pdf').is_file():
                yield odt

    def convert_file(fp: pathlib.Path):
        print(f'Converting {fp}...')
        args = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            str(fp.resolve()),
            '--outdir', str(directory)
        ]
        r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert p.with_suffix('.pdf').is_file(), r.stderr.decode()

    changed = set(get_changed_files())
    missing = set(get_missing_files())
    for p in set.union(changed, missing):
        convert_file(p)


if __name__ == '__main__':
    compress_backups(pathlib.Path('backups'))
    convert_character_files(pathlib.Path('Characters'))
