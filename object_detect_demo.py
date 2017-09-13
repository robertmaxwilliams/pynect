#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  9 19:00:27 2017

@author: max
"""

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import datetime
import time

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image




# This is needed to display the images.
# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
sys.path.append('/Users/max/Documents/models-master/object_detection/') # point to your tensorflow dir
sys.path.append('/Users/max/Documents/models-master/') # point to your tensorflow dir
sys.path.append('/Users/max/Documents/models-master/slim ') # point ot your slim dir


from utils import label_map_util

from utils import visualization_utils as vis_util

# What model to download.
#MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
#MODEL_NAME = 'ssd_inception_v2_coco_11_06_2017'
MODEL_NAME = 'faster_rcnn_resnet101_coco_11_06_2017'

MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'mscoco_label_map.pbtxt'

NUM_CLASSES = 90


"""
opener = urllib.request.URLopener()
opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
tar_file = tarfile.open(MODEL_FILE)
for file in tar_file.getmembers():
  file_name = os.path.basename(file.name)
  if 'frozen_inference_graph.pb' in file_name:
    tar_file.extract(file, os.getcwd())
"""

detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')
    
    
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)
  
# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
#PATH_TO_TEST_IMAGES_DIR = 'test_images'

def detect_objects(path):
    TEST_IMAGE_PATHS = [path]#['flowerpic.jpg', 'live.png']

    # Size, in inches, of the output images.
    IMAGE_SIZE = (12, 8)
    with detection_graph.as_default():
      with tf.Session(graph=detection_graph) as sess:
        # Definite input and output Tensors for detection_graph
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        for image_path in TEST_IMAGE_PATHS:
          image = Image.open(image_path)
          # the array based representation of the image will be used later in order to prepare the
          # result image with boxes and labels on it.
          image_np = load_image_into_numpy_array(image)
          # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
          image_np_expanded = np.expand_dims(image_np, axis=0)
          # Actual detection.
          (boxes, scores, classes, num) = sess.run(
              [detection_boxes, detection_scores, detection_classes, num_detections],
              feed_dict={image_tensor: image_np_expanded})
          #print(boxes, scores, classes, num)
          
          item_counts = defaultdict(int)
          for score, class_index in zip(np.squeeze(scores), np.squeeze(classes)):
              label = category_index[class_index]['name']
              #print(score, label)
              if score > 0.5:
                  print("score: ", score, " Item: ", label)
                  item_counts[category_index[class_index]['name']] += 1
          with open('webserver/items.html', 'w') as textfile:
            textfile.write("<h1>")
            for key, item in item_counts.items():
              textfile.write('<p>' + key + ", " + str(item) + '</p>\n')
            textfile.write("</h1>")
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            textfile.write("<p> Last updated at "+  st)
     
              
          # Visualization of the results of a detection.
          vis_util.visualize_boxes_and_labels_on_image_array(
              image_np,
              np.squeeze(boxes),
              np.squeeze(classes).astype(np.int32),
              np.squeeze(scores),
              category_index,
              use_normalized_coordinates=True,
              line_thickness=8)
          #plt.figure(figsize=IMAGE_SIZE)
          #plt.imshow(image_np)
          #plt.show()
          im = Image.fromarray(image_np)
          print("saving image")
          im.save("tags.jpg")
          im.save("webserver/tags.jpg")

          #plt.savefig(image, "foo.png")
          print("show image")

#detect_objects('kitchen.jpeg')