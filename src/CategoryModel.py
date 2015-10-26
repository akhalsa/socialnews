import untangle
import os

class CategoryModel:
    def __init__(self):
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        print obj.root.category['name']
        print "initializing a catgory model"
