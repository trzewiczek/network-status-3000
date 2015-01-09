import csv
import os
import urllib2

from datetime import datetime as dt

FPS                 = 3
LINE_HEIGHT         = 20
ROW_HEIGHT          = 25
CANVAS_WIDTH        = 1200             # once every 3 seconds → 1200 points an hour
CANVAS_HEIGHT       = 24 * ROW_HEIGHT  # one row for each of 24 hours a day
MARGIN_LEFT         = 50
MARGIN_TOP          = 75
MARGIN_RIGHT_BOTTOM = 25
PICTURE_WIDTH       = CANVAS_WIDTH  + MARGIN_LEFT + MARGIN_RIGHT_BOTTOM
PICTURE_HEIGHT      = CANVAS_HEIGHT + MARGIN_TOP  + MARGIN_RIGHT_BOTTOM

current_date = dt.now().strftime('%Y-%m-%d')


def draw_title(current_date):
  # title
  with pushMatrix():
    translate(PICTURE_WIDTH / 2, 30)

    with pushStyle():
      fill('#999999')
      textSize(16)
      textAlign(CENTER)
      text(current_date, 0, 0)


def draw_grids_and_labels():
  # grid line should stand 5px outside canvas on each side
  outstanding      = 5
  grid_line_height = CANVAS_HEIGHT + (2 * outstanding)

  # with pushStyle doesn't work for text size
  textSize(12)
  
  # vertical grid minutes labels
  ticks = ['%02d' % i for i in range(0, 61, 5)]
  with pushMatrix():
    translate(0, -outstanding)

    for t in ticks:
      x = int(t) * 20
      with pushStyle():
        stroke('#ddddee')
        line(x, 0, x, grid_line_height)

      with pushStyle():
        fill('#999999')
        textAlign(CENTER)
        text(t, x, -outstanding)


  # horizontal grid hours labels
  with pushMatrix():
    translate(-10, 0)

    for h in range(0, 24):
      translate(0, ROW_HEIGHT)

      with pushStyle():
        fill('#999999')
        textAlign(RIGHT)
        text('%02d' % h, 0, -10)


def update_graph_with(connection_status, timestamp):
  h = timestamp.hour
  m = timestamp.minute
  s = timestamp.second

  x = ((m * 60) + s) / FPS
  y = h * ROW_HEIGHT

  with pushStyle():
    stroke('#f6f6ff' if connection_status else '#ff6000')

    with pushMatrix():
      translate(x, y)

      line(0, 0, 0, LINE_HEIGHT)


def log(connection_status, timestamp):
  print "%s %s" % ('>>>' if connection_status else '!!!', timestamp)

  # storing in csv files due to no sqlite3 module in pyprocessing
  # TODO reimplement it with jdbc sqlite interface
  with open('%s.csv' % current_date, 'a') as f:
    f.write('%s,%d\n' % (timestamp, int(connection_status)))


# Processing code starts here
def setup():
  size(PICTURE_WIDTH, PICTURE_HEIGHT)
  frameRate(1.0 / FPS)


  background(255)
  draw_title(current_date)

  translate(MARGIN_LEFT, MARGIN_TOP)
  draw_grids_and_labels()

  # TODO reimplement it with jdbc sqlite interface
  try:
    with open('%s.csv' % current_date, 'r') as f:
      for row in csv.reader(f):
        # [:-7] emoji stands for "Python can't parse milliseconds"
        timestamp = dt.strptime(row[0][:-7], '%Y-%m-%d %H:%M:%S')
        status    = bool(int(row[1]))

        update_graph_with(status, timestamp)

  except IOError:
    print "No data for %s yet" % current_date


def draw():
  global current_date

  translate(MARGIN_LEFT, MARGIN_TOP)

  timestamp = dt.now()
  today = timestamp.strftime('%Y-%m-%d')

  # save the graph and start a new one
  if current_date != today:
    save("{}.png".format(current_date))

    current_date = today
    background(255)
    # an ugly way of keeping global canvas offset that doesn't apply to title
    with pushMatrix():
      translate(MARGIN_LEFT, MARGIN_TOP)
      draw_title(current_date)

    draw_grids_and_labels(current_date)

  # test connection
  try:
    # TODO make it more... well... nerdish... with sockets etc.
    urllib2.urlopen('http://173.194.32.255', timeout=2)
    connection_status = True

  except urllib2.URLError:
    connection_status = False

  update_graph_with(connection_status, timestamp)
  log(connection_status, timestamp)
