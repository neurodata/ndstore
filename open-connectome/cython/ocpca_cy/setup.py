from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy

ext_modules = [Extension("ocpca_cy", ["ocpca_cy.pyx"],include_dirs=[numpy.get_include()])]
# You can add directives for each extension too
# by attaching the `pyrex_directives`
for e in ext_modules:
    e.pyrex_directives = {"boundscheck": False}
setup(
    name = "cython accelerator for processing voxels lists",
    cmdclass = {"build_ext": build_ext},
    ext_modules = ext_modules
)
