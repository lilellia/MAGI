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
    let s = value.toString();
    while (s.length < padLength) {
        s = "0" + s;
    }
    return s;
};

/**
 * 
 * @param {*} key 
 * @param {*} defaultValue 
 */
Object.prototype.get = function(key, defaultValue = undefined) {
    if ( (val = this[key] ) !== undefined) {
        return val;
    }

    return defaultValue;
}


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
        if (typeof(m) === 'string') {
            // month value is string, which we assume is the (full) month name
            // indexOf() returns -1 for not found; we also exclude 0, which holds the empty string
            const idx = CleressianDate.MONTHS.indexOf(m);
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

        const maxDays = CleressianDate.daysInMonth(this.cycle, this.year, this.month);
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
     * @param {int=} day the day within the year (defaults to 1)
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
        const grandCycle = Math.floor((year + 298) / 299);
        const cycle = Math.floor((year + 12) / 13) % 23;
        year = year % 13;
        const month = 1 + Math.floor(day / 34);
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
        return {
            "year": 23 * 13 * (this.grandCycle - 1) + 13 * (this.cycle - 1) + this.year,
            "day": 34 * (this.month - 1) + this.day
        };
    }

    /**
     * 
     * @param {Object} repl the replacements to make
     */
    replace(repl) {
        // use this object as defaults, but overwrite those with the given replacements
        const {
            grandCycle = this.grandCycle,
            cycle = this.cycle,
            year = this.year,
            month = this.month,
            day = this.day
        } = repl;

        return new CleressianDate(grandCycle, cycle, year, month, day);
    }

    copy() {
        return this.replace({});
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
        const shortcutLookup = {
            "%x": "%g:%c:%y %B %d",
            "%X": "%04Y.%03j"
        };
        for (let key in shortcutLookup) {
            format = format.replace(key, shortcutLookup[key]);
        }


        // handle all of the numeric lookups
        const numCodeLookup = {
            "g": this.grandCycle,
            "c": this.cycle,
            "y": this.year,
            "m": this.month,
            "d": this.day,
            "j": this.toAbsoluteDate().day,
            "Y": this.toAbsoluteDate().year
        }
        for (let key in numCodeLookup) {
            const value = numCodeLookup[key];
            const match = format.match(new RegExp('%(0(\\d+))?' + key));

            if (match) {
                const padLength = (match[2] === undefined) ? 1 : parseInt(match[2]);
                format = format.replace(match[0], zfill(value, padLength));
            }
        }

        // handle the nonnumeric lookups
        const alphaCodeLookup = {
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
     * @param {string=} format the format string to use (defaults to "%x")
     */
    toString(format = "%x") {
        return this.strftime(format);
    }

    /**
     * Create a CleressianDate from a string template. This uses the same %_ templates as strftime.
     * @param {str} dateStr 
     * @param {str="%x"} template 
     * @throws {RangeError} if the date string does not match the template
     * @return {CleressianDate} the interpreted CleressianDate
     */
    static strptime(dateStr, template = "%x") {
        const _template = template;

        // replace "%x" and "%X" with their long-form versions
        template = template.replace("%x", "%g:%c:%y %B %d").replace("%X", "%04Y.%03j");

        // now go through the template specifications and replace %_ with the proper regex structures
        const convert = function (key) {
            switch (key) {
                case "g":
                case "c":
                case "y":
                case "m":
                case "d":
                case "j":
                case "Y":
                    // all of the numeric keys
                    // we use parseInt because the regexp will read padLength as, e.g., "03", but we want the
                    // new regexp to simply be ...{3,}...
                    return function(match, padLength, offset, string) {
                        padLength = padLength || "1";
                        return "(?<" + key + ">\\d{" + parseInt(padLength, 10) + ",})";
                    };
                case "b":
                    // short month names
                    return function(match, offset, string) {
                        const shortNames = CleressianDate.MONTHS.slice(1, ).map(s => s.substring(0, 3));
                        return "(?<b>" + shortNames.join("|") + ")";
                    };
                case "B":
                    // long month names
                    return function(match, offset, string) {
                        return "(?<B>" + CleressianDate.MONTHS.slice(1, ).join("|") + ")";
                    }
                case "%":
                    // return a literal percent sign
                    return function(match, offset, string) {
                        return "%";
                    }
            };
        }

        for (let key of "gcymdjY") { template = template.replace(new RegExp('%(0\\d+)?' + key), convert(key)); }
        for (let key of "bB%") { template = template.replace(new RegExp("%" + key), convert(key)); }

        // at this point, template contains the *actual* regexp we can use to parse the date string
        const match = dateStr.match(new RegExp("^" + template + "$"));
        if(match === null) {
            throw new RangeError("Date data « " + dateStr + " » does not match format « " + _template + " »");
        }

        const result = {};      // the values that will be used to create the new object

        // first check for absolute dates
        let a = CleressianDate.fromAbsoluteDate(1, 1);

        if (match.groups.Y !== undefined) {
            const absyear = parseInt(match.groups.Y, 10);
            a = CleressianDate.fromAbsoluteDate(absyear, 1);

            result.grandCycle = a.grandCycle;
            result.cycle = a.cycle;
            result.year = a.year;
        }

        if (match.groups.j !== undefined) {
            const absday = parseInt(match.groups.j, 10);
            const s = CleressianDate.fromAbsoluteDate(1, absday);
            if (a === undefined) {
                a = s.copy();
            } else {
                a = a.replace({month: s.month, day: s.day});
            }

            result.month = a.month;
            result.day = a.day;
        }

        // now check for individual values
        const update = function(reKey, longName) {
            if (reKey in match.groups) {
                const raw = match.groups[reKey];

                const lookup = {
                    // find the index of the month with that abbreviation
                    "b": CleressianDate.MONTHS.map(x => x.substring(0, 3)).indexOf(raw),

                    // just leave the month value intact
                    "B": raw
                }
                const val = lookup.get(reKey, parseInt(raw, 10));

                if (longName in result) {
                    // we already defined this value in the absolute date

                    // true when the year is changed, false otherwise
                    const changeYear = Boolean(reKey.match(/[gcy]/));

                    // determine the "new" value
                    const repl = {}; repl[longName] = val;
                    const updated = a.replace(repl);

                    // warning text
                    const fmt = changeYear ? "%04Y (%g:%c:%y)" : ".%03j (%B %02d)";
                    const prev = a.strftime(fmt);
                    const curr = updated.strftime(fmt);

                    if (prev !== curr) {
                        console.warn("strptime: " + longName + " overwritten: " + prev + " -> " + curr);
                    }
                }

                const repl = {}; repl[longName] = val;
                a = a.replace(repl);
                result[longName] = val;
            }
        }

        update("g", "grandCycle");
        update("c", "cycle");
        update("y", "year");
        update("m", "month");
        update("b", "month");
        update("B", "month");
        update("d", "day");

        // use 1 as default for all fields, overwritten by the values found above
        const {
            grandCycle = 1,
            cycle = 1,
            year = 1,
            month = 1,
            day = 1
        } = result;

        return new CleressianDate(grandCycle, cycle, year, month, day);
    }


    /** plus()
     * Add a number of years and days to the given date.
     * @param {int=} years the number of years to add
     * @param {int=} days the number of days to add
     * 
     * @returns {CleressianDate} the new date
     */
    plus(years = 0, days = 0) {
        let x = this.toAbsoluteDate();
        x.year += years;
        x.day += days;

        // adjust until a valid date
        while (true) {
            offset = (x.day < 1) ? -1 : 0;
            const tmp = CleressianDate.fromAbsoluteDate(x.year + offset);
            const daysInYear = CleressianDate.daysInYear(tmp.cycle, tmp.year);

            if (1 <= x.day && x.day <= daysInYear) { break; }

            const adj = (x.day < 1) ? -1 : 1;
            x.year += adj;
            x.day -= adj * daysInYear;
        }

        return CleressianDate.fromAbsoluteDate(x.year, x.day);
    }

    /** minus()
     * Add a number of years and days to the given date.
     * @param {int=} years the number of years to add
     * @param {int=} days the number of days to add
     * 
     * @returns {CleressianDate} the new date
     */
    minus(years = 0, days = 0) {
        return this.plus(-years, -days);
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

        // First, get the day to line up.
        if (ax.day <= ay.day) {
            result.days = ay.day - ax.day;
            ax.day = ay.day;
        } else {
            const tmp = CleressianDate.fromAbsoluteDate(ax.year);
            let daysInYear = CleressianDate.daysInYear(ax.cycle, ax.year);
            result.days = ay.day + (daysInYear - ax.day);
            ax.day = ay.day;
            ax.year++;
        }

        // now, just subtract the years
        result.years = ay.year - ax.year;

        return result;

    }
}