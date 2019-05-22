import datetime
import itertools
import json
import pandas as  pd
import pathlib
import re
import typing
import warnings

PathLike = typing.Union[pathlib.Path, str]


class DatedDict:
    def __init__(self, data: dict = None):
        self._data = data or dict()

    @classmethod
    def load(cls, fp: PathLike, date_fmt: str = '%Y-%m-%d') -> 'DatedDict':
        """ Take a .json file that contains a single dictionary with date keys, converting the keys to datetime.date objects """
        with open(fp, 'r') as f:
            raw = json.loads(f.read())

        data = {datetime.datetime.strptime(k, date_fmt): v for k, v in raw.items()}
        return cls(data)

    def write(self, fp: PathLike, date_fmt: str = '%Y-%m-%d'):
        """ Take a dictionary with keys of type datetime.datetime and output it to file, converting the keys to strings of the given format """
        data = {k.strftime(date_fmt): v for k, v in self._data.items()}
        with open(fp, 'w+') as f:
            f.write(json.dumps(data, indent=4))

    def fill(self, value: typing.Any = None, *, mode: str = 'fill'):
        """ Fill gaps in the dictionary according to the mode.

        mode=='rollover' :: empty slots are set with the previous existing value
                            (in this case, `value` is ignored)
        mode=='fill'     :: empty slots are filled with `value`

        >>> data = {
            datetime.datetime(2019-01-01): 5,
            datetime.datetime(2019-01-03): 10,
            datetime.datetime(2019-01-04): 20
        }
        >>> d = DatedDict(data)
        >>> e = DatedDict(data)

        >>> d.fill(mode='rollover')
        >>> print(d)
        {
            datetime.datetime(2019-01-01): 5,
            datetime.datetime(2019-01-02): 5,
            datetime.datetime(2019-01-03): 10,
            datetime.datetime(2019-01-04): 20
        }

        >>> e.fill()
        >>> print(e)
        {
            datetime.datetime(2019-01-01): 5,
            datetime.datetime(2019-01-02): None,
            datetime.datetime(2019-01-03): 10,
            datetime.datetime(2019-01-04): 20
        }
        """
        if mode not in {'fill', 'rollover'}:
            raise ValueError(f'Invalid fill mode {mode!r}')

        if not self._data:
            # there's nothing to do
            message = 'Trying to fill an empty DatedDict.'
            warnings.warn(message)
            return

        # find the bounds on the data
        date = start = min(self._data.keys())
        end = max(self._data.keys())

        while date < end:
            if date in self._data.keys():
                # update the rollover value
                rv = self._data[date]
            else:
                # fill this empty spot
                self._data[date] = value if mode == 'fill' else rv

            date += datetime.timedelta(days=1)

    def __str__(self):
        data = {k.strftime('%Y-%m-%d'): v for k, v in self._data.items()}
        return json.dumps(data, indent=4)

    def __repr__(self):
        return f'DatedDict({self._data})'

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        self._data[key] = value

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def sort(self):
        data = self._data.copy()
        self._data = {k: data[k] for k in sorted(self.keys())}


def get_valid_pdfs(directory: PathLike = '../backups'):
    for fp in pathlib.Path(directory).resolve().rglob('*.pdf'):
        fp = fp.resolve()
        date_str = re.search(r'\d\d\d\d-\d\d-\d\d', fp.stem).group()
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        yield date, fp


def most_recent(directory: PathLike = '../backups'):
    g = get_valid_pdfs(directory)
    return sorted(g)[-1]


def pattern_remove(text: str, patterns: typing.Iterable) -> str:
    """ Remove all instances of each pattern (which can either be a string
    or an re.compile object) """
    for p in patterns:
        text = re.sub(p, '', text)
    return text


def pairwise(iterable):
    """ s -> (s0, s1), (s1, s2), (s2, s3), ..."""
    u, v = itertools.tee(iterable, 2)
    next(v, None)
    return zip(u, v)


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return f'{filename}:{lineno} {category.__name__}:{message}\n'


class CTuple(tuple):
    def get(self, key, default=None):
        try:
            return self[key]
        except IndexError:
            return default


def trans_dataframe(dct: dict, index: str, cols: tuple) -> pd.DataFrame:
    k = list(dct.keys())
    v = [CTuple(val) for val in dct.values()]
    data = {c: [tup.get(j) for tup in v] for j, c in enumerate(cols)}
    return pd.DataFrame({index: list(k), **data}).set_index(index)
