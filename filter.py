class Copy():
  def filter(self, data):
    return data

class LineFilter():
  def __init__(self):
    self.buf = bytearray()

  def filter(self, data):
    self.buf += data
    lines = self.buf.split(b'\n')
    self.buf = lines[-1]
    return b''.join([self.line(l) for l in lines[:-1]])

class HolLight(LineFilter):
  def line(self, l):
    return b'HOL! ' + l + b'\n'

filters = {'copy': Copy, 'hollight': HolLight}
