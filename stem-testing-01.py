import curses
import functools

from stem.control import EventType, Controller
from stem.util import str_tools

COLOR_LIST = {
  "red": curses.COLOR_RED,
  "green": curses.COLOR_GREEN,
  "yellow": curses.COLOR_YELLOW,
  "blue": curses.COLOR_BLUE,
  "cyan": curses.COLOR_CYAN,
  "magenta": curses.COLOR_MAGENTA,
  "black": curses.COLOR_BLACK,
  "white": curses.COLOR_WHITE,
}
GRAPH_WIDTH = 40
GRAPH_HEIGHT = 8

DOWNLOAD_COLOR = "green"
UPLOAD_COLOR = "blue"

def main():
  with Controller.from_port(port = 9051) as controller:
    controller.authenticate()

    try:

      curses.wrapper(draw_bandwidth_graph, controller)
    except KeyboardInterrupt:
      pass  

def draw_bandwidth_graph(stdscr, controller):
  window = Window(stdscr)



  bandwidth_rates = [(0, 0)] * GRAPH_WIDTH


  bw_event_handler = functools.partial(_handle_bandwidth_event, window, bandwidth_rates)



  controller.add_event_listener(bw_event_handler, EventType.BW)


  stdscr.getch()

def _handle_bandwidth_event(window, bandwidth_rates, event):


  bandwidth_rates.insert(0, (event.read, event.written))
  bandwidth_rates = bandwidth_rates[:GRAPH_WIDTH] 
  _render_graph(window, bandwidth_rates)

def _render_graph(window, bandwidth_rates):
  window.erase()

  download_rates = [entry[0] for entry in bandwidth_rates]
  upload_rates = [entry[1] for entry in bandwidth_rates]



  label = "Downloaded (%s/s):" % str_tools.size_label(download_rates[0], 1)
  window.addstr(0, 1, label, DOWNLOAD_COLOR, curses.A_BOLD)

  label = "Uploaded (%s/s):" % str_tools.size_label(upload_rates[0], 1)
  window.addstr(0, GRAPH_WIDTH + 7, label, UPLOAD_COLOR, curses.A_BOLD)


  max_download_rate = max(download_rates)
  max_upload_rate = max(upload_rates)

  window.addstr(1, 1, "%4i" % (max_download_rate / 1024), DOWNLOAD_COLOR)
  window.addstr(GRAPH_HEIGHT, 1, "   0", DOWNLOAD_COLOR)

  window.addstr(1, GRAPH_WIDTH + 7, "%4i" % (max_upload_rate / 1024), UPLOAD_COLOR)
  window.addstr(GRAPH_HEIGHT, GRAPH_WIDTH + 7, "   0", UPLOAD_COLOR)



  for col in range(GRAPH_WIDTH):
    col_height = GRAPH_HEIGHT * download_rates[col] / max(max_download_rate, 1)

    for row in range(col_height):
      window.addstr(GRAPH_HEIGHT - row, col + 6, " ", DOWNLOAD_COLOR, curses.A_STANDOUT)

    col_height = GRAPH_HEIGHT * upload_rates[col] / max(max_upload_rate, 1)

    for row in range(col_height):
      window.addstr(GRAPH_HEIGHT - row, col + GRAPH_WIDTH + 12, " ", UPLOAD_COLOR, curses.A_STANDOUT)

  window.refresh()

class Window(object):
  """
  Simple wrapper for the curses standard screen object.
  """

  def __init__(self, stdscr):
    self._stdscr = stdscr


    self._colors = dict([(color, 0) for color in COLOR_LIST])

    try:
      curses.use_default_colors()
    except curses.error:
      pass


    try:
      curses.curs_set(0)
    except curses.error:
      pass


    try:
      if curses.has_colors():
        color_pair = 1

        for name, foreground in COLOR_LIST.items():
          background = -1 
          curses.init_pair(color_pair, foreground, background)
          self._colors[name] = curses.color_pair(color_pair)
          color_pair += 1
    except curses.error:
      pass

  def addstr(self, y, x, msg, color = None, attr = curses.A_NORMAL):

    if color is not None:
      if color not in self._colors:
        recognized_colors = ", ".join(self._colors.keys())
        raise ValueError("The '%s' color isn't recognized: %s" % (color, recognized_colors))

      attr |= self._colors[color]

    max_y, max_x = self._stdscr.getmaxyx()

    if max_x > x and max_y > y:
      try:
        self._stdscr.addstr(y, x, msg[:max_x - x], attr)
      except:
        pass

  def erase(self):
    self._stdscr.erase()
  
  def refresh(self):
    self._stdscr.refresh()

if __name__ == '__main__':
  main()