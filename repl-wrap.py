#!/usr/bin/env python3
import argparse
import os
import pty
import select
import sys

def noecho(fd):
  import termios
  new = termios.tcgetattr(fd)
  new[3] = new[3] & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSADRAIN, new)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='wrap a repl command')
  parser.add_argument('-f', dest='fifo', type=str)
  parser.add_argument('-c', dest='cmd', nargs=argparse.REMAINDER)
  args = parser.parse_args()

  if args.fifo is None or args.cmd is None:
    raise Exception('both -f and -c arguments are required')

  (pid, replfd) = pty.fork()
  if pid == 0:
    os.execv(args.cmd[0], args.cmd)
    os.exit(1)

  noecho(replfd)

  done = False
  while not done:
    (rd, wr, ex) = select.select([replfd, 0], [], [])

    for f in rd:
      # data from the repl, send it to stdout
      if f is replfd:
        try:
          data = os.read(replfd, 1024)
          if not data:
            done = True
        except OSError:
          done = True
          data = b''
        os.write(1, data)

      # data from stdin, send it to the repl
      if f == 0:
        data = os.read(0, 1024)
        if not data:
          done = True
        os.write(replfd, data)
