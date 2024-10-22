import os
import signal

class Copy:
  def filter(self, data):
    return data

class LineFilter:
  def __init__(self):
    self.buf = bytearray()

  def filter(self, data):
    self.buf += data
    lines = self.buf.split(b'\n')
    self.buf = lines[-1]
    return b''.join(filter(None, [self.line(l) for l in lines[:-1]]))

def holtrim(tac, tacticals=[]):
  """
  strip extra HOL tacticals at the beginning
  and end of a tactic
  """
  tacticals += [b';', b',', b' ', b'\n']
  tac = bytearray(tac)
  delims = {
    b'()': tac.count(b'(') - tac.count(b')'),
    b'[]': tac.count(b'[') - tac.count(b']'),
  }
  while True:
    ltac = len(tac)
    for t in tacticals:
      if tac.startswith(t):
        tac[:len(t)] = []
      if tac.endswith(t):
        tac[-len(t):] = []
    for dp, nd in delims.items():
      if nd > 0 and tac.startswith(dp[:1]):
        tac[:1] = []
        delims[dp] -= 1
      if nd < 0 and tac.endswith(dp[1:]):
        tac[-1:] = []
        delims[dp] += 1
    if len(tac) == ltac:
      return tac

def slurp(path):
  try:
    f = open(bytes(path), 'rb')
  except IOError:
    return None
  else:
    with f:
      return f.read()

class HolLight(LineFilter):
  tacticals = [b'THEN', b'THENL']

  def tactic(self, arg):
    data = slurp(arg)
    if data is not None:
      return b'e (%s);;\n' % holtrim(data, self.tacticals)

  def goal(self, arg):
    data = slurp(arg)
    if data is not None:
      return b'g %s;;\n' % holtrim(data)

  def send(self, arg):
    return b'#use "%s";;\n' % arg

  def line(self, l):
    cmds = {
      ord('S'): self.send,
      ord('E'): self.tactic,
      ord('G'): self.goal,
      ord('c'): lambda _: b'\x03',
      ord('b'): lambda _: b'b ();;\n',
      ord('p'): lambda _: b'p ();;\n',
      ord('r'): lambda _: b'r 1;;\n',
      ord('h'): lambda x: b'help "%s";;\n' % x,
    }
    try:
      return cmds[l[0]](l[1:])
    except KeyError:
      return None

filters = {'copy': Copy, 'hol': HolLight}
