/**
 * @typedef {Object} AbsoluteDate
 * @property {int} year the absolute year
 * @property {int} day the day within the year (int between 1 and 313)
 */

/** zfill
 * left-pad a value with zeros to at least the given length
 * @param {*} value the value to pad
 * @param {int} padLength the minimum length of the resulting string
 * @returns {string} the zero-padded string
 * 
 * Example:
 * zfill(3, 5) --> "00003"
 */
zfill = function (value, padLength) {
    s = value.toString();
    while (s.length < padLength) {
        s = "0" + s;
    }
    return s;
};


class CleressianDate {
    // "private" attributes
    _grandCycle;
    _cycle;
    _year;
    _month;
    _day;

    static MONTHS = [
        "", "Sirelle", "Tiri", "Enna", "Fis", "Klesni", "Pelio", "Kria", "Sui", "Brilia", "Neyu"
    ]

    // getters simply echo the private variables
    get grandCycle() {
        return this._grandCycle;
    }
    get cycle() {
        return this._cycle;
    }
    get year() {
        return this._year;
    }
    get month() {
        return this._month;
    }
    get day() {
        return this._day;
    }
    get monthName() {
        return CleressianDate.MONTHS[this.month];
    };

    /** grandCycle setter
     * @param {int} g the new value of grand cycle -> must be an integer
     */
    set grandCycle(g) {
        if (!Number.isInteger(g)) {
            throw new TypeError("grandCycle must be an integer, not " + g);
        }
        this._grandCycle = parseInt(g, 10);
    }

    /** cycle setter
     * @param {int} c the new value of cycle -> must be an integer on [1, 23]
     */
    set cycle(c) {
        if (!Number.isInteger(c)) {
            throw new TypeError("cycle must be an integer, not " + c);
        }
        if (c < 1 || c > 23) {
            throw new RangeError("cycle value must be between 1 and 23, not " + c);
        }
        this._cycle = parseInt(c, 10);
    }

    /** year setter
     * @param {int} y the new value of year -> must be an integer on [1, 13]
     */
    set year(y) {
        if (!Number.isInteger(y)) {
            throw new TypeError("year must be an integer, not " + y);
        }
        if (y < 1 || y > 13) {
            throw new RangeError("year value must be between 1 and 13, not " + y);
        }
        this._year = parseInt(y, 10);
    }

    /** month setter
     * @param {int|string} m the new value of month (int -> month index, string -> month name)
     */
    set month(m) {
        if (typeof (m) === 'string') {
            // month value is string, which we assume is the (full) month name
            // indexOf() returns -1 for not found; we also exclude 0, which holds the empty string
            let idx = CleressianDate.MONTHS.indexOf(m);
            if (idx <= 0) {
                throw new RangeError("invalid month name " + m);
            }
            this._month = idx;
        } else {
            if (!Number.isInteger(m)) {
                throw new TypeError("month must be a string or integer, not " + m);
            }
            this._month = parseInt(m, 10);
        }
    }

    /** day setter
     * @param {int} d the new value of day -> must be an integer on [1, CleressianDate.daysInMonth(...)]
     */
    set day(d) {
        if (!Number.isInteger(d)) {
            throw new TypeError("day must be an integer, not " + d);
        }

        let maxDays = CleressianDate.daysInMonth(this.cycle, this.year, this.month);
        if (d < 1 || d > maxDays) {
            throw new RangeError("cycle value must be between 1 and " + maxDays + ", not " + d);
        }

        this._day = parseInt(d, 10);
    }

    /** constructor
     * 
     * @param {int=} grandCycle the current grand cycle (period of 23 cycles)
     * @param {int=} cycle the current cycle (period of 13 years)
     * @param {int=} year the current year within the cycle
     * @param {int|string=} month the month within the year (as int or as string name)
     * @param {int=} day the day within the month
     * 
     * Empty values are filled as 1.
     * 
     * @throws {RangeError} if the date is invalid
     */
    constructor(grandCycle = 1, cycle = 1, year = 1, month = "Sirelle", day = 1) {
        this.grandCycle = grandCycle;
        this.cycle = cycle;
        this.year = year;
        this.month = month;
        this.day = day;
    }

    /** isLeapYear()
     * Returns true if _:cycle:year defines a leap year and false otherwise.
     * grandCycle is not passed since the leap year pattern resets every grand cycle anyway
     * 
     * @param {int} cycle the cycle within the grand cycle
     * @param {int} year the year in the cycle
     * 
     * @returns {bool} true if a leap year, false otherwise.
     */
    static isLeapYear(cycle, year) {
        if (year % 3 == 0) {
            /* G:C:3|6|9|12 is always a leap year */
            return true;
        }
        if (cycle == 23 && year == 13) {
            /* G:23:13 is also a leap year */
            return true;
        }

        return false;

    }

