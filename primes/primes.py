#!/usr/bin/env python3
# pb_color_bars.py: demonstration of generating video content using OpenCV

# This script assumes the availability of the OpenCV and numpy libraries. A
# recommended method for installing these in Python 3 follows:
#
#   pip3 install opencv-contrib-python
#
# General OpenCV information:   https://opencv.org/
# General NumPy information:    https://numpy.org/

#================================================================
# Import standard Python modules.
import argparse
import math

# Import the numpy and OpenCV modules.
import numpy as np
import cv2 as cv

#================================================================
# Define the video properties using the canonical video format for the Pausch
# Bridge lighting system.
frame_rate   = 30
frame_width  = 228
frame_height = 8

# Specify a format code and file format.  The exact combinations of codec and
# file formats available are different for each platform.
codec_code = cv.VideoWriter.fourcc(*'png ') # PNG images, lossless, clean block edges
file_extension = 'avi'

#================================================================
# Define a set of colors as (B,G,R) triples of unsigned 8-bit integers.

colors = ((255, 255, 255), #white
          (0, 0, 255), #red
          (70, 200, 0), #green
          (255, 0, 0), #blue
          (0, 200, 255), #yellow
          (200, 0, 100), #purple
          (0, 0, 0), #black
          )
#================================================================
# Generate successive frames of the video sequence.

def frame_generator(verbose, tempo):
    count = 0             # count of generated frames
    frame_time = 0.0      # time stamp for generated frame in seconds
    keyframe_phase = 0.0  # unit phase for the cross-fade, cycles over 0 to 1

    frame_interval = 1.0 / frame_rate                       # seconds between video frames
    keyframe_interval = 10.0 / tempo                        # seconds between key frames
    keyframe_rate = 1.0 / (frame_rate * keyframe_interval)  # phase / frame

    # Generate two frames to use as keyframes.
    frame0 = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    # frame1[:,4:20,:] = colors[0]

    # Fill the frames with the first two colors.
   
    offset = 4
    frame0[:,:,:] = colors[0]
    frame0[:,0:1*offset,:] = colors[-1]
    frame1 = frame0
    frame1[:,:,:] = colors[0]
    frame1[:,0:1*offset,:] = colors[-1]
    primes = [2, 3, 5, 7, 11]
    prime_index = 0
    current_prime = 2
    multiple = 2
    
    while True:
        # Cross-fade between successive key frames at the given tempo.  This will
        # return a new frame of integer pixels.
        frame = cv.addWeighted(frame0, (1.0 - keyframe_phase), frame1, keyframe_phase, 0.0)

        # Advance the cross-fade phase.
        keyframe_phase += keyframe_rate

        # Once the second keyframe is reached, generate the successor and reset the fade.
        if keyframe_phase >= 1.0:
            keyframe_phase -= 1.0
            frame0 = frame1
            if (current_prime*multiple*offset <= frame_width):
              print(str(current_prime) + " " + str(multiple))
              frame1[:,current_prime*multiple*offset:current_prime*multiple*offset+offset,:] = colors[prime_index+1]
              multiple += 1
              count += 1
            else:
                prime_index += 1
                if prime_index >= len(primes):
                    break
                current_prime = primes[prime_index]
                count += 1
                multiple = 2
        
        # Return the frame and advance the generator state.
        yield frame
        frame_time += frame_interval

#================================================================
# Write a video file in the default format.

def write_video_file(basename, length, verbose, *args):

    # Open the writer with a path, format, frame rate, and size.
    filename = basename + '.' + file_extension
    out = cv.VideoWriter(filename, codec_code, frame_rate, (frame_width, frame_height))

    if verbose:
        print(f"Open file {filename} for output.")

    # Set up the frame generator.
    frame_sequence = frame_generator(verbose, *args)

    # Synthesize some frames and write them to the stream.
    for count in range(length):
        out.write(next(frame_sequence))

    # Release everything when done.
    out.release()

#================================================================
# Main script follows.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = """Primes video generator for the Pausch Bridge.""")
    parser.add_argument( '-v', '--verbose', action='store_true', help='Enable more detailed output.' )
    parser.add_argument( '-l', '--length', type=int, default=480, help='Number of frames to generate (at 30 fps)')
    parser.add_argument( '-t', '--tempo', type=float, default=30.0, help='Tempo of key frames in beats per minute.')
    parser.add_argument( 'basename', default='primes', nargs='?', help='Base name of output file (not including .mp4 extension).')

    args = parser.parse_args()
    write_video_file(args.basename, args.length, args.verbose, args.tempo)