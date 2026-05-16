import os
import signal
from pathlib import Path

from common.logger import log

RECORDING_ICON_PATH = Path("/tmp/recording_icon")
RECORDING_PID_PATH = Path("/tmp/recording_pid")


def stop_recording():
    recording_pid = None
    try:
        with RECORDING_PID_PATH.open() as f:
            content = f.read().strip()
        recording_pid = int(content)

        os.kill(recording_pid, signal.SIGTERM)

    except FileNotFoundError:
        return
    except ValueError:
        log.error(f"Invalid PID in file: {RECORDING_PID_PATH!r}")
    except ProcessLookupError:
        log.error(f"No such process: {recording_pid!r}")
    except PermissionError:
        log.error(f"Permissions denied for PID {recording_pid!r}.")
    finally:
        RECORDING_PID_PATH.unlink(missing_ok=True)
