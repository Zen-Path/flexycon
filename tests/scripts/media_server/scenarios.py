from datetime import datetime, timedelta


def get_default_data():
    now = datetime.now()
    return [
        # --- RECENT (Minutes/Seconds ago) ---
        (
            "https://www.youtube.com/watch?v=test_video",
            "Rick Astley - Never Gonna Give You Up (Official Music Video)",
            "video",
            (now - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://very-long-url-website.com/long-title-test",
            "This is an extremely long title to test if the CSS truncation works correctly in the dashboard table row and does not break the layout of the cell",
            "unknown",
            (now - timedelta(seconds=45)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(seconds=5)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://twitter.com/updates/status/12345",
            "Breaking News: Python 3.14 Released 🚀",
            "image",
            (now - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://cdn.example.com/assets/logo.png",
            None,  # Missing title
            "image",
            (now - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(minutes=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),  # Instant download
        ),
        # --- TODAY (Hours ago) ---
        (
            "https://imgur.com/gallery/cats",
            "Best Cat Memes 2025",
            "gallery",
            (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(hours=1, minutes=55)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://vimeo.com/12345678",
            'Documentary: "The Life of a Software Engineer"',
            "video",
            (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(hours=3, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://unsplash.com/photos/mountain-view",
            "High resolution mountain landscape [4K]",
            "image",
            (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(hours=4, minutes=59)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://github.com/torvalds/linux/archive/master.zip",
            "linux-master.zip",
            "unknown",
            (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(hours=5, minutes=50)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.tiktok.com/@user/video/987654",
            "Viral Dance Challenge #2025",
            "video",
            (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(hours=7, minutes=59)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        # --- YESTERDAY ---
        (
            "https://example.com/missing-title-2",
            None,
            "gallery",
            (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.nasa.gov/image-of-the-day",
            "Nebula Cluster from James Webb Telescope",
            "image",
            (now - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=1, hours=1, minutes=50)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ),
        (
            "https://stackoverflow.com/questions/12345",
            "How to exit vim? - Stack Overflow",
            "unknown",
            (now - timedelta(days=1, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=1, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.ted.com/talks/future_of_ai",
            "The Future of AI and Humanity",
            "video",
            (now - timedelta(days=1, hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=1, hours=9)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        # --- THIS WEEK (Testing Sorting) ---
        (
            "https://www.reddit.com/r/funny/top",
            "Top posts from r/funny this week",
            "gallery",
            (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://jp.wikipedia.org/wiki/Python",
            "Python (プログラミング言語) - Wikipedia",  # Unicode Test (Japanese)
            "unknown",
            (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://ar.wikipedia.org/wiki/Python",
            "بايثون (لغة برمجة) - ويكيبيديا",  # Unicode Test (Arabic)
            "unknown",
            (now - timedelta(days=3, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=3, hours=0, minutes=59)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ),
        (
            "https://spotify.com/track/123",
            "lofi hip hop radio - beats to relax/study to",
            "video",
            (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=3, hours=20)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),  # Long download
        ),
        (
            "https://www.bbc.com/news/technology",
            "Technology News - BBC News",
            "unknown",
            (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.deviantart.com/art/digital-painting",
            "Cyberpunk Cityscape Concept Art",
            "image",
            (now - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.twitch.tv/videos/111222333",
            "Grand Finals - EVO 2025",
            "video",
            (now - timedelta(days=6, hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=6, hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        # --- OLDER (Last Month) ---
        (
            "https://archive.org/details/old-movie",
            "'Metropolis (1927)' - Full Movie",
            "video",
            (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.pinterest.com/pin/12345",
            "DIY Home Decor Ideas",
            "gallery",
            (now - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.behance.net/gallery/ui-kit",
            "Mobile App UI Kit Freebie",
            "gallery",
            (now - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.coursera.org/learn/machine-learning",
            "Machine Learning Specialization",
            "video",
            (now - timedelta(days=18)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=17, hours=23)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://192.168.1.1/config.backup",
            "Router Configuration Backup",
            "unknown",
            (now - timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://example.com/very/deeply/nested/url/structure/that/goes/on/forever/and/ever/to/test/wrapping",
            "Deeply Nested URL Test",
            "unknown",
            (now - timedelta(days=22)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=22)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://wallhaven.cc/w/123",
            "Abstract Geometric Wallpaper",
            "image",
            (now - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.instagram.com/p/Cxyz123",
            "Sunset at the beach 🏖️",
            "image",
            (now - timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.soundcloud.com/artist/song",
            "New Single - Summer Vibes",
            "unknown",
            (now - timedelta(days=29)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=29)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.dropbox.com/s/shared/project.pdf",
            "Final_Project_Report_v2_FINAL_REAL.pdf",
            "unknown",
            (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "https://www.youtube.com/watch?v=intro",
            "Channel Intro",
            "video",
            (now - timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S"),
            (now - timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    ]
