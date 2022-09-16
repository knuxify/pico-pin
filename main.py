# coding: utf-8
from machine import Pin, SPI
#import framebuf
import os
import st7789 as st7789
import zlib
import gc

# Button data
prev_button = Pin(16, Pin.IN, Pin.PULL_UP)
next_button = Pin(20, Pin.IN, Pin.PULL_UP)

# Screen data
screen_width = const(240)
screen_height = const(240)
screen_rotation = const(1)

spi = SPI(1,
		  baudrate=31250000,
		  polarity=1,
		  phase=1,
		  bits=8,
		  firstbit=SPI.MSB,
		  sck=Pin(10),
		  mosi=Pin(11))

display = st7789.ST7789(
	spi,
	screen_width,
	screen_height,
	reset=Pin(12, Pin.OUT),
	cs=Pin(9, Pin.OUT),
	dc=Pin(8, Pin.OUT),
	backlight=Pin(13, Pin.OUT),
	rotation=screen_rotation)

buffer_width = const(240)
buffer_height = const(240)
#fbuf = framebuf.FrameBuffer(buffer, buffer_width, buffer_height, framebuf.RGB565)

def prepare_dir(path, buffer):
	gc.collect()
	files_zl = []
	files_bin = []

	for _file in os.listdir(path):
		filename = path + '/' + _file
		if filename.endswith('.zl'):
			files_zl.append(filename)
		elif filename.endswith('.bin'):
			files_bin.append(filename)

	for filename in files_zl:
		file_out = filename.replace('.zl', '.bin')
		if file_out not in files_bin:
			file_out = filename.replace('.zl', '.bin')
			#decompress_file(filename, file_out, buffer)

			with open(filename, 'rb') as infile:
				zlib.DecompIO(infile).readinto(memoryview(buffer))
			del infile
			with open(file_out, 'wb') as outfile:
				outfile.write(memoryview(buffer))
			del outfile

			# Blit to the buffer to give a sense of progress
			display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)
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

def blit_file(path, buffer, display):
	with open(path, 'rb') as file:
		file.readinto(buffer)
	display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)

def main_loop(display):
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
	root = const('/anim/')
	ll_path = const('/anim/last_loaded')

	last_loaded = None

	try:
		with open(ll_path, 'r') as lfile:
			last_loaded = lfile.read()
	except OSError:
		pass

	animations = []
	for anim, ftype, _, tmp in os.ilistdir(root):
		if ftype != 0x4000:
			continue
		if not last_loaded:
			last_loaded = anim
		animations.append(root + anim)

	#print(f"Found animations: {animations}")

	if not animations:
		raise Exception("No animations!")

	if root + last_loaded not in animations:
		last_loaded = animations[0]
		loaded_no = 0
	else:
		loaded_no = animations.index(root + last_loaded)

	del last_loaded

	gc.collect()

	buffer = bytearray(buffer_width * buffer_height * 2)

	while True:
		del anim
		del anim_files
		del frame
		del max_frame
		anim = animations[loaded_no]
		for _anim in animations:
			if _anim == anim:
				continue

			path = _anim
			for _file in os.listdir(path):
				file = path + '/' + _file
				if file.endswith('.bin'):
					os.remove(file)
			del file, _file

		#print(f"Loading {anim}...")
		anim_files = prepare_dir(anim, buffer)
		with open(ll_path, 'w') as lfile:
			lfile.write(anim[6:])
		frame = 0
		max_frame = len(anim_files) - 1
		while True:
			if prev_button.value() == 0:
				#print(f"Moving to previous animation!")
				loaded_no -= 1
				if loaded_no < 0:
					loaded_no = len(animations) - 1
				break
			elif next_button.value() == 0:
				#print(f"Moving to next animation!")
				loaded_no += 1
				if loaded_no >= len(animations):
					loaded_no = 0
				break
			else:
				#blit_file(anim_files[frame], buffer, display)

				with open(anim_files[frame], 'rb') as file:
					file.readinto(buffer)
				del file
				display.blit_buffer(buffer, 0, 0, buffer_width, buffer_height)

				frame += 1
				if frame > max_frame:
					frame = 0

main_loop(display)
