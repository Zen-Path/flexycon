## Stats

```json
{
    "level": "notice",
    "msg": "\nTransferred:   \t   32.292 MiB / 32.292 MiB, 100%, 0 B/s, ETA -\nChecks:                 0 / 0, -, Listed 6\nTransferred:            5 / 5, 100%\nElapsed time:         0.2s\n\n",
    "source": "slog/logger.go:256",
    "stats": {
        "bytes": 33860977,
        "checks": 0,
        "deletedDirs": 0,
        "deletes": 0,
        "elapsedTime": 0.232429917,
        "errors": 0,
        "eta": null,
        "fatalError": false,
        "listed": 6,
        "renames": 0,
        "retryError": false,
        "serverSideCopies": 0,
        "serverSideCopyBytes": 0,
        "serverSideMoveBytes": 0,
        "serverSideMoves": 0,
        "speed": 0,
        "totalBytes": 33860977,
        "totalChecks": 0,
        "totalTransfers": 5,
        "transferTime": 0.006062667,
        "transfers": 5
    },
    "time": "2025-10-18T09:39:22.137804+03:00"
}
```

## File Ops

Notice the "size" field.

```json
{
    "level": "notice",
    "msg": "Skipped copy as --dry-run is set (size 1016.511Ki)",
    "object": "this-is-a-file.txt",
    "objectType": "*local.Object",
    "size": 1040907,
    "skipped": "copy",
    "source": "slog/logger.go:256",
    "time": "2025-10-18T09:39:22.133936+03:00"
}
```

## Directory Ops

```json
{
    "level": "notice",
    "msg": "Skipped make directory as --dry-run is set",
    "object": "this-is-a-new-directory",
    "objectType": "string",
    "skipped": "make directory",
    "source": "slog/logger.go:256",
    "time": "2025-10-18T11:28:40.112558+03:00"
}
```
