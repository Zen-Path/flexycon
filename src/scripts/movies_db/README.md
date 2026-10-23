# Movies DB

## Formulas

### Movies

release year:

```
=ARRAYFORMULA(
    LEFT(Movies[Release Date], 4)
)
```

watch count:

```
=MAP(
    Movies[Title], LAMBDA(key,
        IF(
            key="", "",
            COUNTIFS(
                Movies_History[Title], key,
                Movies_History[Status], "Finished"
            )
        )
    )
)
```

movie dupe index:

```
=MAP(
    Movies[Title],
    SEQUENCE(ROWS(Movies[Title])),
    LAMBDA(val, idx,
        IF(
            val="", "",
            COUNTIF(INDEX(Movies[Title], 1):INDEX(Movies[Title], idx), val)
        )
    )
)
```

### TV Series

release year:

```
=ARRAYFORMULA(
    LEFT(TV_Series[First Air Date], 4)
)
```

series dupe index:

```
=MAP(
    TV_Series[Title],
    SEQUENCE(ROWS(TV_Series[Title])),
    LAMBDA(val, idx,
        IF(
            val="", "",
            COUNTIF(INDEX(TV_Series[Title], 1):INDEX(TV_Series[Title], idx), val)
        )
    )
)
```

## TMDb Responses

Movie overview:

```py
{
    "movie_results": [
        {
            "adult": False,
            "backdrop_path": "/pNjh59JSxChQktamG3LMp9ZoQzp.jpg",
            "id": 278,
            "title": "The Shawshank Redemption",
            "original_title": "The Shawshank Redemption",
            "overview": "Imprisoned in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison, where he puts his accounting skills to work for an amoral warden. During his long stretch in prison, Dufresne comes to be admired by the other inmates -- including an older prisoner named Red -- for his integrity and unquenchable sense of hope.",
            "poster_path": "/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg",
            "media_type": "movie",
            "original_language": "en",
            "genre_ids": [18, 80],
            "popularity": 53.2887,
            "release_date": "1994-09-23",
            "softcore": False,
            "video": False,
            "vote_average": 8.732,
            "vote_count": 31610,
        }
    ],
    "person_results": [],
    "tv_results": [],
    "tv_episode_results": [],
    "tv_season_results": [],
}
```

Movie detailed:

```py
{
    "adult": False,
    "backdrop_path": "/pNjh59JSxChQktamG3LMp9ZoQzp.jpg",
    "belongs_to_collection": None,
    "budget": 25000000,
    "genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
    "homepage": "",
    "id": 278,
    "imdb_id": "tt0111161",
    "origin_country": ["US"],
    "original_language": "en",
    "original_title": "The Shawshank Redemption",
    "overview": "Imprisoned in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison, where he puts his accounting skills to work for an amoral warden. During his long stretch in prison, Dufresne comes to be admired by the other inmates -- including an older prisoner named Red -- for his integrity and unquenchable sense of hope.",
    "popularity": 53.2887,
    "poster_path": "/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg",
    "production_companies": [
        {
            "id": 97,
            "logo_path": "/smyTD67uNsdaySnnjVDmh0kyotp.png",
            "name": "Castle Rock Entertainment",
            "origin_country": "US",
        }
    ],
    "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
    "release_date": "1994-09-23",
    "revenue": 28341469,
    "runtime": 142,
    "softcore": False,
    "spoken_languages": [
        {"english_name": "English", "iso_639_1": "en", "name": "English"}
    ],
    "status": "Released",
    "tagline": "Fear can hold you prisoner. Hope can set you free.",
    "title": "The Shawshank Redemption",
    "video": False,
    "vote_average": 8.732,
    "vote_count": 31610,
}
```

TV Series overview:

```py
{
    "movie_results": [],
    "person_results": [],
    "tv_results": [
        {
            "adult": False,
            "backdrop_path": "/zZqpAXxVSBtxV9qPBcscfXBcL2w.jpg",
            "id": 1399,
            "name": "Game of Thrones",
            "original_name": "Game of Thrones",
            "overview": "Seven noble families fight for control of the mythical land of Westeros. Friction between the houses leads to full-scale war. All while a very ancient evil awakens in the farthest north. Amidst the war, a neglected military order of misfits, the Night's Watch, is all that stands between the realms of men and icy horrors beyond.",
            "poster_path": "/1XS1oqL89opfnbLl8WnZY1O1uJx.jpg",
            "media_type": "tv",
            "original_language": "en",
            "genre_ids": [10765, 18, 10759],
            "popularity": 246.1416,
            "first_air_date": "2011-04-17",
            "softcore": False,
            "vote_average": 8.474,
            "vote_count": 27972,
            "origin_country": ["US"],
        }
    ],
    "tv_episode_results": [],
    "tv_season_results": [],
}
```

