import os
import signal

class Copy:
  def __init__(self, child):
    pass

  def filter(self, data):
    return data

class LineFilter:
  def __init__(self, child):
    self.child = child
    self.buf = bytearray()

  def filter(self, data):
    self.buf += data
    lines = self.buf.split(b'\n')
    self.buf = lines[-1]
    return b''.join(filter(None, [self.line(l) for l in lines[:-1]]))

def tactrim(tac):
  """
  strip extra HOL tacticals at the beginning
  and end of a tactic
  """
  tacticals = [
    b'THEN', b'THENL', b'THEN1',
    b'\\', b'>>', b'>-',
    b',', b' ', b'\n',
  ]
  tac = bytearray(tac)
  nop = tac.count(b'(')
  ncp = tac.count(b')')
  while True:
    ltac = len(tac)
    for t in tacticals:
      if tac.startswith(t):
        tac[:len(t)] = []
      if tac.endswith(t):
        tac[-len(t):] = []
    if nop > ncp and tac.startswith(b'('):
      tac[:1] = []
      nop -= 1
    if ncp > nop and tac.endswith(b')'):
      tac[-1:] = []
      ncp -= 1
    if len(tac) == ltac:
      return tac

class HolLight(LineFilter):
  def cancel(self, arg):
    os.kill(self.child, signal.SIGINT)

  def tactic(self, arg):
    return b'e (%s);;\n' % tactrim(arg)

  def send(self, arg):
    return arg + b';;\n'

  def line(self, l):
    cmds = {
      ord('c'): self.cancel,
      ord('s'): self.send,
      ord('e'): self.tactic,
      ord('g'): lambda _: b'g ();;\n',
      ord('b'): lambda _: b'b ();;\n',
      ord('p'): lambda _: b'p ();;\n',
    }
    try:
      return cmds[l[0]](l[1:])
    except KeyError:
      return None

filters = {'copy': Copy, 'hollight': HolLight}
