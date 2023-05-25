#!/usr/bin/env python

#Convert Python colormaps to NiiVue JSON
# https://matplotlib.org/stable/gallery/color/colormap_reference.html
# PiYG color map

import codecs, json, os
from _cm import datad

for name, spec in datad.items():
    pylut = datad[name]
    if (type(pylut) is not tuple):
        print('Skipping ' + name)
        continue
    nNode = len(pylut)
    if (type(pylut[0][1]) is tuple):
        print('Skipping ' + name)
        continue
    print(' Converting {} with {} nodes'.format(name, nNode))
    js = {'R': [], 'G': [], 'B': [], 'A': [], 'I': []}
    for i in range(nNode):
        js['R'].append(int(255 * pylut[i][0]))
        js['G'].append(int(255 * pylut[i][1]))
        js['B'].append(int(255 * pylut[i][2]))
        idx = int(i/(nNode-1) * 255)
        js['A'].append(int(0.3 * idx))
        js['I'].append(idx)
    fnm = '.' + os.path.sep + 'lut' + os.path.sep + name + '.json'
    with codecs.open(fnm, 'w', 'utf8') as f:
         f.write(json.dumps(js, sort_keys = False, ensure_ascii=False))