TV Series detailed:

```py
{
    "adult": False,
    "backdrop_path": "/zZqpAXxVSBtxV9qPBcscfXBcL2w.jpg",
    "created_by": [
        {
            "id": 9813,
            "credit_id": "5256c8c219c2956ff604858a",
            "name": "David Benioff",
            "original_name": "David Benioff",
            "gender": 2,
            "profile_path": "/xvNN5huL0X8yJ7h3IZfGG4O2zBD.jpg",
        },
    ],
    "episode_run_time": [],
    "first_air_date": "2011-04-17",
    "genres": [
        {"id": 10765, "name": "Sci-Fi & Fantasy"},
    ],
    "homepage": "https://www.hbo.com/game-of-thrones",
    "id": 1399,
    "in_production": False,
    "languages": ["en"],
    "last_air_date": "2019-05-19",
    "last_episode_to_air": {
        "id": 1551830,
        "name": "The Iron Throne",
        "overview": "In the aftermath of the devastating attack on King's Landing, Daenerys must face the survivors.",
        "vote_average": 4.5,
        "vote_count": 471,
        "air_date": "2019-05-19",
        "episode_number": 6,
        "episode_type": "finale",
        "production_code": "806",
        "runtime": 80,
        "season_number": 8,
        "show_id": 1399,
        "still_path": "/zBi2O5EJfgTS6Ae0HdAYLm9o2nf.jpg",
    },
    "name": "Game of Thrones",
    "next_episode_to_air": None,
    "networks": [
        {
            "id": 49,
            "logo_path": "/tuomPhY2UtuPTqqFnKMVHvSb724.png",
            "name": "HBO",
            "origin_country": "US",
        }
    ],
    "number_of_episodes": 73,
    "number_of_seasons": 8,
    "origin_country": ["US"],
    "original_language": "en",
    "original_name": "Game of Thrones",
    "overview": "Seven noble families fight for control of the mythical land of Westeros. Friction between the houses leads to full-scale war. All while a very ancient evil awakens in the farthest north. Amidst the war, a neglected military order of misfits, the Night's Watch, is all that stands between the realms of men and icy horrors beyond.",
    "popularity": 246.1416,
    "poster_path": "/1XS1oqL89opfnbLl8WnZY1O1uJx.jpg",
    "production_companies": [
        {
            "id": 3268,
            "logo_path": "/tuomPhY2UtuPTqqFnKMVHvSb724.png",
            "name": "HBO",
            "origin_country": "US",
        },
    ],
    "production_countries": [
        {"iso_3166_1": "GB", "name": "United Kingdom"},
    ],
    "seasons": [
        {
            "air_date": "2010-12-05",
            "episode_count": 300,
            "id": 3627,
            "name": "Specials",
            "overview": "",
            "poster_path": "/aos6lC1JGYt6ZRL85lgstNsfSeY.jpg",
            "season_number": 0,
            "vote_average": 0.0,
        },
        {
            "air_date": "2011-04-17",
            "episode_count": 10,
            "id": 3624,
            "name": "Season 1",
            "overview": "Trouble is brewing in the Seven Kingdoms of Westeros. For the driven inhabitants of this visionary world, control of Westeros' Iron Throne holds the lure of great power. But in a land where the seasons can last a lifetime, winter is coming...and beyond the Great Wall that protects them, an ancient evil has returned. In Season One, the story centers on three primary areas: the Stark and the Lannister families, whose designs on controlling the throne threaten a tenuous peace; the dragon princess Daenerys, heir to the former dynasty, who waits just over the Narrow Sea with her malevolent brother Viserys; and the Great Wall--a massive barrier of ice where a forgotten danger is stirring.",
            "poster_path": "/wgfKiqzuMrFIkU1M68DDDY8kGC1.jpg",
            "season_number": 1,
            "vote_average": 8.4,
        },
    ],
    "softcore": False,
    "spoken_languages": [
        {"english_name": "English", "iso_639_1": "en", "name": "English"}
    ],
    "status": "Ended",
    "tagline": "Winter is coming.",
    "type": "Scripted",
    "vote_average": 8.474,
    "vote_count": 27973,
}
```
