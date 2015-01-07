import csv
import os
import urllib2

from datetime import datetime as dt

FPS            = 3
LINE_HEIGHT    = 20
ROW_HEIGHT     = 25
CANVAS_WIDTH   = 1200             # once every 3 seconds → 1200 points an hour
CANVAS_HEIGHT  = 24 * ROW_HEIGHT  # one row for each of 24 hours a day
MARGIN         = 25
PICTURE_WIDTH  = CANVAS_WIDTH  + (2 * MARGIN)
PICTURE_HEIGHT = CANVAS_HEIGHT + (2 * MARGIN)

current_date = dt.now().strftime('%Y-%m-%d')


def draw_grids_and_labels():
  # draw 5-minutes grid
  outstanding      = 5
  grid_line_height = CANVAS_HEIGHT + (2 * outstanding)

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

  # TODO uncomment and make it work
  # pushMatrix()
  # translate(10, top_margin)
  #
  # # current_h = None
  #
  #
  # # draw hour label
  # if h != current_h:
  #   current_h = h
  #   with pushStyle():
  #     fill('#999999')
  #     text(h, 0, y + 14)
  #
  #
  # popMatrix()
  #
  # # draw top date label and legend
  # with pushMatrix():
  #   translate(0, 20)
  #
  #   center = width / 2
  #   with pushStyle():
  #     textAlign(CENTER)
  #     fill('#333333')
  #     text(today, center, 0)
  #
  #   with pushStyle():
  #     textAlign(LEFT)
  #     fill('#999999')
  #     text('Connection:', center + 360, 0)
  #
  #   with pushStyle():
  #     noStroke()
  #     fill('#ddddee')
  #     rect(center + 440, -12, 2, 18)
  #     text('success', center + 445, 0)
  #
  #   with pushStyle():
  #     noStroke()
  #     fill('#ff6000')
  #     rect(center + 505, -12, 2, 18)
  #     text('failed', center + 510, 0)
  #
  #


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
  with pushMatrix():
    translate(MARGIN, MARGIN)
    draw_grids_and_labels()

  # TODO reimplement it with jdbc sqlite interface
  try:
    with open('%s.csv' % current_date, 'r') as f:
      for row in csv.reader(f):
        # [:-7] emoji stands for "Python can't parse milliseconds"
        timestamp = dt.strptime(row[0][:-7], '%Y-%m-%d %H:%M:%S')
        status    = bool(int(row[1]))

        with pushMatrix():
          translate(MARGIN, MARGIN)
          update_graph_with(status, timestamp)

  except IOError:
    print "No data for %s yet" % current_date


def draw():
  global current_date

  timestamp = dt.now()
  today = timestamp.strftime('%Y-%m-%d')

  # save the graph and start a new one
  if current_date != today:
    save("{}.png".format(current_date))

    current_date = today
    background(255)
    with pushMatrix():
      translate(MARGIN, MARGIN)
      draw_grids_and_labels()

  # test connection
  try:
    # TODO make it more... well... nerdish... with sockets etc.
    urllib2.urlopen('http://173.194.32.255', timeout=2)
    connection_status = True

  except urllib2.URLError:
    connection_status = False

  with pushMatrix():
    translate(MARGIN, MARGIN)
    update_graph_with(connection_status, timestamp)

  log(connection_status, timestamp)
