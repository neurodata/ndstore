from collections import defaultdict

"""Classes that hold annotation metadata """

class Annotation:
  """Metdata common to all annotations."""

  annid = 0
  status = 0
  confidence = 0.0
  kvpairs = defaultdict(list)

class AnnSynapse (Annotation):
  """Metadata specific to synapses"""

  weight = 0.0
  type = 0
  seeds = []
  segments = []
  
class AnnSeed (Annotation):
  """Metadata specific to seeds"""

  parent=0      # parent seed
  position=[0,0,0] 
  cubelocation=0  # some enumeration
  source=0      # source annotation
