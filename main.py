import subprocess
from functools import reduce


def extract_raw_timecode(chunk):
    return chunk[chunk.index(b'time='):chunk.index(b' bitrate')]


def to_seconds(timecode):
    x = 60

    def func(y):
        nonlocal x
        y *= x
        x *= 60
        return y

    l = list(reversed(list(map(float, timecode[timecode.index(b'=') + 1:].split(b':')))))
    return reduce(lambda a, b: func(b) + a, l)


# Function to execute once new progress log is found
def on_new_log(new_progress, target_file_length):
    timecode = extract_raw_timecode(new_progress)
    seconds = to_seconds(timecode)
    print((str(seconds / target_file_length * 100))[:5] + '%')


def skip_prefix(p):
    prefix = b''
    while True:
        tmp_output = p.stderr.read(100)
        prefix += tmp_output
        if b'size=' in prefix:
            return prefix[prefix.index(b'size='):]


def contains_new_progress(_bytes):
    return _bytes.count(b'size=') > 1


def extract_progress(_bytes):
    return _bytes[_bytes.index(b'size='):_bytes.index(b'size=', _bytes.index(b'size=') + 1)], \
           _bytes[_bytes.index(b'size=', _bytes.index(b'size=') + 1):]


def extract_last_progress(_bytes):
    return _bytes[_bytes.index(b'size='):]


def get_progress_log(p, _bytes, on_new_progress_callback):
    result = []
    while True:
        tmp_output = p.stderr.read(10)
        if not tmp_output:
            break
        _bytes += tmp_output
        if contains_new_progress(_bytes):
            last_progress, _bytes = extract_progress(_bytes)
            result.append(last_progress)
            on_new_progress_callback(last_progress)
    last_progress = extract_last_progress(_bytes)
    result.append(last_progress)
    on_new_progress_callback(last_progress)
    return result


def get_duration(file_path):
    from moviepy.editor import VideoFileClip
    clip = VideoFileClip(file_path)
    return clip.duration


target_file = 'target.mp4'

# Get file duration to compute progress percentage
target_file_duration = get_duration(target_file)

# Command to run
command = ['ffmpeg', '-i', target_file, '-y', 'result.avi']
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

# Skip all the output before the progress log
leftover = skip_prefix(p)

# Read progress log
progress_log = get_progress_log(p, leftover, lambda x: on_new_log(x, target_file_duration))

p.stdout.close()
p.wait()

