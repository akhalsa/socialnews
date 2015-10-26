import untangle
import os

class CategoryModel:
    def __init__(self):
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        
        for cat in obj.root.category.category.category:
            print cat['name']
            for h in cat.handle:
                print h.cdata

        print "initializing a catgory model"
