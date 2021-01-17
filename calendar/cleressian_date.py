# TODO: Implement .strptime, __add__, and __sub__ #

__all__ = ['Month', 'CleressianDate']

import collections
import enum
import math
import re


_AbsoluteDate = collections.namedtuple('AbsoluteDate', ('year', 'day'))


class Month(enum.Enum):
    SIRELLE = 1
    TIRI = 2
    ENNA = 3
    FIS = 4
    KLESNI = 5
    PELIO = 6
    KRIA = 7
    SUI = 8
    BRILIA = 9
    NEYU = 10


class CleressianDate:
    def __init__(self, grand_cycle: int, cycle: int, year: int, month: int = 1, day: int = 1):
        """ Create a new Clerèssian Date.

        Parameters:

            grand_cycle         int
            The current grand cycle (period of 23 cycles).

            cycle               int
            The current cycle (period of 13 years).
            We must have 1 <= cycle <= 23. Otherwise, ValueError is raised.

            year                int
            The current year within the cycle.
            We must have 1 <= year <= 13. Otherwise, ValueError is raised.

            month               int = 1
            The number of the month within the year.
            We must have 1 <= month <= 10. Otherwise, ValueError is raised.

            day                 int = 1
            The number of the day within the month.
            We must have 1 <= day <= 34 when month <= 9, 1 <= day <= 6 when month == 10
            and the year is not a leap year, and 1 <= day <= 7 when month == 10 and the
            year is a leap year.
        """
        if not (1 <= cycle <= 23):
            raise ValueError(f'cycle must be on ℤ[1, 23], not {cycle!r}')

        if not (1 <= year <= 13):
            raise ValueError(f'year must be on ℤ[1, 13], not {year!r}')

        if isinstance(month, Month):
            month = month.value

        if not (1 <= month <= 10):
            raise ValueError(f'month must be on ℤ[1, 10], not {month!r}')

        # We're allowed 34 days in every month except the intercalendary month 10,
        # where we're allowed 6 in a standard year and 7 in a leap year
        intercalendary_days = 6 + int(self.__class__.is_leap_year(grand_cycle, cycle, year))
        allowed_days = 34 if month != 10 else intercalendary_days
        if not (1 <= day <= allowed_days):
            raise ValueError(f'day must be on ℤ[1, {allowed_days}], not {day!r}')

        self.grand_cycle = grand_cycle
        self.cycle = cycle
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def is_leap_year(cls, grand_cycle: int, cycle: int, year: int) -> bool:
        """ Determine if the given year (GC:C:Y) represents a leap year.

        Parameters:
            grand_cycle         int
            The current grand cycle (period of 23 cycles)

            cycle               int
            The current cycle (period of 13 years)

            year                int
            The current year within the cycle.


        Returns:                bool
            True when GC:C:Y represents a leap year; False otherwise.

        Raises:
                                ValueError
                When any of the values cannot form a correct date.
                (See __init__)

        This behavior is determined by the combination of :cycle: and :year:.
        We have 22 cycles (#1-22) which follow the SSL SSL SSL SSL S pattern, then
        one cycle (#23) which follows the          SSL SSL SSL SSL L pattern.
        """
        if year % 3 == 0:
            # X:Y:3/6/9/12 are leap years
            return True
        elif cycle == 23 and year == 13:
            # X:23:13 is a leap year as well
            return True

        # Anything else is not a leap year
        return False

    @classmethod
    def from_absolute_date(cls, year: int, day: int = 1):
        """ Create a CleressianDate from a total number of years and days.

        Parameters:
            year                int
                The current year (1-indexed)

            day                 int
                The day within the year (1-indexed)

        Returns:                CleressianDate
            The CleressianDate corresponding to the given year and day.

        Raises:                 ValueError
                If the day is invalid (cannot be used to construct a date)
                (See __init__)
        """
        grand_cycle = 1 + year // (1 + 23 * 13)
        cycle = math.ceil(year / 13) % 23 or 23  # need to have [1, 23], not [0, 22]
        year = year % 13 or 13                   # need to have [1, 13], not [0, 12]

        month, day = divmod(day, 34)
        month += 1                               # need to have [1, 10], not [0, 9]

        return cls(grand_cycle, cycle, year, month, day)

    def to_absolute_date(self):
        year = 23 * 13 * (self.grand_cycle - 1) + 13 * (self.cycle - 1) + self.year
        day = 34 * (self.month - 1) + self.day

        return _AbsoluteDate(year, day)

    @property
    def month_name(self) -> str:
        return Month(self.month).name.title()

    def __format__(self, fmt: str) -> str:
        """

        Format codes:

        %g      number of grand cycle as an unpadded decimal number
                (1, 2, 3, ...)

        %c      number of cycle as an zero-padded decimal number**
                (1, 2, 3, ..., 23)

        %y      year of cycle as an zero-padded decimal number*
                (01, 02, 03, ..., 13)

        %b      month as locale's abbreviated name*
                (Sir, Tir, ..., Kle)

        %B      month as locale's full name*
                (Sirelle, Tiri, ..., Klesni)

        %m      month as zero-padded decimal number*
                (01, 02, ..., 10)

        %d      day of month as a zero padded decimal number*
                (01, 02, 03, ..., 34)

        %j      day of the year as a zero-padded decimal number*
                (001, 002, ..., 313)

        %Y      absolute year as a zero-padded decimal number, where GC01:C01:Y01 => 0001.**
                (0001, 0002, ..., 9998, 9999)

        %x      appropriate date representation*
                shorthand for: %g:%c:%y %B %d

        %X      absolute date representation**
                shorthand for: %04Y.%03j

        %%      a literal % character*
                (%)


        *consistent with 1989 C standard, which is also used by datetime's strftime
        **inconsistent with 1989 C standard, which uses:
            %c  Locale's appropriate date and time representation (e.g., "Tue Aug 16 21:30:00 1988")
            %Y  Year with century as decimal number (0001, 0002, ..., 2013, 2014, ..., 9998, 9999)
        """

        fmt = fmt.replace('%x', '%g:%c:%y %B %d').replace('%X', '%04Y.%03j')

        num_codes = {
            'g': self.grand_cycle,
            'c': self.cycle,
            'y': self.year,
            'm': self.month,
            'd': self.day,
            'j': self.to_absolute_date().day,
            'Y': self.to_absolute_date().year
        }

        for k, v in num_codes.items():
            pattern = r'%(0\d+)?' + str(k)
            match = re.search(pattern, fmt)
            if match:
                subfmt = f"{match.group(1) or ''}d"
                fmt = re.sub(pattern, format(v, subfmt), fmt)

        nonnum_codes = {
            # month as locale's abbreviated name
            '%b': self.month_name[:3],

            # month as locale's full name
            '%B': self.month_name,

            # literal % character
            '%%': '%'
        }

        for k, v in nonnum_codes.items():
            fmt = fmt.replace(k, v)

        return fmt

    def strftime(self, fmt: str = '%x') -> str:
        return format(self, fmt)

    @classmethod
    def strptime(cls, date_str: str, fmt: str):
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.__format__('%x')

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return f'{cls}(grand_cycle={self.grand_cycle!r}, cycle={self.cycle!r}, year={self.year!r})'

    def __add__(self, absdate: _AbsoluteDate):
        raise NotImplementedError()

    def __sub__(self, other) -> _AbsoluteDate:
        raise NotImplementedError()
