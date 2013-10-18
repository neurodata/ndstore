#
# OCPCA errors
#
class OCPCAError (Exception):
  """General annotation error"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

