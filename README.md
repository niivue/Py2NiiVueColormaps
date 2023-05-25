# Py2NiiVueColormaps


NiiVue comes with many built-in colormaps, which you can explore in this [live demo](https://niivue.github.io/niivue/features/colormaps.html). 

The live demo `custom` button also shows how you can define new colormaps:
```JavaScript
let cmap = {
  R: [0, 255, 22, 127],
  G: [0, 20, 192, 187],
  B: [0, 152, 80, 255],
  A: [0, 255, 255, 255],
  I: [0, 22, 222, 255],
};
let key = "Custom";
nv1.addColormap(key, cmap);
nv1.volumes[0].colormap = key;
```

However, matplotlib provides many [of its own colormaps](https://matplotlib.org/stable/gallery/color/colormap_reference.html). The purpose of this repository is to convert **many** of the [matplotlib _cm.py](https://github.com/matplotlib/matplotlib/blob/28a0205a52ae54c4fbf2f94cfeea40d96be709ac/lib/matplotlib/_cm.py#L4) colormaps to NiiVue's JSON format. To re-build the colormaps in the `lut` folder you can run:

```bash
git clone https://github.com/niivue/Py2NiiVueColormaps
cd Py2NiiVueColormaps
python lut2niivue.py
```

Note that _cm.py uses several different methods to colormaps, and this repository only currently converts some of these (it generates a report of the converted and skipped colormaps).

Note that the file _cm.py is from matplotlib and retains that permissive license.