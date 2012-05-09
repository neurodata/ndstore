from collections import defaultdict

"""Classes that hold annotation metadata """

# Annotation types
ANNO_SYNAPSE = 1
ANNO_SEED = 2

class Annotation:
  """Metdata common to all annotations."""

  annid = 0 
  status = 0 
  confidence = 0.0 
  kvpairs = defaultdict(list)

class AnnSynapse (Annotation):
  """Metadata specific to synapses"""

  weight = 0.0 
  synapse_type = 0 
  seeds = []
  segments = []
  
class AnnSeed (Annotation):
  """Metadata specific to seeds"""

  parent=0        # parent seed
  position=[]
  cubelocation=0  # some enumeration
  source=0        # source annotation
