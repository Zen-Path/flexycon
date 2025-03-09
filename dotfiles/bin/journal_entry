#!/bin/python3

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

ABS_DATE_FMTS = ["%Y.%m.%d", "%m.%d"]


def format_help_choices(choices):
    return " | ".join([f"'{str(choice).replace('%', '%%')}'" for choice in choices])


def clean_abs_date(abs_date):
    # Mainly used for arguments containing the extension (e.g "2024.05.03.md")
    return re.sub(r"[^\d.]+", "", abs_date).strip(".")


def abs_date(date: str, date_fmts: list[str] = ABS_DATE_FMTS):
    for fmt in date_fmts:
        try:
            parsed_date = datetime.strptime(clean_abs_date(date), fmt)

            # If year is not specified, default to the current one
            if "%Y" not in fmt and "%y" not in fmt:
                parsed_date = parsed_date.replace(year=datetime.now().year)

            return parsed_date
        except ValueError:
            continue  # Try the next format

    raise ValueError("Invalid date format")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Opens a journal entry in an editor based on a specified absolute or relative date. "
        "If no date is specified, it defaults to the current date. If no $EDITOR is found, "
        "it defaults to 'vim'."
    )
    parser.add_argument(
        "relative_date",
        nargs="?",
        type=int,
        metavar="REL_DATE",
        help=f"Relative date. Format: {format_help_choices(['-int', 'int', '+int'])}.",
    )
    parser.add_argument(
        "-a",
        "--absolute-date",
        type=abs_date,
        metavar="ABS_DATE",
        help=f"Absolute date. Format: {format_help_choices(ABS_DATE_FMTS)}.",
    )

    return parser.parse_args()


def determine_date(args):
    if args.absolute_date is not None:
        return args.absolute_date

    current_time = datetime.now()
    if args.relative_date:
        return current_time + timedelta(days=args.relative_date)

    return current_time


def parse_date_obj(date_obj):
    return {
        "year": date_obj.year,
        "month_num": date_obj.month,
        "month_name_full": date_obj.strftime("%B"),
        "month_name_short": date_obj.strftime("%b"),
        "day": date_obj.day,
    }


def prompt_user(prompt, positive_resp=["y"], negative_resp=["n"], default="n"):
    possible_resp = positive_resp + negative_resp
    if default not in possible_resp:
        return False

    default_index = possible_resp.index(default)
    possible_resp[default_index] = possible_resp[default_index].upper()
    user_resp = input(f"> {prompt} ({'/'.join(possible_resp)}): ").strip().lower()

    return user_resp in positive_resp


def ensure_directory(path):
    if not os.path.exists(path):
        print(f":: The directory '{path}' does not exist.")
        user_resp = prompt_user("Would you like to create the directory?")
        if user_resp:
            os.makedirs(path)
        else:
            print(":: Operation cancelled by user.")
            sys.exit(1)


def open_journal_entry(date_obj):
    year = str(date_obj["year"])
    month_num = f"{date_obj['month_num']:02}"
    journal_home_dir = os.environ["JOURNAL_HOME"]

    if not journal_home_dir:
        raise EnvironmentError("JOURNAL_HOME environment variable is not set.")

    journal_year_dir = os.path.join(journal_home_dir, year)
    journal_month_dir = os.path.join(journal_year_dir, month_num)

    ensure_directory(journal_year_dir)
    ensure_directory(journal_month_dir)

    file_path = os.path.join(journal_month_dir, f"{month_num}.{date_obj['day']:02}.md")
    editor = os.getenv("EDITOR", "vim")
    subprocess.run([editor, file_path])


# TODO: add logging
# TODO: add tests
def main():
    args = parse_args()
    target_date_obj = determine_date(args)
    open_journal_entry(parse_date_obj(target_date_obj))


if __name__ == "__main__":
    main()
