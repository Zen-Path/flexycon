from typing import Literal


def resolve_icon(
    volume: float, is_muted: bool
) -> Literal["🔇"] | Literal["🔊"] | Literal["🔉"] | Literal["🔈"]:
    if is_muted:
        return "🔇"

    if volume >= 70:
        return "🔊"

    if volume >= 30:
        return "🔉"

    return "🔈"
