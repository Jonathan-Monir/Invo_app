"""Egyptian pound (EGP) review support.

Two pieces live here:

* ``RatePeriods`` -- the pure logic. A list of non-overlapping [from, to] date
  periods, each with a pounds-per-dollar rate, plus the lookup that maps a
  row's Departure date onto its rate.
* ``EgpFrame`` -- the Tkinter menu shown under each file on the Export Data
  page: pick the existing EGP column (review it) or ask the app to create one,
  then type the rate periods.

Periods are inclusive at both ends and are validated to not overlap, so a date
never matches two rates. Entering 17/4-23/4 followed by 23/4-28/4 is rejected
with a message asking for 24/4, rather than silently picking a winner.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import pandas as pd
from tkcalendar import DateEntry


# Column names added to the output when the EGP review is enabled.
RATE_COLUMN = "Rate EGP/$"
CALCULATED_COLUMN = "Total price EGP"
HOTEL_COLUMN = "Amount-hotel EGP"
DIFFERENCE_COLUMN = "Difference EGP"

# The statement column whose date decides which rate period a row falls in.
DATE_COLUMN = "Departure"


class RateError(Exception):
    """Raised when the rate periods the user typed do not make sense."""


class RatePeriods:
    """A validated set of dated pounds-per-dollar rates."""

    def __init__(self, periods):
        """``periods`` is a list of (start, end, rate) with dates and a number."""
        self.periods = self._validate(periods)

    @staticmethod
    def _validate(periods):
        cleaned = []
        for index, (start, end, rate) in enumerate(periods, start=1):
            start = pd.Timestamp(start).normalize()
            end = pd.Timestamp(end).normalize()

            if pd.isna(start) or pd.isna(end):
                raise RateError(f"Period {index}: both dates are required.")
            if start > end:
                raise RateError(
                    f"Period {index}: the 'from' date ({start:%d/%m/%Y}) is after "
                    f"the 'to' date ({end:%d/%m/%Y})."
                )
            try:
                rate = float(rate)
            except (TypeError, ValueError):
                raise RateError(f"Period {index}: the rate must be a number.")
            if rate <= 0:
                raise RateError(f"Period {index}: the rate must be greater than zero.")

            cleaned.append((start, end, rate))

        if not cleaned:
            raise RateError("Add at least one rate period.")

        # Sort by start date so overlaps are only ever between neighbours, and
        # so the message below can name the two offending periods clearly.
        cleaned.sort(key=lambda period: period[0])

        for earlier, later in zip(cleaned, cleaned[1:]):
            if later[0] <= earlier[1]:
                raise RateError(
                    "Two periods overlap: "
                    f"{earlier[0]:%d/%m/%Y}-{earlier[1]:%d/%m/%Y} and "
                    f"{later[0]:%d/%m/%Y}-{later[1]:%d/%m/%Y}. "
                    "Periods include both of their dates, so the second one "
                    f"should start on {(earlier[1] + pd.Timedelta(days=1)):%d/%m/%Y}."
                )

        return cleaned

    def rate_for(self, date):
        """The rate covering ``date``, or None when no period covers it."""
        if pd.isna(date):
            return None
        date = pd.Timestamp(date).normalize()
        for start, end, rate in self.periods:
            if start <= date <= end:
                return rate
        return None

    def rates_for(self, dates):
        """Vectorised :meth:`rate_for` over a pandas Series.

        Uncovered rows come back as ``NaN`` rather than ``pd.NA``: openpyxl
        refuses to write ``pd.NA``, while ``NaN`` becomes an empty cell.
        """
        dates = pd.to_datetime(dates, errors="coerce").dt.normalize()
        rates = pd.Series(np.nan, index=dates.index, dtype="float64")
        for start, end, rate in self.periods:
            covered = dates.between(start, end) & rates.isna()
            rates.loc[covered] = rate
        return rates


class EgpSettings:
    """What the user chose for one file on the Export Data page."""

    def __init__(self, enabled, rate_periods, hotel_egp_column=None):
        self.enabled = enabled
        self.rate_periods = rate_periods
        # None means "create the EGP column"; otherwise the statement column
        # holding the hotel's own EGP amount, which we check against.
        self.hotel_egp_column = hotel_egp_column


def apply_egp(statment, settings):
    """Add the EGP columns to ``statment`` in place.

    Returns the number of rows whose Departure date matched no rate period.
    """
    if not settings.enabled:
        return 0

    rates = settings.rate_periods.rates_for(statment[DATE_COLUMN])
    statment[RATE_COLUMN] = rates
    statment[CALCULATED_COLUMN] = (
        pd.to_numeric(statment["Total price"], errors="coerce") * rates
    ).round(2)

    hotel_column = settings.hotel_egp_column
    if hotel_column and hotel_column in statment.columns:
        hotel_amounts = pd.to_numeric(statment[hotel_column], errors="coerce")
        if hotel_column != HOTEL_COLUMN:
            statment[HOTEL_COLUMN] = hotel_amounts
        statment[DIFFERENCE_COLUMN] = (
            statment[CALCULATED_COLUMN] - hotel_amounts
        ).round(2)
        # Mirror the dollar check: rounding noise under half a pound is not a
        # real difference and should not be highlighted.
        small = statment[DIFFERENCE_COLUMN].abs() < 0.5
        statment.loc[small.fillna(False), DIFFERENCE_COLUMN] = 0

    return int(rates.isna().sum())


def order_egp_columns(columns, has_hotel_egp):
    """Move the EGP columns to the end, in a readable order."""
    egp_columns = [RATE_COLUMN, CALCULATED_COLUMN]
    if has_hotel_egp:
        egp_columns += [HOTEL_COLUMN, DIFFERENCE_COLUMN]

    ordered = [column for column in columns if column not in egp_columns]
    ordered += [column for column in egp_columns if column in columns]
    return ordered


class _PeriodRow:
    """One 'from / to / rate' line in the rate menu."""

    def __init__(self, parent, row_index, on_remove):
        self.frame = parent
        self.from_entry = DateEntry(parent, width=11, date_pattern="dd/mm/yyyy")
        self.to_entry = DateEntry(parent, width=11, date_pattern="dd/mm/yyyy")
        self.rate_entry = ttk.Entry(parent, width=10)
        self.remove_button = ttk.Button(
            parent, text="x", width=3, command=lambda: on_remove(self)
        )
        self.grid(row_index)

    def grid(self, row_index):
        self.from_entry.grid(row=row_index, column=0, padx=2, pady=2)
        self.to_entry.grid(row=row_index, column=1, padx=2, pady=2)
        self.rate_entry.grid(row=row_index, column=2, padx=2, pady=2)
        self.remove_button.grid(row=row_index, column=3, padx=2, pady=2)

    def destroy(self):
        for widget in (self.from_entry, self.to_entry, self.rate_entry, self.remove_button):
            widget.destroy()

    def values(self):
        return (
            self.from_entry.get_date(),
            self.to_entry.get_date(),
            self.rate_entry.get().strip(),
        )

    def is_blank(self):
        return not self.rate_entry.get().strip()


class EgpFrame(ttk.LabelFrame):
    """The per-file EGP menu on the Export Data page."""

    CREATE_CHOICE = "Create the EGP column"

    def __init__(self, parent, statment_columns):
        super().__init__(parent, text="Amount in Egyptian pounds")

        # Any numeric-looking column that is not one we produce ourselves is a
        # candidate for the hotel's own EGP amount.
        self.candidate_columns = [
            column
            for column in statment_columns
            if column not in (RATE_COLUMN, CALCULATED_COLUMN, DIFFERENCE_COLUMN)
        ]

        self.enabled = tk.BooleanVar(value=False)
        self.enable_check = ttk.Checkbutton(
            self,
            text="Review the amount in Egyptian pounds",
            variable=self.enabled,
            command=self._toggle,
        )
        self.enable_check.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=3)

        self.body = ttk.Frame(self)
        self.body.grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

        ttk.Label(self.body, text="EGP amount column:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.column_box = ttk.Combobox(
            self.body,
            values=[self.CREATE_CHOICE] + self.candidate_columns,
            state="readonly",
            width=28,
        )
        self.column_box.set(self._guess_column())
        self.column_box.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(
            self.body,
            text="Rate per period (pounds for one dollar), matched on Departure date:",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 2))

        self.periods_frame = ttk.Frame(self.body)
        self.periods_frame.grid(row=2, column=0, columnspan=2, sticky="w")

        for header_index, header in enumerate(("From", "To", "Rate", "")):
            ttk.Label(self.periods_frame, text=header).grid(
                row=0, column=header_index, padx=2
            )

        self.rows = []
        self.add_button = ttk.Button(
            self.body, text="Add period", command=self.add_period
        )
        self.add_button.grid(row=3, column=0, sticky="w", pady=4)

        self.add_period()
        self._toggle()

    def _guess_column(self):
        """Pre-select a column that looks like an EGP amount, if there is one."""
        for column in self.candidate_columns:
            name = str(column).lower()
            if "egp" in name or "pound" in name or "جنيه" in str(column):
                return column
        return self.CREATE_CHOICE

    def _toggle(self):
        state = "normal" if self.enabled.get() else "disabled"
        self.column_box.configure(state="readonly" if self.enabled.get() else "disabled")
        self.add_button.configure(state=state)
        for row in self.rows:
            for widget in (
                row.from_entry,
                row.to_entry,
                row.rate_entry,
                row.remove_button,
            ):
                widget.configure(state=state)

    def add_period(self):
        row = _PeriodRow(self.periods_frame, len(self.rows) + 1, self.remove_period)
        self.rows.append(row)
        self._toggle()

    def remove_period(self, row):
        if len(self.rows) == 1:
            # Keep one line on screen so the menu never looks broken.
            row.rate_entry.delete(0, tk.END)
            return
        row.destroy()
        self.rows.remove(row)
        for row_index, remaining in enumerate(self.rows, start=1):
            remaining.grid(row_index)

    def get_settings(self):
        """The chosen settings, or raise :class:`RateError` if they are invalid."""
        if not self.enabled.get():
            return EgpSettings(enabled=False, rate_periods=None)

        typed = [row.values() for row in self.rows if not row.is_blank()]
        if not typed:
            raise RateError("Add at least one rate period, or untick the EGP review.")

        rate_periods = RatePeriods(typed)

        choice = self.column_box.get()
        hotel_column = None if choice == self.CREATE_CHOICE else choice
        return EgpSettings(True, rate_periods, hotel_column)


def ask_settings(frame, filename):
    """Read one file's settings, showing the error in a dialog if invalid."""
    try:
        return frame.get_settings()
    except RateError as error:
        messagebox.showerror(f"Egyptian pound rates - {filename}", str(error))
        return None
