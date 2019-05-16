import argparse
import calendar
import dataclasses
import datetime
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import pathlib
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import sys
import typing

import reader
import utils
from utils import PathLike

register_matplotlib_converters()
plt.switch_backend('QT5Agg')


def render(n):
    """ figure out the best way to arrange `n` things into a rectangle """
    rows = round(np.sqrt(n))
    cols = np.ceil(n / rows)
    return int(rows), int(cols)


@dataclasses.dataclass
class Subplot:
    rows: int
    columns: int
    index: int

    def __iter__(self):
        t = self.rows, self.columns, self.index
        return iter(t)


class Plotter:
    def __init__(self, counts_fp: PathLike, backups: PathLike):
        self.counts = reader.update_counts(counts_fp, backups)
        self.range = min(self.counts.keys()), max(self.counts.keys())

    @property
    def rates(self) -> utils.DatedDict:
        r = {d2: v2-v1 for (d1, v1), (d2, v2) in utils.pairwise(self.counts.items())}
        return utils.DatedDict(r)

    @property
    def most_recent(self) -> typing.Tuple[datetime.datetime, reader.Reader]:
        try:
            date, fp = sorted(utils.get_valid_pdfs())[-1]
            return date, reader.Reader(fp)
        except IndexError as e:
            raise FileNotFoundError('no .pdfs found') from e

    def plot_totals(self, subplot: Subplot, **kwargs):
        plt.subplot(*subplot)
        df = pd.DataFrame(self.counts.items(), columns=['date', 'words'])

        after = kwargs.get('after')
        if after:
            df = df[df['date'] >= after]

        sns.lineplot(
            x='date', y='words', data=df,
            markers='X', color='purple'
        )

        n = sorted(self.counts.items())[-1][1]
        self.prettify(title=f'Cumulative # words written (current = {n})')

    def plot_rates(self, subplot: Subplot, **kwargs):
        plt.subplot(*subplot)
        bound = kwargs.get('after', None)
        mask_zero = kwargs.get('mask_zero', False)

        d = {k: v for k, v in self.rates.items() if not bound or k >= bound}

        start, end = min(d.keys()), max(d.keys())
        start_copy, end_copy = start, end   # copied for building the mask

        start -= datetime.timedelta(days=start.weekday())  # get to start of week
        end += datetime.timedelta(days=6-end.weekday())    # get to start of week

        # create an N x 7 grid, where each row represents one week
        num_weeks = int(np.ceil((end - start).days / 7))
        arr = np.zeros((num_weeks, 7))
        mask = np.empty((num_weeks, 7))

        # turn the rate data into that grid
        date = start
        while date <= end:
            rate = d.get(date, 0)
            i = (date - start).days // 7    # row = num of weeks since beginning
            j = date.weekday()              # col = day of week

            arr[i, j] = rate

            # mask is True when:
            #   * date is out of bounds
            #   * rate is zero and we want to mask zeros
            mask[i, j] = not (start_copy <= date <= end_copy) or (mask_zero and rate == 0)

            date += datetime.timedelta(days=1)

        # get useful tick labels
        xticklabels = [f'{i:+} ({abbr})' for i, abbr in enumerate(calendar.day_abbr)]
        yticklabels = [
            str(s)[:10]
            for s in np.arange(start, end, step=datetime.timedelta(days=7))
        ]

        sns.heatmap(
            data=arr,
            annot=True, fmt='.0f',      # write the cell value
            linecolor='white',          # border color
            linewidths=0.1,             # width of the cell borders,
            cmap='PuBuGn',              # color map (white to purple to blue to green)
            xticklabels=xticklabels,
            yticklabels=yticklabels,
            mask=mask
        )

        self.prettify(
            title='# words written per day',
            xlabel='weekday', ylabel='week starting with'
        )

    def plot_chapters(self, subplot: Subplot, **kwargs):
        plt.subplot(*subplot)

        date, r = self.most_recent
        df = pd.DataFrame(r.num_words_by_chapter.items(), columns=['chapter', 'words'])
        df = df[df['chapter'] != 0]
        df['name'] = [r._chapter_names.get(c) for c in df['chapter']]

        x = df['chapter']
        y = df['words']

        x = [str(t) for t in df.chapter]
        plt.bar(x, df.words, color='pink')

        ymin, ymax = plt.ylim()
        yrange = ymax - ymin

        for c, y, name in zip(x, df.words, df.name):
            plt.text(
                x=c, y=y+0.01*yrange, s=f'{y:,.0f}',
                color='black', va='bottom', ha='center',
                fontdict=dict(fontsize=9)
            )
            plt.text(
                x=c, y=0.02*yrange, s=name,
                color='black', va='bottom', ha='center',
                fontdict=dict(fontsize=9), rotation=90
            )

        self.prettify(title='# words per chapter', xlabel='chapter')

    def plot_word_freq(self, subplot: Subplot, **kwargs):
        plt.subplot(*subplot)

        date, r = self.most_recent
        k, v = zip(*r.words.items())
        df = pd.DataFrame({'words': k, 'freq': v}).sort_values(by=['freq'], ascending=False)
        n = sum(df.freq)
        df['%'] = df['freq'] / n

        sns.scatterplot(x='words', y='%', data=df)

        k = len(df)
        hapax = sum(1 for f in df.freq if f == 1)
        self.prettify(
            title=f'Word Frequency\n(unique={k}, hapax legomena={hapax}={hapax/k:.1%})',
            xlabel='word',
            ylabel='% occurrence'
        )

        plt.xticks([], [])

        for word, perc, i in zip(df.words, df['%'], range(5)):
            plt.text(
                x=word, y=perc, s=f'{word}: {perc:.1%}',
                color='black', va='bottom', ha='left',
                fontdict=dict(fontsize=9)
            )

    @staticmethod
    def prettify(title, xlabel='Date', ylabel='# Words'):
        plt.setp(plt.gca().get_xticklabels(), fontsize=9, rotation=90, ha='center')
        plt.setp(plt.gca().get_yticklabels(), fontsize=9)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.subplots_adjust(top=0.95, bottom=0.125, hspace=0.5)

    def plot(self, modes, **kwargs):
        funcs = {
            'total': self.plot_totals,
            'rate': self.plot_rates,
            'chapter': self.plot_chapters,
            'wordfreq': self.plot_word_freq
        }

        assert all(mode in funcs.keys() for mode in modes), 'Invalid plot type'
        rows, cols = render(len(modes))

        for i, arg in enumerate(modes, start=1):
            s = Subplot(rows, cols, i)
            funcs[arg](subplot=s, **kwargs)

        plt.get_current_fig_manager().window.showMaximized()
        plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--datafile', dest='datafile', type=pathlib.Path, help='filepath to JSON file with cumulative counts [default: ../data.json]', default=pathlib.Path('../data.json'))
    parser.add_argument('-b', '--backups', type=pathlib.Path, help='directory where text backups can be found (for the purposes of updating the datafile) [default: ../backups/]', default=pathlib.Path('../backups'))
    parser.add_argument('-t', '--total', dest='modes', action='append_const', const='total', help='flag: when activated, plot cumulative totals')
    parser.add_argument('-r', '--rate', dest='modes', action='append_const', const='rate', help='flag: when activated, plot daily rate heatmap')
    parser.add_argument('--mask-zero', dest='mask_zero', action='store_true', help='in the rate plot, mask cells with a value of zero [default: False: show zeros]')
    parser.add_argument('-c', '--chapter', dest='modes', action='append_const', const='chapter', help='flag: when activated, plot daily rate heatmap')
    parser.add_argument('-a', '--after', dest='after', default=None, type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), help='force a beginning to the rate graph, even if the data extend before this date [default: show all data] (only affects graphs of totals (-t/--total) and rates (-r/--rates))')
    parser.add_argument('-wf', '--wordfreq', dest='modes', action='append_const', const='wordfreq', help='flag: when activated, plot word frequency')

    parser.add_argument('-y', dest='validate', action='store_const', const='y', default=None, help='flag: when activated, skip validation of datafile & backups [default: False, i.e. perform validation]')

    args = parser.parse_args()

    while args.validate not in {'y', 'n'}:
        print('Using:', args.datafile.resolve(), args.backups.resolve(), sep='\n')
        args.validate = input('Is this okay? [Y/N] ').lower()

        if args.validate == 'n':
            sys.exit()

    kwargs = {'after': args.after, 'mask_zero': args.mask_zero}
    Plotter(args.datafile, args.backups).plot(args.modes or [], **kwargs)


if __name__ == '__main__':
    main()