    /** daysInMonth()
     * Return the number of days in the given month.
     * 
     * @param {int} cycle the cycle within the grand cycle
     * @param {int} year the year in the cycle
     * @param {int} month the month of the year as integer
     * 
     * @returns {int} the number of days in the given month
     */
    static daysInMonth(cycle, year, month) {


        if (month == 10) {
            // only month 10 is affected by leap years
            return 6 + CleressianDate.isLeapYear(cycle, year);
        }

        // all other months have 34 days
        return 34;
    }

    /** daysInYear()
     * Return the number of days in the given year.
     * @param {int} cycle the cycle in the grand cycle
     * @param {int} year the year in the cycle
     * @returns {int} the number of days in the year (either 312 or 313)
     */
    static daysInYear(cycle, year) {
        return CleressianDate.isLeapYear(cycle, year) ? 313 : 312;
    }

    /** fromAbsoluteDate()
     * An alternate constructor using the absolute year and day.
     *
     * @param {int} year the absolute year 
     * @param {int} day the day within the year (defaults to 1)
     * 
     * @returns {CleressianDate}
     * 
     * 
     * The grand cycle, G, starts in the year 299(G-1)+1, so the years, y, which fall in the grand cycle are precisely
     * 299(G-1) + 1 <= y < 299G + 1. We can manipulate this inequality to give G <= (y + 298)/299 < G + 1, and since
     * G and G+1 are both integers, we have G = floor[ (y+298)/299 ].
     * 
     * Similarly, the cycle (counted absolutely) C begins in 13(C-1)+1, which yields C = floor[ (y+12)/13 ]. However,
     * we loop the cycle count so that C=24 is equivalent to C=1. Thus, a simple modular operation can be performed
     * (as long as we remember to move C=23k to C=23 instead of C=0).
     * 
     */
    static fromAbsoluteDate(year, day = 1) {
        let grandCycle = Math.floor((year + 298) / 299);
        let cycle = Math.floor((year + 12) / 13) % 23;
        year = year % 13;
        let month = 1 + Math.floor(day / 34);
        day = day % 34;

        return new CleressianDate(grandCycle, cycle || 23, year || 13, month || 10, day || 34);
    }

    /** toAbsoluteDate()
     * Convert a CleressianDate to an object describing absolute year and absolute day
     * 
     * @returns {AbsoluteDate}
     * 
     */
    toAbsoluteDate() {
        let year = 23 * 13 * (this.grandCycle - 1) + 13 * (this.cycle - 1) + this.year;
        let day = 34 * (this.month - 1) + this.day;

        return {
            "year": year,
            "day": day
        };
    }

    /** strftime()
     * portmanteau of "string format time": convert the date object to a string according to
     * the format specification below
     * 
     * @param {string} format the format string, which may include any of the following symbols,
     * which are interpreted accordingly
     * 
     * %g       number of grand cycle (1, 2, 3, ...)
     * %c       number of cycle in grand cycle (1, 2, 3, ..., 23)
     * %y       number of year in cycle (1, 2, 3, ..., 13)
     * %b       abbreviated name of month (Sir, Tir, Enn, ..., Ney)
     * %B       full name of month (Sirelle, Tiri, Enna, ..., Neyu)
     * %m       number of month (1, 2, 3, ..., 10)
     * %d       number of day within month (1, 2, 3, ..., 34)
     * %j       number of day within year (1, 2, 3, ..., 313)
     * %Y       number of absolute year (1:1:1 == year 1)
     * 
     * %x       standard form date representation (%g:%c:%y %B %d)
     * %X       absolute form date representation (%04Y.%03j)
     */
    strftime(format) {
        // handle the two shortcuts
        let shortcutLookup = {
            "%x": "%g:%c:%y %B %d",
            "%X": "%04Y.%03j"
        };
        for (let key in shortcutLookup) {
            format = format.replace(key, shortcutLookup[key]);
        }


        // handle all of the numeric lookups
        let numCodeLookup = {
            "g": this.grandCycle,
            "c": this.cycle,
            "y": this.year,
            "m": this.month,
            "d": this.day,
            "j": this.toAbsoluteDate().day,
            "Y": this.toAbsoluteDate().year
        }
        for (let key in numCodeLookup) {
            let value = numCodeLookup[key];
            let match = format.match(new RegExp('%(0(\\d+))?' + key));

            if (match) {
                let padLength = (match[2] === undefined) ? 1 : parseInt(match[2]);
                format = format.replace(match[0], zfill(value, padLength));
            }
        }

        // handle the nonnumeric lookups
        let alphaCodeLookup = {
            "%b": this.monthName.substring(0, 3),
            "%B": this.monthName,
            "%%": "%"
        };
        for (let key in alphaCodeLookup) {
            format = format.replace(key, alphaCodeLookup[key]);
        }

        return format;
    }

