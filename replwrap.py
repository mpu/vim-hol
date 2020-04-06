#!/usr/bin/env python3
import argparse
import fcntl
import os
import pty
import select
import signal
import sys
import termios
from filter import filters

def resettty(fd, attr=None):
  old = termios.tcgetattr(fd)
  if attr is None:
    attr = old[:]
    attr[3] = attr[3] & ~termios.ICANON
    attr[3] = attr[3] & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSANOW, attr)
  return old

def copysize(ifd, rfd):
  s = fcntl.ioctl(ifd, termios.TIOCGWINSZ, b'\x00' * 8)
  fcntl.ioctl(rfd, termios.TIOCSWINSZ, s)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="""Runs a command as if it were running directly in
                   the terminal, but provides a fifo for
                   remote-control.""")
  parser.add_argument('-F', dest='filter', default='copy',
    help=('fifo filter (%s)' % ', '.join(filters.keys())))
  parser.add_argument('-f', dest='fifo', default='/tmp/replfifo')
  parser.add_argument(
    '-c', dest='cmd', nargs=argparse.REMAINDER, required=True,
    help='command to run')
  args = parser.parse_args()

  try:
    os.mkfifo(args.fifo)
  except FileExistsError:
    pass
  fifofd = os.open(args.fifo, os.O_RDONLY|os.O_NONBLOCK)

  (pid, replfd) = pty.fork()
  if pid == 0:
    try:
      os.execvp(args.cmd[0], args.cmd)
      err = 'execv returned'
    except OSError as e:
      err = str(e)
    parser.error('could not run command: ' + err)

  if args.filter not in filters:
    parser.error('invalid filter: %s' % args.filter)
  fifofilter = filters[args.filter](pid)

  oldattr = resettty(0)
  copysize(1, replfd)
  signal.signal(signal.SIGWINCH, lambda sig, stk: copysize(1, replfd))

  done = False
  while not done:
    rd = select.select([replfd, fifofd, 0], [], [])[0]

    for f in rd:
      # data from the repl, send it to stdout
      if f is replfd:
        try:
          data = os.read(replfd, 1024)
        except OSError:
          data = b''
        if not data:
          done = True
        os.write(1, data)

      # data from the fifo, send it to the repl
      if f is fifofd:
        data = os.read(fifofd, 1024)
        os.write(replfd, fifofilter.filter(data))

      # data from stdin, send it to the repl
      if f == 0:
        data = os.read(0, 1024)
        if not data:
          done = True
        os.write(replfd, data)

  resettty(0, oldattr)
