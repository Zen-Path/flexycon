#!/usr/bin/env python3


def format_help_choices(choices):
    return " | ".join([f"'{str(choice).replace('%', '%%')}'" for choice in choices])
