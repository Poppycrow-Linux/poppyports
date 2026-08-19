# logging utils and benchmarks
import os
import time
from enum import Enum

# TODO: here move log() and Colors and such


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

class StateBenchmark:
  def __init__(self):
    now = time.time()
    self.started_at = now
    self.state_started_at = now
    self.state = State.IDLE
    self.elapsed = {}  # map[state, ms]

  def total(self):
    return time.time() - self.started_at

  def current(self):
    return time.time() - self.state_started_at

  def change(self, state: str):
    now = time.time()
    self.elapsed[self.state] = now - self.state_started_at
    self.state = state
    self.state_started_at = now

  def build_breakdown(self) -> str:
    res = []
    for state, duration in self.elapsed.items():
      res.append(f"{state.value}: {human_time(duration)}")
    return "\n".join(res)
