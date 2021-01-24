import collections.abc
import dataclasses
import inspect
import logging
import re
from typing import Callable, Iterable, Union


def _reprify(cls):
    param_names = tuple(inspect.signature(cls).parameters)
    cls.__repr__ = lambda self: f'{cls.__name__}(' + ', '.join(f'{k}={getattr(self, k)!r}' for k in param_names) + ')'
    return cls


@dataclasses.dataclass
class AbsoluteDate:
    year: int = 1
    day: int = 1

    def __iter__(self):
        return iter((self.year, self.day))

    def validate(self) -> bool:
        try:
            CleressianDate.from_absolute_date(*self)
        except Exception:
            return False
        return True


@dataclasses.dataclass
class DateDelta:
    years: int = 0
    days: int = 0

    def __iter__(self):
        return iter((self.years, self.days))

    def __mul__(self, r):
        return self.__class__(self.years * r, self.days * r)


@_reprify
class CleressianDate:
    MONTHS = ['', 'Sirelle', 'Tiri', 'Enna', 'Fis', 'Klesni', 'Pelio', 'Kria', 'Sui', 'Brilia', 'Neyu']

    def __init__(
        self,
        grand_cycle: int = 1,
        cycle: int = 1,
        year: int = 1,
        month: Union[int, str] = 1,
        day: int = 1
    ):
        self.grand_cycle = grand_cycle
        self.cycle = cycle
        self.year = year
        self.month = month
        self.day = day

    #############################################################################################
    # ACCESSORS #################################################################################
    #############################################################################################

    @property
    def grand_cycle(self):
        return self._grand_cycle

    @grand_cycle.setter
    def grand_cycle(self, val):
        try:
            val = int(float(val))
        except ValueError:
            raise TypeError(f'grand_cycle must be interpretable as an integer, not {val!r}')

        self._grand_cycle = val

    @property
    def cycle(self):
        return self._cycle

    @cycle.setter
    def cycle(self, val):
        try:
            val = int(float(val))
        except ValueError:
            raise TypeError(f'cycle must be interpretable as an integer, not {val!r}')

        if not (1 <= val <= 23):
            raise ValueError(f'cycle must be between 1 and 23, not {val!r}')

        self._cycle = val

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, val):
        try:
            val = int(float(val))
        except ValueError:
            raise TypeError(f'year must be interpretable as an integer, not {val!r}')

        if not (1 <= val <= 13):
            raise ValueError(f'year must be between 1 and 13, not {val!r}')

        self._year = val

    @property
    def month(self):
        """ Return the month NUMBER """
        return self._month

    @month.setter
    def month(self, val):
        val = self._parse_month(val)
        self._month = val

    @property
    def day(self):
        return self._day

    @day.setter
    def day(self, val):
        try:
            val = int(float(val))
        except ValueError:
            raise TypeError(f'year must be interpretable as an integer, not {val!r}')

        daycap = self.days_in_month(self.cycle, self.year, self.month)
        if not (1 <= val <= daycap):
            raise ValueError(f'year must be between 1 and {daycap}, not {val!r}')

        self._day = val

    @property
    def month_name(self) -> str:
        return self.MONTHS[self.month]

    #############################################################################################
    # UTILITY METHODS ###########################################################################
    #############################################################################################

    @staticmethod
    def _parse_month(val: Union[int, str]) -> int:
        """ Parse the given value into the corresponding month number. """
        try:
            return int(float(val))
        except ValueError:
            if not isinstance(val, str):
                raise TypeError(f'month must be a string interpretable as an integer, not {val!r}')
            try:
                return 1 + CleressianDate.MONTHS[1:].index(val)
            except ValueError:
                raise ValueError(f'month must be full name of month or integer between 1 and 10, not {val!r}')

    @staticmethod
    def is_leap_year(cycle: int, year: int) -> bool:
        """ Return true if _:cycle:year defines a leap year; false, otherwise """
        if year % 3 == 0:
            # _:_:3k is a leap year
            return True

        if cycle == 23 and year == 13:
            # _:23:13 is also a leap year
            return True

        return False

    @staticmethod
    def days_in_month(cycle: int, year: int, month: Union[int, str]) -> int:
        """ Return the number of days in the given month"""
        month = CleressianDate._parse_month(month)

        if month == 10:
            # only month 10 has weird numbers of days
            return 6 + int(CleressianDate.is_leap_year(cycle, year))

        # all other months have 34 days
        return 34

    @staticmethod
    def days_in_year(cycle: int, year: int) -> int:
        """ Return the number of years in the given year. """
        return 313 if CleressianDate.is_leap_year(cycle, year) else 312

    def replace(self, **repl) -> 'CleressianDate':
        """ Create a copy of this date with the given replacements """
        values = dict(
            grand_cycle=self.grand_cycle,
            cycle=self.cycle,
            year=self.year,
            month=self.month,
            day=self.day
        )

        values.update(repl)

        return self.__class__(**values)

    def copy(self) -> 'CleressianDate':
        """ Create a copy of this date. """
        return self.replace()

    def __copy__(self) -> 'CleressianDate':
        return self.copy()

    def __deepcopy__(self) -> 'CleressianDate':
        return self.copy()

    #############################################################################################
    # ABSOLUTE DATE HANDLING ####################################################################
    #############################################################################################

    @classmethod
    def from_absolute_date(cls, year: int = 1, day: int = 1) -> 'CleressianDate':
        """ An alternate constructor using the absolute year and day.

        The grand cycle G starts in the year 299(G-1)+1, so the years which fall into this grand
        cycle are 299(G-1) + 1 <= y < 299G + 1. We can manipulate this inequality to give
        G <= (y + 298)/299 < G + 1. Since G and G+1 are both integers, we have
        G = floor((y+298)/299).

        Similarly, the cycle (counted absolutely) C begins in the year 13(C-1)+1, which yields
        by identical reasoning that C = floor((y+12)/13). Since we loop the cycle count in such
        a way that C=24 is equivalent to C=1, we can simply find C (mod 23) and remember to
        change 0 → 23.
        """
        g = (year + 298) // 299
        c = ((year + 12) // 13) % 23
        y = year % 13
        m = 1 + day // 34
        d = day % 34

        # the "or _" calcs are used to emulate 1-indexing
        return cls(g, c or 23, y or 13, m or 10, d or 34)

    def to_absolute_date(self) -> AbsoluteDate:
        """ Convert a CleressianDate to a tuple describing the absolute year and day in year

        For all CleressianDate objects `a` and integers `year` and valid `day`, we have both:
            CleressianDate.from_absolute_date(*a.to_absolute_date()) == a
            CleressianDate.from_absolute_date(year, day).to_absolute_date() == (year, day)
        """
        return AbsoluteDate(
            year=23 * 13 * (self.grand_cycle - 1) + 13 * (self.cycle - 1) + self.year,
            day=34 * (self.month - 1) + self.day
        )

    #############################################################################################
    # FORMATTING METHODS ########################################################################
    #############################################################################################

    def strftime(self, template: str = "%x") -> str:
        """ Convert the date object to a string following the given template, which may contain %_ tags,
        which are interpreted as:

        %g      number of grand cycle (1, 2, 3, ...)
        %c      number of cycle in grand cycle (1, 2, 3, ..., 23)
        %y      number of year in cycle (1, 2, 3, ..., 13)
        %b      abbreviated name of month (Sir, Tir, Enn, ..., Ney)
        %B      full name of month (Sirelle, Tiri, Enna, ..., Neyu)
        %m      number of month (1, 2, 3, ..., 10)
        %d      number of day within month (1, 2, 3, ..., 34)
        %j      number of day within year (1, 2, 3, ..., 313)
        %Y      number of absolute year (1:1:1 == year 1)

        %x      standard form date representation (%g:%c:%y %B %d)
        %X      absolute form date representation (%04Y.%03j)

        The numeric tags also support numeric padding, such as %04Y meaning %Y but zero-padded
        to a width of four characters.
        """
        if not isinstance(template, str):
            raise TypeError(f'template must be a string, not {template!r}')

        # replace the two shortcut tags
        template = template.replace("%x", "%g:%c:%y %B %d").replace("%X", "%04Y.%03j")

        # handle numeric lookups
        numeric = dict(
            g=self.grand_cycle, c=self.cycle, y=self.year,
            m=self.month, d=self.day,
            j=self.to_absolute_date().day,
            Y=self.to_absolute_date().year
        )

        for k, v in numeric.items():
            match = re.search(r'%(0(\d+))?' + k, template)
            if match is not None:
                length = int(match.group(2) or '1')  # always force a width >= 1
                template = template.replace(match.group(0), str(v).zfill(length))

        # handle nonnumeric lookups
        nonnumeric = {'%b': self.month_name[:3], '%B': self.month_name, '%%': '%'}
        for k, v in nonnumeric.items():
            template = template.replace(k, v)

        return template

    def __str__(self) -> str:
        return self.strftime(template="%x")

    @classmethod
    def strptime(cls, date_str: str, template: str = "%x") -> 'CleressianDate':
        if not isinstance(date_str, str):
            raise TypeError(f'date_str must be a string, not {date_str!r}')
        if not isinstance(template, str):
            raise TypeError(f'template must be a string, not {template!r}')

        # handle the two shortcut tags
        pattern: str = template.replace("%x", "%g:%c:%y %B %d").replace("%X", "%04Y.%03j")

        # go through the template and replace %_ with the proper regex structures
        def _repl(key: str) -> Callable[[re.Match], str]:
            if key in set('gcymdjY'):
                # numeric key
                return lambda match, key=key: f'(?P<{key}>' + r'\d{' + (match.group(1) or '1') + r',})'
            elif key == 'b':
                # short month names
                names = '|'.join(month[:3] for month in cls.MONTHS[1:])
                return lambda _: f'(?P<b>{names})'
            elif key == 'B':
                # long month names
                names = '|'.join(cls.MONTHS[1:])
                return lambda _: f'(?P<B>{names})'
            elif key == '%':
                # literal percent sign
                return lambda _: '%'
            else:
                raise ValueError(f'invalid key {key!r}')

        # numeric tags
        for key in set('gcymdjY'):
            pattern = re.sub(r'%(0\d+)?' + key, _repl(key), pattern)

        # nonnumeric tags
        for key in set('bB%'):
            pattern = re.sub(f'%{key}', _repl(key), pattern)

        # ---------------------------------------------------------------------------------------------
        # At this point, `pattern` contains the *actual* regex we can use to parse the date string.
        # ---------------------------------------------------------------------------------------------

        match = re.fullmatch(pattern, date_str)
        if match is None:
            raise ValueError(f'Date data {date_str!r} does not match format {template!r}')

        kwargs = {}

        # first check for absolute dates
        sentinel = cls.from_absolute_date(1, 1)

        if 'Y' in match.groupdict().keys():
            absyear = int(match.group('Y'))
            sentinel = cls.from_absolute_date(absyear, 1)

            kwargs['grand_cycle'] = sentinel.grand_cycle
            kwargs['cycle'] = sentinel.cycle
            kwargs['year'] = sentinel.year

        if 'j' in match.groupdict().keys():
            absday = int(match.group('j'))
            tmp = cls.from_absolute_date(1, absday)
            sentinel = sentinel.replace(month=tmp.month, day=tmp.day)

            kwargs['month'] = sentinel.month
            kwargs['day'] = sentinel.day

        # now check for individual values
        def _update(key: str, name: str):
            nonlocal sentinel
            if key not in match.groupdict().keys():
                return

            raw_value = match.group(key)
            if key == 'b':
                # find the index of the month with that abbreviation
                val = [s[:3] for s in cls.MONTHS].index(raw_value)
            elif key == 'B':
                # just leave the month name intact
                val = raw_value
            else:
                # interpret the value as numeric
                val = int(raw_value)

            if name in kwargs.keys():
                # we've already defined this value
                tmp = sentinel.replace(**{name: val})

                if tmp != sentinel:
                    fmt = "%04Y (%g:%c:%y)" if key in 'gcy' else ".%03j (%B %02d)"
                    prev = sentinel.strftime(fmt)
                    curr = tmp.strftime(fmt)
                    logging.warning(f'strptime: {name} overwritten: {prev} -> {curr}')

            sentinel = sentinel.replace(**{name: val})
            kwargs[name] = val

        # perform the updates
        _update('g', 'grand_cycle')
        _update('c', 'cycle')
        _update('y', 'year')
        _update('m', 'month')
        _update('b', 'month')
        _update('B', 'month')
        _update('d', 'day')

        kwargs.setdefault('grand_cycle', 1)
        kwargs.setdefault('cycle', 1)
        kwargs.setdefault('year', 1)
        kwargs.setdefault('month', 1)
        kwargs.setdefault('day', 1)

        return cls(**kwargs)

    #############################################################################################
    # COMPARISON METHODS ########################################################################
    #############################################################################################

    def __eq__(self, other) -> int:
        if not isinstance(other, CleressianDate):
            return False
        return repr(self) == repr(other)

    def __lt__(self, other) -> int:
        """ Return True if both are CleressianDates and `self` occurs before `other` """
        if not isinstance(other, CleressianDate):
            a, b = self.__class__.__name__, other.__class__.__name__
            raise TypeError(f"'<' not supported between instances of {a!r} and {b!r}")
        return tuple(self.to_absolute_date()) < tuple(other.to_absolute_date())

    #############################################################################################
    # ARITHMETIC METHODS ########################################################################
    #############################################################################################

    def __add__(self, other: Union[int, Iterable[int]]) -> 'CleressianDate':
        """ Return the date a given number of years and days in the future.
        If `other` is a single integer, interpret it as a number of days.
        """
        try:
            years = 0
            days = int(float(other))
        except ValueError:
            if isinstance(other, collections.abc.Iterable):
                try:
                    years, days = [int(float(x)) for x in other]
                except ValueError:
                    clsname = self.__class__.__name__
                    raise TypeError(f'other must be one of (int, Iterable[int, int], {clsname}), not {other!r}')
            else:
                clsname = self.__class__.__name__
                raise TypeError(f'other must be one of (int, Iterable[int, int], {clsname}), not {other!r}')

        # alias from_absolute_date
        fabs = self.__class__.from_absolute_date

        # naively make the additions
        x = self.to_absolute_date()
        x.year += years
        x.day += days

        # adjust until a valid date
        while True:
            offset = -1 if x.day < 1 else 0
            tmp = fabs(x.year + offset)
            diy = self.days_in_year(tmp.cycle, tmp.year)

            if 1 <= x.day <= diy:
                break

            adj = 2 * offset + 1
            x.year += adj
            x.day -= adj * diy

        return fabs(x.year, x.day)

    def __sub__(self, other: Union[int, Iterable[int], 'CleressianDate']) -> Union[DateDelta, 'CleressianDate']:
        """ Find the (1) number of years/days between two dates (2) date a given number of years/days in the past

        If `other` is another CleressianDate, do option (1).
        Otherwise, `other` should be an integer or a 2-iterable of ints. A bare int is interpreted as # of days.
        """
        if isinstance(other, CleressianDate):
            # find the number of years and days between the two dates
            cls = self.__class__
            distance = cls.distance(self, other)
            return distance if self > other else distance * -1

        # otherwise, calculate a date some number of years and days in the past
        try:
            years = 0
            days = int(float(other))
        except ValueError:
            if isinstance(other, collections.abc.Iterable):
                try:
                    years, days = [int(float(x)) for x in other]
                except ValueError:
                    clsname = self.__class__.__name__
                    raise TypeError(f'other must be one of (int, Iterable[int, int], {clsname}), not {other!r}')
            else:
                clsname = self.__class__.__name__
                raise TypeError(f'other must be one of (int, Iterable[int, int], {clsname}), not {other!r}')

        return self + (-years, -days)

    @staticmethod
    def distance(x: 'CleressianDate', y: 'CleressianDate') -> DateDelta:
        """ Return the number of years and days between two dates, regardless of order. """
        if not isinstance(x, CleressianDate) or not isinstance(y, CleressianDate):
            raise TypeError('arguments must be CleressianDate onjects')

        if x == y:
            return DateDelta(0, 0)

        # otherwise, swap as necessary to make x < y
        if x > y:
            x, y = y, x

        ax, ay = x.to_absolute_date(), y.to_absolute_date()
        result = DateDelta()

        # get the day to line up
        if ax.day < ay.day:
            result.days = ay.day - ax.day
            ax.day = ay.day
        else:
            tmp = CleressianDate.from_absolute_date(ax.year)
            diy = CleressianDate.days_in_year(tmp.cycle, tmp.year)

            result.days = ay.day + (diy - ax.day)
            ax.day = ay.day
            ax.year += 1

        # now, just subtract the years
        result.years = ay.year - ax.year

        return result
