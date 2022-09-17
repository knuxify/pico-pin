#!/usr/bin/python
import sys
import os
import zlib

from PIL import Image, ImageSequence
from PIL import ImageDraw
from PIL import GifImagePlugin
GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_ALWAYS
import struct

class ConvImage:
    def __init__(self, filename):
        self.filename = filename
        self.img = Image.open(filename)
        self.is_animated = self.img.is_animated
        self.w = self.img.size[0]
        self.h = self.img.size[0]

    def convert(self, output_prefix='output'):
        if self.is_animated and self.img.n_frames > 1:
            self.convert_animated(output_prefix)
        else:
            self.convert_static(output_prefix)

    def convert_static(self, output_prefix='output', frame_override=0):
        pixels = self.img.load()

        with open(f'{output_prefix}_{frame_override}.bin', 'wb') as outfile:
            for y in range(self.h):
                for x in range(self.w):
                    if x < self.w:
                        r = pixels[x,y][0] >> 3
                        g = pixels[x,y][1] >> 2
                        b = pixels[x,y][2] >> 3

                        rgb = (r << 11) | g << 5 | b
                        byte = rgb >> 8 | (rgb & 0x00ff) << 8 # COMMENT OUT TO SKIP SWAP
                        outfile.write(struct.pack('H', byte))

    def convert_animated(self, output_prefix='output'):
        for frame_no in range(self.img.n_frames):
            self.img.seek(frame_no)
            self.convert_static(output_prefix, frame_override=frame_no)
            with open(f'{output_prefix}_{frame_no}.bin', mode="rb") as fin, open(f'{output_prefix}_{frame_no}.zl', mode="wb") as fout:
                data = fin.read()
                compressed_data = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
                fout.write(compressed_data)
        with open(f'{os.path.split(output_prefix)[0] or "."}/speed', 'w') as speedfile:
            if 'duration' in self.img.info:
                speedfile.write(str(self.img.info['duration']))

if __name__=="__main__":
    ConvImage(sys.argv[1]).convert(sys.argv[2])
