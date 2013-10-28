# This disables py.test for this directory
import py

class DisableDirectory(py.test.collect.Directory):

    def buildname2items(self):
        return {}

Directory = DisableDirectory
