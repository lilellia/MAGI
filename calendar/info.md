# MAGI Calendar

Let the planetary orbital period (solar year) be 312.311 local days long, and let the moon's orbital period be 34.397 local days long. This creates a balance of 9.106... lunar cycles per solar year. If we let the calendar consist of nine months, this gives nine months of 34 days (306 total) with six (standard) or seven (leap year) intercalendary days.

We name these ten periods as follows:

1. Sirelle
2. Tiri
3. Enna
4. Fis
5. Klesni
6. Pelio
7. Kria
8. Sui
9. Brilia
10. Neyu

These names originate as names of gods from the ancient mythology. Neyu was an organizer whose role was to bring together the bickering gods, always watching out for humanity and keeping everything in check.

What we observe is that 312.311 = 312 + 4/13 + 1/302.32..., meaning that we want four leap years per cycle of thirteen years, which we can achieve with a pattern of `SSL SSL SSL SSL S`. After thirteen years, 4060.043 days have passed, and this calendar yields 312(9)+313(4)=4060 days, making this system only 0.043=1/23.2 days short, meaning that the calendar is short one full day after twenty-three cycles (299 years). In this case, the twenty-third cycle can simply include one extra day, meaking the pattern `SSL SSL SSL SSL L` for that cycle.

Because all those numbers (13, 34, 23) suck for clean systems, the date is generally written `(grand-cycle):(cycle):(year) (month-name) (day)` or as `(absolute-year).(day-in-year)`.

There are 34 days per month, 10 months per year, 13 years per cycle, 23 grand cycles per grand cycle. Hence, the first day of the first year would be `1:1:1 Sirelle 1`, and the 43rd day of the 677th year would be `3:7:1 Tiri 9`.

```python
>>> from cleressian_date import CleressianDate, Month
>>> print(CleressianDate.from_absolute_date(year=1, day=1))
1:1:1 Sirelle 1
>>> print(CleressianDate.from_absolute_date(year=677, day=43))
3:7:1 Tiri 9

>>> x = CleressianDate(3, 7, 1, Month.TIRI, 9)
>>> x.to_absolute_date()
AbsoluteDate(year=677, day=43)
>>> print(x.strftime('%X'))  # %X is absolute date (%04Y.%03j)
0677.043
```

## School Calendar

- Spring Term: Sirelle 01–Fis 17 (3.5 months)
- Summer Break: Fis 18–Klesni 17 (1 month)
- Autumn Term: Klesni 18–Sui 34 (3.5 months)
- Winter Break: Brilia 01–Brilia 34 (1 month)
- End-of-year celebrations: Neyu 01–06 (or 7)