    /** toString
     * override toString to allow formatting (according to strftime specs)
     * @param {string} format the format string to use (defaults to "%x")
     */
    toString(format = "%x") {
        return this.strftime(format);
    }


    /** plus()
     * Add a number of years and days to the given date.
     * @param {int} years the number of years to add
     * @param {int} days the number of days to add
     * 
     * @returns {CleressianDate} the new date
     */
    plus(years = 0, days = 0) {
        let x = this.toAbsoluteDate();
        x.year += years;
        x.day += days;

        while (true) {
            let tmp = CleressianDate.fromAbsoluteDate(x.year, 1);
            let daysInYear = CleressianDate.daysInYear(tmp.cycle, tmp.year);

            if (x.day <= daysInYear) {
                break;
            }

            x.day -= daysInYear;
            x.year++;
        }

        return CleressianDate.fromAbsoluteDate(x.year, x.day);
    }

    /** minus()
     * Add a number of years and days to the given date.
     * @param {int} years the number of years to add
     * @param {int} days the number of days to add
     * 
     * @returns {CleressianDate} the new date
     */
    minus(years = 0, days = 0) {
        let x = this.toAbsoluteDate();
        x.year -= years;
        x.day -= days;

        while (true) {
            let tmp = CleressianDate.fromAbsoluteDate(x.year - 1, 1);
            let daysInYear = CleressianDate.daysInYear(tmp.cycle, tmp.year);

            if (x.day > 0) {
                break;
            }

            x.day += daysInYear;
            x.year--;
        }

        return CleressianDate.fromAbsoluteDate(x.year, x.day);
    }

    /** compare
     * 
     * @param {CleressianDate} x the first date to compare
     * @param {CleressianDate} y the second date to compare
     * @throws {TypeError} if either x or y is not a CleressianDate
     * @returns {int} -1 if x < y, 0 if x == y, and 1 if x > y
     */
    static compare(x, y) {
        if (!(x instanceof CleressianDate) || !(y instanceof CleressianDate)) {
            throw new TypeError("CleressianDate.compare can only interpret CleressianDate objects");
        }

        let ax = x.toAbsoluteDate();
        let ay = y.toAbsoluteDate();

        if (ax.year < ay.year) {
            return -1;
        }
        if (ax.year > ay.year) {
            return 1;
        }

        // years are the same
        if (ax.day == ay.day) {
            return 0;
        }
        return (ax.day < ay.day) ? -1 : 1;
    }

    /** comparison methods
     * equals, ne, lt, le, gt, ge
     */
    equals(other) {
        return CleressianDate.compare(this, other) == 0;
    }
    eq(other) {
        return this.equals(other);
    }
    ne(other) {
        return !this.equals(other);
    }
    lt(other) {
        return CleressianDate.compare(this, other) == -1;
    }
    le(other) {
        return CleressianDate.compare(this, other) <= 0;
    }
    gt(other) {
        return CleressianDate.compare(this, other) == 1;
    }
    ge(other) {
        return CleressianDate.compare(this, other) >= 0;
    }

    /** distance()
     * Return the number of years and days between two dates.
     * In a sense, this is |x - y|.
     * @param {CleressianDate} x one date
     * @param {CleressianDate} y the other date
     * @returns {Object} the years and days between the two dates
     */
    static distance(x, y) {
        if (!(x instanceof CleressianDate) || !(y instanceof CleressianDate)) {
            throw new TypeError("CleressianDate.compare can only interpret CleressianDate objects");
        }

        let result = {
            years: 0,
            days: 0
        };

        // if the two dates are the same, return 0
        if (x == y) {
            return result;
        }

        // otherwise, swap as necessary to make x < y
        if (CleressianDate.compare(x, y) == 1) {
            let tmp = y;
            y = x;
            x = tmp;
        }

        // convert to absolute dates
        let ax = x.toAbsoluteDate()
        let ay = y.toAbsoluteDate()

        // First, get the day._ to line up.
        if (ax.day <= ay.day) {
            result.days = ay.day - ax.day;
            ax.day = ay.day;
        } else {
            let daysInYear = CleressianDate.daysInYear(ax.year);
            result.days = ay.day + (daysInYear - ax.day);
            ax.day = ay.day;
            ax.year++;
        }

        // now, just subtract the years
        result.years = ay.year - ax.year;

        return result;

    }
}