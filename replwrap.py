#!/usr/bin/env python3
import argparse
import os
import pty
import select
import sys
import termios

def resettty(fd, attr=None):
  old = termios.tcgetattr(fd)
  if attr is None:
    attr = old[:]
    attr[3] = attr[3] & ~termios.ICANON
    attr[3] = attr[3] & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSADRAIN, attr)
  return old

def copysize(ifd, rfd):
  import fcntl
  import struct
  s = fcntl.ioctl(ifd, termios.TIOCGWINSZ, b'\x00' * 8)
  (rows, cols) = struct.unpack('HHHH', s)[:2]
  s = struct.pack('HHHH', rows, cols, 0, 0)
  fcntl.ioctl(rfd, termios.TIOCSWINSZ, s)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='wrap a repl command')
  parser.add_argument('-f', dest='fifo', type=str)
  parser.add_argument('-c', dest='cmd', nargs=argparse.REMAINDER)
  args = parser.parse_args()

  if args.fifo is None or args.cmd is None:
    raise Exception('both -f and -c arguments are required')

  try:
    os.mkfifo(args.fifo)
  except FileExistsError:
    pass
  fifofd = os.open(args.fifo, os.O_RDONLY | os.O_NONBLOCK)

  (pid, replfd) = pty.fork()
  if pid == 0:
    os.execv(args.cmd[0], args.cmd)
    os.exit(1)

  old = resettty(0)
  copysize(1, replfd)

  done = False
  while not done:
    rd = select.select([replfd, fifofd, 0], [], [])[0]

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

      # data from the fifo, send it to the repl
      if f is fifofd:
        data = os.read(fifofd, 1024)
        os.write(replfd, data)

      # data from stdin, send it to the repl
      if f == 0:
        data = os.read(0, 1024)
        if not data:
          done = True
        os.write(replfd, data)

  resettty(0, old)
