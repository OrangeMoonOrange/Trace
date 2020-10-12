import pyximport; pyximport.install()
from src.kde import subiterations
import numpy as np
import scipy.ndimage as nd
from scipy.ndimage import imread
from scipy.misc import imsave, toimage
from scipy.stats import threshold

from PIL import Image
Image.MAX_IMAGE_PIXELS = None

skeleton_images_path = "../../temp/skeleton_images/"

class GrayscaleSkeleton:
    def __init__(self):
        pass
    
    def skeletonize(self, image,isdebug=0):
        sys.stdout.write("\nGrayscaleSkeleton ing... \n")
        sys.stdout.flush()
        #image = grey_closing(image, footprint=circle(8), mode='constant', cval=0.0)
        image = add_zero_mat(image)
        prev_binary_image = np.zeros_like(image)
        image_bit_depth = (image.dtype.itemsize * 8) / 2
        # print ("image_bit_depth: ") + str(image_bit_depth)
        # image_thresholds = [2**x for x in range(image_bit_depth, 3, -1)] + range(15, 0, -1)
        # image_thresholds = [2**x for x in range(image_bit_depth, 2, -1)]
        image_thresholds=[16384, 8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7,6,5,4,3,2,1]

        # print ("image_thresholds: ") + str(image_thresholds)
        
        for curr_threshold in image_thresholds:

            curr_thresh_image = threshold(image, curr_threshold)
            
            curr_binary_image = curr_thresh_image.astype(np.bool).astype(np.int)
            if(isdebug):
                imsave(skeleton_images_path + ("binary_") + str(curr_threshold) + (".png"), curr_binary_image)
            
            curr_sum_image = (prev_binary_image + curr_binary_image)
            curr_skeleton_image = self.thin_pixels(curr_sum_image)
            if(isdebug):
                imsave(skeleton_images_path + ("skeleton_") + str(curr_threshold) + (".png"), curr_skeleton_image)
            # print ("curr_skeleton max: ") + str(curr_skeleton_image.max())
            
            prev_binary_image = curr_skeleton_image

        sys.stdout.write("\nGrayscaleSkeleton done... \n")
        sys.stdout.flush()

        return remove_zero_mat(prev_binary_image)
    
    def thin_pixels(self, image):
        pixel_removed = True
        
        neighbors = nd.convolve((image>0).astype(np.int),[[1,1,1],[1,0,1],[1,1,1]],mode='constant',cval=0.0)
        fg_pixels = np.where((image==1) & (neighbors >= 2) & (neighbors <= 6))
        check_pixels = zip(fg_pixels[0], fg_pixels[1])

        while len(check_pixels)>0:
            (image, sub1_check_pixels) = self.parallel_sub(subiterations.first_subiteration, image, check_pixels)
            (image, sub2_check_pixels) = self.parallel_sub(subiterations.second_subiteration, image, list(set(check_pixels + sub1_check_pixels)))
            check_pixels=list(set(sub1_check_pixels+sub2_check_pixels))

        neighbors = nd.convolve(image>0,[[1,1,1],[1,0,1],[1,1,1]],mode='constant',cval=0.0)
        fg_pixels = np.where(image==1)
        check_pixels = zip(fg_pixels[0],fg_pixels[1])
        (image, _) = self.parallel_sub(self.empty_pools, image, check_pixels)
        return image
    
    def parallel_sub(self, sub_function, image, fg_pixels):
        #manager = Manager()
        #queue = manager.Queue()
        #next_queue = manager.Queue()
        
        #num_procs = int(math.ceil(float(cpu_count()) * 0.75))
        #workload_size = int(math.ceil(float(len(fg_pixels)) / float(num_procs)))
        
        process_list = []
        if len(fg_pixels) == 0:
            return (image, [])

        (zero_pixels, next_pixels) = sub_function(image,fg_pixels)
        for (x,y) in zero_pixels:
            image[x][y]=0;

        return (image, next_pixels)
    
    def empty_pools(self, curr_image, fg_pixels):
        zero_pixels = {}
        
        for (i, j) in fg_pixels:
            p2 = curr_image[i - 1][j]
            p3 = curr_image[i - 1][j + 1]
            p4 = curr_image[i][j + 1]
            p5 = curr_image[i + 1][j + 1]
            p6 = curr_image[i + 1][j]
            p7 = curr_image[i + 1][j - 1]
            p8 = curr_image[i][j - 1]
            p9 = curr_image[i - 1][j - 1]
            
            if (bool(p2) + bool(p3) + bool(p4) + bool(p5) + bool(p6) + bool(p7) + bool(p8) + bool(p9) > 6):
                zero_pixels[(i,j)] = 0
        
        return zero_pixels,[]

#
# helper functions
#
def add_zero_mat(image):
    num_rows, num_cols = image.shape
    
    image = np.insert(image, num_rows, np.zeros(num_cols, dtype=np.int), 0)
    image = np.insert(image, 0, np.zeros(num_cols, dtype=np.int), 0)
    
    num_rows, num_cols = image.shape
    
    image = np.insert(image, num_cols, np.zeros(num_rows, dtype=np.int), 1)
    image = np.insert(image, 0, np.zeros(num_rows, dtype=np.int), 1)
    
    return image

def remove_zero_mat(image):
    num_rows, num_cols = image.shape
    
    image = np.delete(image, num_rows - 1, 0)
    image = np.delete(image, 0, 0)
    image = np.delete(image, num_cols - 1, 1)
    image = np.delete(image, 0, 1)
    
    return image

def circle(radius):
    x, y = np.mgrid[:(2 * radius) + 1, :(2 * radius) + 1]
    circle = (x - radius) ** 2 + (y - radius) ** 2
    return (circle <= (radius ** 2)).astype(np.int)

import sys, time
if __name__ == '__main__':
    input_filename = "../../temp/kde.png"
    output_filename = "../../temp/skeleton.png"
    
    print ("input filename: ") + str(input_filename)
    print ("output filename: ") + str(output_filename)
    
    input_kde = imread(input_filename)
    s = GrayscaleSkeleton()
    
    start_time = time.time()

    skeleton = s.skeletonize(input_kde,0)

    print ("total elapsed time: ") + str(time.time() - start_time) + (" seconds")
    
    toimage(skeleton, cmin=0, cmax=255).save(output_filename)

    imsave("../../temp/sss.jpg", skeleton)
