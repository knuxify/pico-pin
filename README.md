# pico-pin

This is a Micropython project that turns a Raspberry Pi Pico (and potentially other Micropython-supported devices, if you're willing to tweak the parameters) into a little display for animated images.

Images are converted with the png2rgb565.py utility, which takes the image file and an output prefix (for example, "anim/anim" is going to output "anim/anim_0.zl", "anim/anim_1.zl", etc.) as input. You are responsible for scaling and cropping the image so that it fits in the 240x240 display.

Converted images are stored in a folder, with separate files for each frame. .zl contains zlib-compressed data, which is decompressed on the Pico before the image is displayed. Those folders are stored in `/anim/` on the Pico, and that's where `main.py` loads them from.

This program assumes you're using a [1.3" Pico LCD from Waveshare](https://www.waveshare.com/pico-lcd-1.3.htm), but it should be possible to modify it to work on other boards as well.
