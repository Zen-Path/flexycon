import random
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional

from scripts.media_server.src.constants import MediaType


def validate_seed_data(data):
    for i, entry in enumerate(data):
        url = entry.get("url", "Unknown URL")
        start = entry["start_time"]
        end = entry["end_time"]

        if end and end < start:
            raise ValueError(
                f"Item #{i} ({url!r}): 'end_time' is earlier than 'start_time'."
            )


DEFAULT_OPTIONS = {
    "end_time_probability": 0.9,
    "max_days_offset": 200,
    "max_duration_seconds": 3600,
    "min_duration_seconds": 5,
    "seed": 42,
}


@lru_cache(maxsize=1)
def get_demo_downloads(
    now: Optional[datetime] = None, row_count: Optional[int] = None, **options: Any
) -> List[Dict[str, Any]]:
    config = {**DEFAULT_OPTIONS, **options}

    # Avoid side effects on global random
    rng = random.Random(config["seed"])

    if now is None:
        now = datetime.now()

    base_data: List[Dict[str, Any]] = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "title": "Rick Astley - Never Gonna Give You Up (Official Video) - YouTube",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(seconds=2),
            "end_time": now,
        },
        {
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "title": "Me at the zoo - YouTube",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(seconds=30),
            "end_time": now - timedelta(seconds=25),
        },
        # Long title
        {
            "url": "https://very-long-url-website.com/long-title-test",
            "title": "This is an extremely long title to test if the CSS truncation"
            "works correctly in the dashboard table row and does not break the layout"
            "of the cell",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(minutes=1, seconds=10),
            "end_time": now - timedelta(minutes=1, seconds=5),
        },
        {
            "url": "https://x.com/updates/status/12345",
            "title": "Breaking News: Python 3.14 Released 🚀",
            "media_type": MediaType.IMAGE,
            "start_time": now - timedelta(minutes=5, seconds=25),
            "end_time": now - timedelta(minutes=5, seconds=20),
        },
        # Missing title
        {
            "url": "https://cdn.example.com/assets/logo.png",
            "title": None,
            "media_type": MediaType.IMAGE,
            "start_time": now - timedelta(hours=1, minutes=1, seconds=10),
            "end_time": now - timedelta(hours=1, minutes=1, seconds=5),
        },
        # Gallery media
        {
            "url": "https://imgur.com/gallery/cats",
            "title": "Best Cat Memes 2025",
            "media_type": MediaType.GALLERY,
            "start_time": now - timedelta(hours=1, minutes=45, seconds=10),
            "end_time": now - timedelta(hours=1, minutes=45, seconds=5),
        },
        # Double quotes in title
        {
            "url": "https://vimeo.com/12345678",
            "title": 'Documentary: "The Life of a Software Engineer"',
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(hours=2, minutes=5, seconds=40),
            "end_time": now - timedelta(hours=2, minutes=5, seconds=35),
        },
        {
            "url": "https://unsplash.com/photos/mountain-view",
            "title": "High resolution mountain landscape [4K]",
            "media_type": MediaType.IMAGE,
            "start_time": now - timedelta(hours=3, minutes=10, seconds=10),
            "end_time": now - timedelta(hours=3, minutes=10, seconds=5),
        },
        # Direct zip link
        {
            "url": "https://github.com/torvalds/linux/archive/master.zip",
            "title": "linux-master.zip",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(hours=3, minutes=20, seconds=20),
            "end_time": now - timedelta(hours=3, minutes=20, seconds=10),
        },
        {
            "url": "https://www.tiktok.com/@user/video/987654",
            "title": "Viral Dance Challenge #2025",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(hours=4, minutes=20, seconds=30),
            "end_time": now - timedelta(hours=4, minutes=20, seconds=25),
        },
        {
            "url": "https://example.com/missing-title-2",
            "title": None,
            "media_type": MediaType.GALLERY,
            "start_time": now - timedelta(hours=4, minutes=30, seconds=35),
            "end_time": now - timedelta(hours=4, minutes=30, seconds=25),
        },
        # Start time = end time
        {
            "url": "https://www.nasa.gov/image-of-the-day",
            "title": "Nebula Cluster from James Webb Telescope",
            "media_type": MediaType.IMAGE,
            "start_time": now - timedelta(hours=5, minutes=1, seconds=1),
            "end_time": now - timedelta(hours=5, minutes=1, seconds=1),
        },
        # Same start time for the next 2
        {
            "url": "https://stackoverflow.com/questions/12345",
            "title": "How to exit vim? - Stack Overflow",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(hours=6, minutes=1, seconds=10),
            "end_time": now - timedelta(hours=6, minutes=1, seconds=5),
        },
        {
            "url": "https://www.ted.com/talks/future_of_ai",
            "title": "The Future of AI and Humanity",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(hours=6, minutes=1, seconds=10),
            "end_time": now - timedelta(hours=6, minutes=1, seconds=1),
        },
        # Long running
        {
            "url": "https://www.reddit.com/r/funny/top",
            "title": "Top posts from r/funny this week",
            "media_type": MediaType.GALLERY,
            "start_time": now - timedelta(hours=6, minutes=5, seconds=1),
            "end_time": now - timedelta(hours=5, minutes=1, seconds=10),
        },
        # Emoji in title
        {
            "url": "https://jp.wikipedia.org/wiki/Python",
            "title": "Python (🐍) - Wikipedia",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(hours=7, minutes=1, seconds=10),
            "end_time": now - timedelta(hours=7, minutes=1, seconds=1),
        },
        # Right-to-left title
        {
            "url": "https://ar.wikipedia.org/wiki/Python",
            "title": "بايثون (لغة برمجة) - ويكيبيديا",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(hours=7, minutes=5, seconds=10),
            "end_time": now - timedelta(hours=7, minutes=5, seconds=1),
        },
        # Yesterday
        {
            "url": "https://spotify.com/track/123",
            "title": "lofi hip hop radio - beats to relax/study to",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(days=1, hours=1, minutes=5, seconds=10),
            "end_time": now - timedelta(days=1, hours=1, minutes=5, seconds=5),
        },
        {
            "url": "https://www.bbc.com/news/technology",
            "title": "Technology News - BBC News",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(days=1, hours=2, minutes=5, seconds=15),
            "end_time": now - timedelta(days=1, hours=2, minutes=5, seconds=10),
        },
        {
            "url": "https://www.deviantart.com/art/digital-painting",
            "title": "Cyberpunk Cityscape Concept Art",
            "media_type": MediaType.IMAGE,
            "start_time": now - timedelta(days=1, hours=15, minutes=55, seconds=10),
            "end_time": now - timedelta(days=1, hours=15, minutes=50, seconds=5),
        },
        # This week
        {
            "url": "https://www.twitch.tv/videos/111222333",
            "title": "Grand Finals - EVO 2025",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(days=2, hours=1, minutes=5, seconds=10),
            "end_time": now - timedelta(days=2, hours=1, minutes=5, seconds=5),
        },
        {
            "url": "https://archive.org/details/old-movie",
            "title": "'Metropolis (1927)' - Full Movie",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(days=2, hours=5, minutes=25, seconds=10),
            "end_time": now - timedelta(days=2, hours=5, minutes=25, seconds=5),
        },
        {
            "url": "https://www.pinterest.com/pin/12345",
            "title": "DIY Home Decor Ideas",
            "media_type": MediaType.GALLERY,
            "start_time": now - timedelta(days=4, hours=1, minutes=5, seconds=10),
            "end_time": now - timedelta(days=4, hours=1, minutes=5, seconds=5),
        },
        # Last week
        {
            "url": "https://www.behance.net/gallery/ui-kit",
            "title": "Mobile App UI Kit Freebie",
            "media_type": MediaType.GALLERY,
            "start_time": now - timedelta(days=7, hours=1, minutes=5, seconds=10),
            "end_time": now - timedelta(days=7, hours=1, minutes=5, seconds=5),
        },
        {
            "url": "https://www.coursera.org/learn/machine-learning",
            "title": "Machine Learning Specialization",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(days=8, hours=1, minutes=5, seconds=10),
            "end_time": now - timedelta(days=8, hours=1, minutes=5, seconds=5),
        },
        {
            "url": "https://192.168.1.1/config.backup",
            "title": "Router Configuration Backup",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(days=9, hours=1, minutes=5, seconds=10),
            "end_time": now - timedelta(days=9, hours=1, minutes=5, seconds=5),
        },
        {
            "url": "https://example.com/very/deeply/nested/url/structure/that/goes/on/forever/and/ever/to/test/wrapping",
            "title": "Deeply Nested URL Test",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(days=10, hours=1, minutes=5, seconds=10),
            "end_time": now - timedelta(days=10, hours=1, minutes=5, seconds=5),
        },
        # Last month
        {
            "url": "https://wallhaven.cc/w/123",
            "title": "Abstract Geometric Wallpaper",
            "media_type": MediaType.IMAGE,
            "start_time": now - timedelta(days=32, hours=1, minutes=5, seconds=10),
            "end_time": now - timedelta(days=32, hours=1, minutes=5, seconds=5),
        },
        {
            "url": "https://www.instagram.com/p/Cxyz123",
            "title": "Sunset at the beach 🏖️",
            "media_type": MediaType.IMAGE,
            "start_time": now - timedelta(days=35, hours=1, seconds=10),
            "end_time": now - timedelta(days=35, hours=1, seconds=5),
        },
        {
            "url": "https://www.soundcloud.com/artist/song",
            "title": "New Single - Summer Vibes",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(days=40, hours=5, seconds=10),
            "end_time": now - timedelta(days=40, hours=5, seconds=5),
        },
        # Very old entries
        {
            "url": "https://www.dropbox.com/s/shared/project.pdf",
            "title": "Final_Project_Report_v2_FINAL_REAL.pdf",
            "media_type": MediaType.TEXT,
            "start_time": now - timedelta(days=90, hours=1, seconds=10),
            "end_time": now - timedelta(days=90, hours=1, seconds=5),
        },
        {
            "url": "https://www.youtube.com/watch?v=intro",
            "title": "Channel Intro",
            "media_type": MediaType.VIDEO,
            "start_time": now - timedelta(days=195, hours=10, seconds=10),
            "end_time": now - timedelta(days=195, hours=10, seconds=5),
        },
    ]

    data = list(base_data)

    if row_count is not None:
        if row_count > len(data):
            metadata_pool = [{"url": d["url"], "title": d["title"]} for d in base_data]

            extra_needed = row_count - len(data)
            for _ in range(extra_needed):
                source = rng.choice(metadata_pool)

                days_offset = rng.randint(0, config["max_days_offset"])
                seconds_offset = rng.randint(0, 86400)
                start_time = now - timedelta(days=days_offset, seconds=seconds_offset)

                end_time = None
                if rng.random() < config["end_time_probability"]:
                    duration = rng.randint(
                        config["min_duration_seconds"], config["max_duration_seconds"]
                    )
                    end_time = start_time + timedelta(seconds=duration)

                data.append(
                    {
                        "url": source["url"],
                        "title": source["title"],
                        "media_type": rng.choice(list(MediaType)),
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                )
        else:
            data = data[:row_count]

    data.sort(key=lambda x: x["start_time"], reverse=False)

    validate_seed_data(data)

    return data
