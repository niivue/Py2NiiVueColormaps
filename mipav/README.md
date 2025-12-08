# MIPAV colormaps

This folder contains the original MIPAV colormaps (in the txt/ directory) along with their NiiVue-compatible conversions (in json/). It also includes a script for converting colormaps from the MIPAV format to the NiiVue format. The script extends the [mipav-to-niivue](https://github.com/chhsiao1981/mipav-to-niivue) created by Chuan-Heng Hsiao.

MIPAV colormaps explicitly define the red, green, and blue values for all 256 entries in a palette. NiiVue, by contrast, represents colormaps using a set of irregularly spaced control points and linearly interpolates colors between them. Because of this difference, the conversion script lets you control the precision of the conversion: higher precision typically produces more control points and closer matches to the original MIPAV palette.

By default, the converter ensures that every color channel (0–255 range) is reproduced with an error of no more than 2. The script also normalizes colormap names by replacing spaces with underscores.

## Usage

The script takes two required arguments and one optional argument:

 - Source folder containing the MIPAV .txt colormaps
 - Output folder where NiiVue .json colormaps will be written
 - Precision (optional; defaults to 2)

Example:

```sh
python txt2lut.py ./txt ./json 2

```