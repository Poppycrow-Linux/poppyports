# logging utils and benchmarks
import os
import time
from enum import Enum

# exceptions
class InvalidRecipeError(Exception):
  pass
class InvalidChecksumError(Exception):
  pass

# TODO: here move log() and Colors and such

# ANSI colors and printing
class Colors:
  ERROR = "\x1b[5;97;101m"
  WARNING = "\x1b[5;30;103m"
  SUCCESS = "\x1b[0;97;48;5;28m"
  SH_COMMAND = "\x1b[0;97;48;5;21m"
  END = "\x1b[0m"

important_colors = [Colors.SUCCESS, Colors.ERROR, Colors.WARNING]

# THIS IS TEMPORARY someone PLEASE find a way to make colorless and cleaner logs work without reading the config and args 9 billion times
def log(clr, *args):
    print(f"{clr if (clr is not None) else ''}I:", *args, Colors.END)

# not used due to config parameter complications
def log_new(clr, supressnonerrorlogs, color, *args):
  if (supressnonerrorlogs and (clr in important_colors)) or not (supressnonerrorlogs):
    print(f"{clr if (clr is not None and color) else ''}I:", *args, Colors.END)

def human_fsize(path):
  size = os.path.getsize(path)
  for unit in ["B", "KB", "MB", "GB"]:
    if size < 1024 or unit == "GB":
      return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
    size /= 1024

def human_time(ms):
  # https://docs.python.org/2/library/string.html#format-specification-mini-language
  if ms > 60000: return f"{ms/60000:.5g} min"
  if ms > 1000:  return f"{ms/1000:.5g} s"
  return f"{ms:.5g} ms"


class State(Enum):
  IDLE     = "Idle"
  DOWNLOAD = "Download"
  CHECKSUM = "Checksum"
  EXTRACT  = "Extract"
  BUILD    = "Build"
  INSTALL  = "Install"
  DONE     = "Done"

def ctime():
  return time.time() * 1000

class StateBenchmark:
  def __init__(self):
    now = ctime()
    self.started_at = now
    self.state_started_at = now
    self.state = State.IDLE
    self.elapsed = {}  # map[state, ms]

  def total(self):
    return ctime() - self.started_at

  def current(self):
    return ctime() - self.state_started_at

  def change(self, state: str):
    now = ctime()
    self.elapsed[self.state] = now - self.state_started_at
    self.state = state
    self.state_started_at = now

  def build_breakdown(self) -> str:
    res = []
    for state, duration in self.elapsed.items():
      res.append(f"{state.value}: {human_time(duration)}")
    return "\n".join(res)
