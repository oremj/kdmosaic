import Image
from collections import defaultdict
import sys
import kdtree
import os
import os.path
import cPickle
from datetime import datetime
import operator
import random

DIR='favicons_sample'
KDTREE_PICKLE='kdtree.dat'

class ImageOps:

    favicon_path = os.path.join(os.path.dirname(__file__),DIR)

    def __init__(self, images):
        self.ims = [ Image.open(image).convert('RGB') for image in images ]
        self.load_favicons()
    
    def yuv(self, rgb):
        r,g,b = [ int(i) for i in rgb ]
        return r,g,b
        y = int((0.257 * r) + (0.504 * g) + (0.098 * b) + 16)
        v = int((0.439 * r) - (0.368 * g) - (0.071 * b) + 128)
        u = int(-(0.148 * r) - (0.291 * g) + (0.439 * b) + 128)

    def load_favicons(self):
        try:
          self.favicons = cPickle.load(open(KDTREE_PICKLE))
        except IOError:
          self.favicons = []
          for file in os.listdir(self.favicon_path):
              try:
                r,g,b = Image.open('%s/%s' % (DIR,file)).resize((1,1), Image.ANTIALIAS).convert('RGB').load()[0,0]
                self.favicons.append(kdtree.P(file, self.yuv((r,g,b))))
              except IOError:
                print 'skipping', file
                continue
          self.favicons = kdtree.kdtree(self.favicons)
          cPickle.dump(self.favicons, open(KDTREE_PICKLE, 'w+'))

    img_cache = {}
    def mosaic(self, tile_size = 16):
        ts = []
        for im in self.ims:
            t0 = datetime.now()
            width, height = im.size
            new_im = Image.new(im.mode, (height * tile_size, width * tile_size))
            p_data = im.load()

            all_points = [ (x, y) for x in range(width) for y in range(height) ]
            random.shuffle(all_points)
            for p in all_points: 
                key = p_data[p]
                node = kdtree.nearestn(self.yuv(key), self.favicons)[0]
                nn = node.location.data 
                kdtree.removenode(node)
                try:
                    img = self.img_cache[nn]
                except KeyError:
                    img = Image.open('%s/%s' % (DIR,nn))
                    self.img_cache[nn] = img

                new_im.paste(img, (p[0] * tile_size, p[1] * tile_size))

            t = datetime.now()-t0
            ts.append(t)
            print t, reduce(operator.add,ts)/len(ts)

        if len(self.ims) == 1:
           new_im.show()
                

    def pixelate(self,box_size=10):
        color_avgs = defaultdict(list)
        new_im = Image.new(self.im.mode, self.im.size)

        width, height = self.im.size
        p_data = self.im.load()
        new_p_data = new_im.load()


        for x in xrange(0,width):
            column = x / box_size
            for y in xrange(0,height):
                row = y / box_size
                color_avgs[(row,column)].append(p_data[x,y])

        for k,v in color_avgs.iteritems():
            l = len(v)
            r = sum(i[0] for i in v) / l
            g = sum(i[1] for i in v) / l
            b = sum(i[2] for i in v) / l
            color_avgs[k] = (r,g,b) 

        for x in xrange(0,width):
            column = x / box_size
            for y in xrange(0,height):
                row = y / box_size
                new_p_data[x,y] = color_avgs[row,column]
        new_im.show()


if __name__ == '__main__':
    image = ImageOps(sys.argv[1:])
    image.mosaic()
