# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

""" Demo for image detection"""

#%% 
# Importing necessary basic libraries and modules
import numpy as np
from PIL import Image
import os
#%% 
# PyTorch imports 
import torch
from torch.utils.data import DataLoader

#%% 
# Importing the model, dataset, transformations and utility functions from PytorchWildlife
from PytorchWildlife.models import detection as pw_detection
from PytorchWildlife.data import transforms as pw_trans
from PytorchWildlife.data import datasets as pw_data 
from PytorchWildlife import utils as pw_utils

#%% 
# Setting the device to use for computations ('cuda' indicates GPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

#%% 
# Initializing the MegaDetectorV5 model for image detection
detection_model = pw_detection.MegaDetectorV5(device=DEVICE, pretrained=True)

#%% Single image detection
# Specifying the path to the target image TODO: Allow argparsing
tgt_img_path = os.path.join(".","demo_data","imgs","10050028_0.JPG")

# Opening and converting the image to RGB format
img = np.array(Image.open(tgt_img_path).convert("RGB"))

# Initializing the Yolo-specific transform for the image
transform = pw_trans.MegaDetector_v5_Transform(target_size=detection_model.IMAGE_SIZE,
                                               stride=detection_model.STRIDE)

# Performing the detection on the single image
results = detection_model.single_image_detection(transform(img), img.shape, tgt_img_path)

# Saving the detection results 
pw_utils.save_detection_images(results, os.path.join(".","demo_output"), overwrite=False)

#%% Batch detection
""" Batch-detection demo """

# Specifying the folder path containing multiple images for batch detection
tgt_folder_path = os.path.join(".","demo_data","imgs")

# Creating a dataset of images with the specified transform
dataset = pw_data.DetectionImageFolder(
    tgt_folder_path,
    transform=pw_trans.MegaDetector_v5_Transform(target_size=detection_model.IMAGE_SIZE,
                                                 stride=detection_model.STRIDE),
    extension='JPG' # Can be other extensions based on your own data, such as png. And this argument is case sensitive.
)

# Creating a DataLoader for batching and parallel processing of the images
loader = DataLoader(dataset, batch_size=32, shuffle=False, 
                    pin_memory=True, num_workers=0, drop_last=False)

# Performing batch detection on the images
results = detection_model.batch_image_detection(loader)

#%% Output to annotated images
# Saving the batch detection results as annotated images
pw_utils.save_detection_images(results, "batch_output", overwrite=False)

#%% Output to cropped images
# Saving the detected objects as cropped images
pw_utils.save_crop_images(results, "crop_output", overwrite=False)

#%% Output to JSON results
# Saving the detection results in JSON format
pw_utils.save_detection_json(results, os.path.join(".","batch_output.json"),
                             categories=detection_model.CLASS_NAMES,
                             exclude_category_ids=[], # Category IDs can be found in the definition of each model.
                             exclude_file_path=None)

# Saving the detection results in timelapse JSON format
pw_utils.save_detection_timelapse_json(results, os.path.join(".","batch_output_timelapse.json"),
                                       categories=detection_model.CLASS_NAMES,
                                       exclude_category_ids=[], # Category IDs can be found in the definition of each model.
                                       exclude_file_path=tgt_folder_path,
                                       info={"detector": "MegaDetectorV5"})