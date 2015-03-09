#!/usr/bin/python

from PIL import Image
from PIL import ImageChops
import sys, time

########################################################################
# Image similarity module
# Two approaches to understand the difference (or similarity)
# of two provided images within a filesystem, from a pixel perspective
# (c) 2015 Tony DiLoreto
########################################################################

def dhash(image, hash_size = 8):
	
    # Grayscale and shrink the image in one step.
    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

    pixels = list(image.getdata())

    # Compare adjacent pixels.
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)

    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0

    return ''.join(hex_string)



def get_image_hash_similarity(img1 = 'whitesquare.jpg', img2 = 'blacksquare.jpg'):

	# start the timer
	start = time.time()

	# ensure we're workign with images not string representations
	image1 = Image.open(img1) if isinstance(img1, str) else img1
	image2 = Image.open(img2) if isinstance(img2, str) else img2

	hash_image1 = dhash(image1)
	hash_image2 = dhash(image2)

	compare_hash_string_similarity(hash_image1, hash_image2)

	print("Completed in {time} seconds".format(time=time.time()-start))


def compare_hash_string_similarity(hash1, hash2):

	hash_list = [int(hash1[i:i+1] == hash2[i:i+1]) for i in range(max(len(hash1), len(hash2)))]

	total_chars = len(hash_list)
	total_matches = sum(hash_list)

	hash_sim = total_matches / total_chars
	hash_diff = 1 - hash_sim

	print("[HASH]: the two images are {:.2%} different".format(hash_diff))
	print("[HASH]: the two images are {:.2%} similar".format(hash_sim))


def get_image_pixel_similarity(img1 = 'whitesquare.jpg', img2 = 'blacksquare.jpg'):

	# start the timer
	start = time.time()

	# ensure we're workign with images not string representations
	image1 = Image.open(img1) if isinstance(img1, str) else img1
	image2 = Image.open(img2) if isinstance(img2, str) else img2


	# First thing to do is resize image2 to be image1's dimensions
	image2 = image2.resize(image1.size, Image.BILINEAR)


	# each of these are lists of (r,g,b) values
	image1_pixels = list(image1.getdata())
	image2_pixels = list(image2.getdata())


	# now need to compare the r, g, b values for each image2_pixels

	# initialize vars
	i = 0
	tot_img_diff = 0
	diff_pixels = 0

	for pix1 in image1_pixels:
		pix2 = image2_pixels[i]

		r_diff = abs(pix1[0] - pix2[0])
		g_diff = abs(pix1[1] - pix2[1])
		b_diff = abs(pix1[2] - pix2[2])

		tot_pix_diff = (r_diff + g_diff + b_diff)

		if tot_pix_diff != 0:
			# print("comparing: " , pix1 , " to " , pix2)
			diff_pixels += 1

		i += 1

		# keep a running total of the difference of each pixel triplet
		tot_img_diff += tot_pix_diff

	# the greatest difference will be 765 * image1.size

	# now calculate our proprietary 'similarity score'
	# similarity = 1 - difference %
	# difference % = tot_img_diff / (image1_size * 255 * 3)
	# where the denominator is the maximum difference

	# print(i)
	# print(tot_img_diff)

	tot_pix = image1.size[0] * image1.size[1]
	hues = 255
	channels = 3
	
	img_diff = float(diff_pixels / tot_pix)
	img_sim = 1 - img_diff

	# print("there were", diff_pixels , "mis-matched pixels out of a total of", tot_pix , "pixels")

	print("[PIXEL]: the two images are {:.2%} different".format(img_diff))
	print("[PIXEL]: the two images are {:.2%} similar".format(img_sim))
	
	print("Completed in {time} seconds".format(time=time.time()-start))



def skimage_test():

	import numpy as np
	import matplotlib.pyplot as plt

	from skimage import data
	from skimage.feature import match_template


	image = data.coins()
	coin = image[170:220, 75:130]

	result = match_template(image, coin)

	ij = np.unravel_index(np.argmax(result), result.shape)
	x, y = ij[::-1]

	fig, (ax1, ax2, ax3) = plt.subplots(ncols=3, figsize=(8, 3))

	ax1.imshow(coin)
	ax1.set_axis_off()
	ax1.set_title('template')

	ax2.imshow(image)
	ax2.set_axis_off()
	ax2.set_title('image')
	# highlight matched region
	hcoin, wcoin = coin.shape
	rect = plt.Rectangle((x, y), wcoin, hcoin, edgecolor='r', facecolor='none')
	ax2.add_patch(rect)

	ax3.imshow(result)
	ax3.set_axis_off()
	ax3.set_title('`match_template`\nresult')
	# highlight matched region
	ax3.autoscale(False)
	ax3.plot(x, y, 'o', markeredgecolor='r', markerfacecolor='none', markersize=10)

	plt.show()



if __name__ == '__main__':
	img1 = sys.argv[1]
	img2 = sys.argv[2]

	# Create image objects
	image1 = Image.open(img1)
	image2 = Image.open(img2)

	# Test pixel by pixel
	get_image_pixel_similarity(img1, img2)

	# Test via greyscaling & hashing
	get_image_hash_similarity(img1, img2)

	# If we need to explore looking for one image within another
	# uncomment the following line and tweak
	# skimage_test()

