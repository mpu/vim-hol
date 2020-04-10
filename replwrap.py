#!/usr/bin/env python3
import argparse
import fcntl
import os
import pty
import select
import signal
import sys
import termios
import tty
from filter import filters

def copysize(ifd, rfd):
  s = fcntl.ioctl(ifd, termios.TIOCGWINSZ, b'\x00' * 8)
  fcntl.ioctl(rfd, termios.TIOCSWINSZ, s)

def main():
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
  fifofd = os.open(args.fifo, os.O_RDWR|os.O_NONBLOCK)

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
  fifofilter = filters[args.filter]()

  tty.setraw(0)
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

if __name__ == "__main__":
  ttyattr = termios.tcgetattr(0)
  try:
    main()
  finally:
    termios.tcsetattr(0, termios.TCSANOW, ttyattr)
