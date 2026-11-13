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

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date

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
SHARED_SETTINGS_KEY = "__shared_egp_settings__"


def _settings_file():
    """Return the per-user file used to remember EGP review choices."""
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return root / "INVO" / "egp_settings.json"


def _load_egp_settings(settings_key):
    try:
        with _settings_file().open("r", encoding="utf-8") as settings_file:
            settings = json.load(settings_file)
        saved_files = settings.get("files", {})
        if not isinstance(saved_files, dict):
            return None
        if settings_key in saved_files:
            return saved_files[settings_key]
        # Migrate settings saved by older versions, which kept one entry per
        # input path, into the new shared EGP configuration.
        if settings_key == SHARED_SETTINGS_KEY and saved_files:
            return list(saved_files.values())[-1]
        return None
    except (OSError, json.JSONDecodeError, AttributeError):
        return None


def _store_egp_settings(settings_key, saved_settings):
    path = _settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("r", encoding="utf-8") as settings_file:
            settings = json.load(settings_file)
    except (OSError, json.JSONDecodeError):
        settings = {}

    if not isinstance(settings, dict):
        settings = {}
    files = settings.setdefault("files", {})
    if not isinstance(files, dict):
        files = {}
        settings["files"] = files
    files[settings_key] = saved_settings

    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(temporary_path, path)


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

    def __init__(self, parent, statment_columns, settings_id=None, filename=None):
        super().__init__(parent, text="Amount in Egyptian pounds")
        self.filename = filename or str(settings_id or "this file")
        self.settings_key = SHARED_SETTINGS_KEY
        self._save_error_shown = False

        # Any numeric-looking column that is not one we produce ourselves is a
        # candidate for the hotel's own EGP amount.
        self.candidate_columns = [
            column
            for column in statment_columns
            if column not in (RATE_COLUMN, CALCULATED_COLUMN, DIFFERENCE_COLUMN)
        ]

        saved_settings = _load_egp_settings(self.settings_key)
        self.enabled = tk.BooleanVar(
            value=bool(saved_settings.get("enabled", False))
            if isinstance(saved_settings, dict)
            else False
        )
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
        saved_column = (
            saved_settings.get("hotel_column")
            if isinstance(saved_settings, dict)
            else None
        )
        if saved_column is None:
            saved_column = self._guess_column()
        self.column_box.set(saved_column)
        self.column_box.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.column_box.bind("<<ComboboxSelected>>", self._save_settings)

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

        self.reset_button = ttk.Button(
            self.body, text="Reset", command=self.reset_periods
        )
        self.reset_button.grid(row=3, column=1, sticky="w", padx=5, pady=4)

        saved_periods = (
            saved_settings.get("periods")
            if isinstance(saved_settings, dict)
            else None
        )
        if not isinstance(saved_periods, list):
            saved_periods = None
        if saved_periods is None:
            self.add_period(save=False)
        else:
            for period in saved_periods:
                if isinstance(period, dict):
                    self.add_period(period=period, save=False)
        self._toggle(save=False)

    def _guess_column(self):
        """Pre-select a column that looks like an EGP amount, if there is one."""
        for column in self.candidate_columns:
            name = str(column).lower()
            if "egp" in name or "pound" in name or "جنيه" in str(column):
                return column
        return self.CREATE_CHOICE

    def _toggle(self, save=True):
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
        if save:
            self._save_settings()

    def add_period(self, period=None, save=True):
        row = _PeriodRow(self.periods_frame, len(self.rows) + 1, self.remove_period)
        if period:
            try:
                row.from_entry.set_date(date.fromisoformat(period.get("from", "")))
                row.to_entry.set_date(date.fromisoformat(period.get("to", "")))
            except (TypeError, ValueError):
                pass
            row.rate_entry.insert(0, str(period.get("rate", "")))
        row.from_entry.bind("<<DateEntrySelected>>", self._save_settings)
        row.from_entry.bind("<FocusOut>", self._save_settings)
        row.to_entry.bind("<<DateEntrySelected>>", self._save_settings)
        row.to_entry.bind("<FocusOut>", self._save_settings)
        row.rate_entry.bind("<KeyRelease>", self._save_settings)
        row.rate_entry.bind("<FocusOut>", self._save_settings)
        self.rows.append(row)
        self._toggle(save=save)

    def remove_period(self, row):
        if len(self.rows) == 1:
            # Keep one line on screen so the menu never looks broken.
            row.rate_entry.delete(0, tk.END)
            self._save_settings()
            return
        row.destroy()
        self.rows.remove(row)
        for row_index, remaining in enumerate(self.rows, start=1):
            remaining.grid(row_index)
        self._save_settings()

    def reset_periods(self):
        """Remove every rate period after the user confirms the reset."""
        confirmed = messagebox.askyesno(
            "Reset Egyptian pound periods",
            f"Remove all rate periods for {self.filename}?",
            parent=self.winfo_toplevel(),
        )
        if not confirmed:
            return
        for row in self.rows:
            row.destroy()
        self.rows.clear()
        self._save_settings()

    def _save_settings(self, _event=None):
        """Remember the current controls as they are edited."""
        periods = []
        for row in self.rows:
            try:
                start = row.from_entry.get_date().isoformat()
                end = row.to_entry.get_date().isoformat()
            except (ValueError, TypeError):
                # DateEntry can temporarily contain a partially typed date.
                start = row.from_entry.get()
                end = row.to_entry.get()
            periods.append({
                "from": start,
                "to": end,
                "rate": row.rate_entry.get().strip(),
            })

        settings = {
            "enabled": bool(self.enabled.get()),
            "hotel_column": self.column_box.get(),
            "periods": periods,
        }
        try:
            _store_egp_settings(self.settings_key, settings)
            self._save_error_shown = False
        except OSError as error:
            if not self._save_error_shown:
                messagebox.showerror(
                    "Could not save Egyptian pound settings",
                    f"The settings could not be saved for next time.\n\n{error}",
                    parent=self.winfo_toplevel(),
                )
                self._save_error_shown = True

    def get_settings(self):
        """The chosen settings, or raise :class:`RateError` if they are invalid."""
        self._save_settings()
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
