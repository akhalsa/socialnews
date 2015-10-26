import untangle
import os

class CategoryModel:
    def __init__(self):
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        print obj.root.category
        for cat in obj.root.category.category.category:
            print cat['name']
        print "initializing a catgory model"
