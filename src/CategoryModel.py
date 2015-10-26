import untangle
import os

class CategoryModel:
    def __init__(self):
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        print "initializing a catgory model"
