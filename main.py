# coding: utf-8
from machine import Pin, SPI
#import framebuf
import os
import st7789 as st7789
import zlib
import gc

class PicoPin:
    root = const('/anim/')

    screen_width = const(240)
    screen_height = const(240)
    screen_rotation = const(1)
    buffer_width = const(240)
    buffer_height = const(240)

    def __init__(self):
        gc.collect()

        self.animations = []
        self.buffer = bytearray(buffer_width * buffer_height * 2)

        self.spi = SPI(1,
                  baudrate=31250000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=SPI.MSB,
                  sck=Pin(10),
                  mosi=Pin(11))

        self.display = st7789.ST7789(
            self.spi,
            self.screen_width,
            self.screen_height,
            reset=Pin(12, Pin.OUT),
            cs=Pin(9, Pin.OUT),
            dc=Pin(8, Pin.OUT),
            backlight=Pin(13, Pin.OUT),
            rotation=self.screen_rotation)

        # Button data
        self.prev_button = Pin(16, Pin.IN, Pin.PULL_UP)
        self.next_button = Pin(20, Pin.IN, Pin.PULL_UP)

    def prepare_dir(self, path):
        gc.collect()
        files_zl = []
        files_bin = []

        for _file in os.listdir(path):
            filename = path + '/' + _file
            if filename.endswith('.zl'):
                files_zl.append(filename)
            elif filename.endswith('.bin'):
                files_bin.append(filename)

        if len(files_zl) != len(files_bin):
            for _file in files_bin:
                os.remove(_file)
                files_bin = []

        for filename in files_zl:
            file_out = filename.replace('.zl', '.bin')
            if file_out not in files_bin:
                file_out = filename.replace('.zl', '.bin')
                #decompress_file(filename, file_out, buffer)

                if self.prev_button.value() == 0 or self.next_button.value() == 0 and len(files_bin) > 1:
                    break
                else:
                    with open(filename, 'rb') as infile:
                        zlib.DecompIO(infile).readinto(memoryview(self.buffer))
                    del infile
                    with open(file_out, 'wb') as outfile:
                        outfile.write(memoryview(self.buffer))
                    del outfile

                # Blit to the buffer to give a sense of progress
                self.display.blit_buffer(self.buffer, 0, 0, self.buffer_width, self.buffer_height)
                files_bin.append(file_out)
                gc.collect()

        del _file
        del file_out
        del filename
        del files_zl
        f = sorted(files_bin)
        del files_bin
        gc.collect()

        return f

    #def blit_file(self, path):
    #   with open(path, 'rb') as file:
    #       file.readinto(self.buffer)
    #   self.display.blit_buffer(self.buffer, 0, 0, self.buffer_width, self.buffer_height)

    def main_loop(self):
        # Animations are stored in the "anim" folder and loaded in
        # alphabetical order.
        # A file named "last_loaded" is automatically placed in this
        # folder, and contains the name of the last loaded animation
        # (to be used in open_dir).

        # Each animation is stored in a separate folder, which
        # contains the frames in either .bin or .zl format.
        # The program also looks for a file named "speed", which
        # contains the length of one frame. If this file is not found,
        # the animation runs at a full uncapped speed.
        gc.collect()
        ll_path = const('/anim/last_loaded')

        last_loaded = None

        try:
            with open(ll_path, 'r') as lfile:
                last_loaded = lfile.read()
        except OSError:
            pass

        for anim, ftype, _, tmp in os.ilistdir(root):
            if ftype != 0x4000:
                continue
            if not last_loaded:
                last_loaded = anim
            self.animations.append(self.root + anim)

        #print(f"Found animations: {animations}")

        if not self.animations:
            raise Exception("No animations!")

        if last_loaded not in self.animations:
            last_loaded = self.animations[0]
            loaded_no = 0
        else:
            loaded_no = self.animations.index(last_loaded)

        del last_loaded

        while True:
            gc.collect()

            anim = self.animations[loaded_no]
            for _anim in self.animations:
                if _anim == anim:
                    continue

                path = _anim
                has_zl = False
                for _file in os.listdir(path):
                    if _file.endswith('.zl'):
                        has_zl = True
                        break
                if has_zl:
                    for _file in os.listdir(path):
                        file = path + '/' + _file
                        if file.endswith('.bin'):
                            os.remove(file)
                del file, _file, has_zl

            #print(f"Loading {anim}...")
            self.anim_files = self.prepare_dir(anim)
            if len(self.anim_files) <= 0:
                # Loading was paused
                if self.prev_button.value() == 0:
                    #print(f"Moving to previous animation!")
                    loaded_no -= 1
                    if loaded_no < 0:
                        loaded_no = len(self.animations) - 1
                elif self.next_button.value() == 0:
                    #print(f"Moving to next animation!")
                    loaded_no += 1
                    if loaded_no >= len(self.animations):
                        loaded_no = 0
                continue
            with open(ll_path, 'w') as lfile:
                lfile.write(anim)
            frame = 0
            max_frame = len(self.anim_files) - 1
            while True:
                if self.prev_button.value() == 0:
                    #print(f"Moving to previous animation!")
                    loaded_no -= 1
                    if loaded_no < 0:
                        loaded_no = len(self.animations) - 1
                    break
                elif self.next_button.value() == 0:
                    #print(f"Moving to next animation!")
                    loaded_no += 1
                    if loaded_no >= len(self.animations):
                        loaded_no = 0
                    break
                else:
                    #blit_file(anim_files[frame], buffer, display)

                    with open(self.anim_files[frame], 'rb') as file:
                        file.readinto(self.buffer)
                    self.display.blit_buffer(self.buffer, 0, 0, self.buffer_width, self.buffer_height)

                    frame += 1
                    if frame > max_frame:
                        frame = 0

PicoPin().main_loop()
