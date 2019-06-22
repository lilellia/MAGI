import argparse
import collections
import dataclasses
import datetime
import pathlib
import re
import typing
import warnings

import utils
from utils import PathLike

from tika import parser as tika_parser

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from fuzzywuzzy import fuzz


warnings.formatwarning = utils.warning_on_one_line


@dataclasses.dataclass
class _ChapterMatch:
    number: int
    title: str
    text: str


@dataclasses.dataclass
class _FrequencyMatch:
    word: str
    total: int
    proportion: float
    regex: list = dataclasses.field(default_factory=list)


class Reader:
    def __init__(self, fp: PathLike):
        self._fp = pathlib.Path(fp)
        assert self._fp.is_file()
        self._raw_content = tika_parser.from_file(str(fp))['content']
        self._chapter_names = dict()
        self.content = self._parse()

    @property
    def date(self) -> datetime.datetime:
        s = re.match(r'[A-Za-z_]+ (.*)', str(self._fp.stem)).group(1)
        return datetime.datetime.strptime(s, '(%Y-%m-%d)')

    def _parse(self, *, to_parse: str = None):
        """ Parse the raw content to remove things like headers, footers, etc. """
        # fix the spacing because there are a LOT of extra line breaks that
        # don't make a lot of sense
        lines = [line.strip() for line in to_parse or self._raw_content.split('\n')]
        lines = [line for line in lines if line]
        text = '\n'.join(lines)

        # since I've changed the working title, we'll need to pull it out for each file
        title = lines[0]

        # remove all the footers (emdash page# emdash)
        text = re.sub(r'\u2014 \d+ \u2014', '', text)

        # I'll need to strip out the headers, but I'm going to use them to find
        # all the chapter titles first. That will make pulling out the actual
        # chapter declarations a lot easier.
        header = re.compile(title + r' Chapter (?P<num>\d+) \u2014 (?P<title>.*)')
        for match in re.finditer(header, text):
            n = int(match.group('num'))
            title = match.group('title')
            self._chapter_names[n] = title

        # ...and NOW we can remove all of the headers
        text = re.sub(header, '', text)

        # No, CMoS, you're not getting away with this!
        # \hdots gets interpreted here with spaces added between the dots
        text = text.replace('. . .', '...')

        # ...apostrophes get messed up as well,
        # being replaced with ’ (rather than ')
        text = text.replace('\u2019', "'")

        return text

    @property
    def chapters(self) -> typing.Iterator[_ChapterMatch]:
        """ Here, we'll separate the text into its own chapter blocks """
        # make a copy of the content that we can mess with
        text = self.content

        curr, curr_title = 0, 'none'

        for next_, next_title in self._chapter_names.items():
            # k, v are the chapter# and title we're looking for
            # decl is the chapter declaration string, though since we're using
            # it for regex searching, we need to make sure any special re characters
            # are properly handled
            decl = re.escape(f'{next_} {next_title}')

            match = re.search(decl, text)
            start, end = match.span()

            # split the text according to this match
            # all text before the match is part of the current chapter,
            # everything after the match is part of the next chapter
            curr_text = text[:start]
            text = text[end+1:]
            yield _ChapterMatch(curr, curr_title, curr_text)
            curr, curr_title = next_, next_title

        # And now we just need to return the last chapter
        yield _ChapterMatch(curr, curr_title, text)

    @staticmethod
    def word_counter(text: str) -> collections.Counter:
        """ count the number of words in a particular block of text
        Honorifics make this a little bit more complicated, since a simple
        regex split (such as \w+) will split apart names such as "Amara-san"
        into two different words (["Amara", "san"]), which we don't want.
        """

        pattern = re.compile(r'''
                             # match some letters or apostrophe:
                             # e.g., "Amara" or "Amara's"
                             ([\w+']+)

                             # match an optional honorific prefixed with hyphen
                             (-san|-kun|-chan|-sama|-senpai|-sensei)?

                             # match optional contractions following the honorific
                             # e.g. "Amara-senpai's"
                             (['\w]+)?
                             ''', re.VERBOSE)
        words = [''.join(w) for w in re.findall(pattern, text.lower())]
        return collections.Counter(words)

    @property
    def words_by_chapter(self) -> typing.Dict[int, collections.Counter]:
        """ return a dictionary {chapter#: Counter} of the number of words per chapter """
        return {
                chapter.number: self.word_counter(chapter.text)
                for chapter in self.chapters
        }

    @property
    def words(self) -> collections.Counter:
        """ return a Counter with all of the words in the text """
        filtered = {k: v for k, v in self.words_by_chapter.items() if k}
        return sum(filtered.values(), collections.Counter())

    @property
    def num_words(self) -> int:
        """ return the total number of content words in this text """
        return sum(v for k, v in self.words.items())

    @property
    def num_words_by_chapter(self) -> typing.Dict[int, int]:
        return {k: sum(v.values()) for k, v in self.words_by_chapter.items()}

    def frequency(self, word: str, regex=False) -> _FrequencyMatch:
        """ find the frequency of a given word """

        word = word.lower()  # coerce to lowercase since everything was stored that way
        corpus = self.words
        total = sum(corpus.values())

        if len(word.split()) > 1:
            warnings.warn(f'Trying to check multiword string {word!r}. This will not be found.')

        if regex:
            pattern = re.compile(word)
            matches = [_FrequencyMatch(k, v, v/total) for k, v in corpus.items() if pattern.fullmatch(k)]

            n = sum(f.total for f in matches)
            return _FrequencyMatch(word, n, n/total, [f.word for f in matches])

        n = corpus.get(word, 0)
        if not n:
            # Word not found. Let's see if any other words are close.
            x = {w: fuzz.ratio(w, word) for w in corpus.keys()}
            tgt, conf = max(x.items(), key=lambda item: item[1])
            warnings.warn(f'{word!r} not found. Did you mean {tgt!r} (confidence {conf}%)?')

        return _FrequencyMatch(word, n, n/total)


def update_counts(fp: PathLike = '../data.json', backups: PathLike = '../backups'):
    fp = pathlib.Path(fp).resolve()
    backups = pathlib.Path(backups).resolve()
    counts = utils.DatedDict.load(fp)

    for date, pdf in utils.get_valid_pdfs(backups):
        if date not in counts.keys():
            counts[date] = Reader(pdf).num_words
    counts.fill(mode='rollover')
    counts.sort()

    counts.write(fp)
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--datafile', type=pathlib.Path, default='../data.json')
    parser.add_argument('-b', '--backups', type=pathlib.Path, default='../backups')
    parser.add_argument('-x', '--frequency', nargs='+')
    parser.add_argument('-r', '--regex', action='store_true')
    args = parser.parse_args()

    update_counts(args.datafile, args.backups)

    date, fp = utils.most_recent(args.backups)
    r = Reader(fp)

    res = {word: r.frequency(word, args.regex) for word in args.frequency}
    if args.regex:
        res = {word: (f.total, f.proportion, f.regex) for word, f in res.items()}
        cols = 'count', 'proportion', 'matches'
    else:
        res = {word: (f.total, f.proportion) for word, f in res.items()}
        cols = 'count', 'proportion'

    print(utils.trans_dataframe(res, index='word', cols=cols))


if __name__ == '__main__':
    main()
