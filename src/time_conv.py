from .constants import *

def time_conv(time: int) -> str:
    assert isinstance(time, int)
    time = max(0, time)
    (time, frames) = divmod(time, FRAME_RATE_HZ)
    hundredths = (frames * 100) // FRAME_RATE_HZ
    (minutes, seconds) = divmod(time, 60)
    return f"{minutes:d}'{seconds:02d}\"{hundredths:02d}"
