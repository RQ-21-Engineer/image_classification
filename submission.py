# -*- coding: utf-8 -*-
"""proyek akhir.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jwZHZWg3ss_lzqAU4CvzxxdkS_UnJ0wK

<h1>Image Classification</h1>
<h3>Student Name : Al-Fariqy Raihan</h3>

<br>
<h3>Download Datasets</h3>
"""

!wget https://github.com/dicodingacademy/assets/releases/download/release/rockpaperscissors.zip
!ls -al | grep .zip

"""<br>
<h3>Extract dataset files and delete archive dataset files</h3>
"""

import os
from zipfile import ZipFile

extract_zipfile = ZipFile(file  = "rockpaperscissors.zip", mode = 'r')
extract_zipfile.extractall(path = 'image_datasets')
extract_zipfile.close()

!rm -rf rockpaperscissors.zip
!ls -al

"""<br>
<h3>Setting path datasets and validation set</h3>
"""

# Datasets Path
DATASETS_PATH     = "image_datasets/rockpaperscissors/rps-cv-images"

ROCK_DATASETS     = f"{DATASETS_PATH}/rock"
PAPER_DATASETS    = f"{DATASETS_PATH}/paper"
SCISSORS_DATASETS = f"{DATASETS_PATH}/scissors"


# Validation Set (40 %)
VALIDATION_SET = 0.4

"""<br>
<h3>Checking Images</h3>
"""

total_images = 0
datasets = ["rock", "paper", "scissors"]

for dataset_name in datasets :
  temp_total = len(os.listdir(f"{DATASETS_PATH}/{dataset_name}"))
  total_images += temp_total

  print(f"Total gambar {dataset_name} : {temp_total}")

print(f"\nTotal gambar keseluruhan : {total_images}")

"""<br>
<h3></h3>

<h3>Perform preprocessing of image data generator</h3>
"""

from keras.preprocessing.image import ImageDataGenerator

# Generate Validation Set
validation_datagen = ImageDataGenerator (
    
    validation_split  =  VALIDATION_SET,
    fill_mode         =  "nearest",
    horizontal_flip   =  True,
    rescale           =  1./255,

    brightness_range  =  [0.2,1.0],
    zoom_range        =  0.2,
    shear_range       =  0.2,
    rotation_range    =  30
)


# Generate Train Set
train_datagen = ImageDataGenerator (
    
    validation_split  =  VALIDATION_SET,
    fill_mode         =  "nearest",
    horizontal_flip   =  True,
    rescale           =  1./255,
    
    brightness_range  =  [0.2,1.0],
    zoom_range        =  0.2,
    shear_range       =  0.2,
    rotation_range    =  30
)

"""<br>
<h3>Generate validation and train with categorical mode</h3>
"""

validation_generator = validation_datagen.flow_from_directory (
    
    DATASETS_PATH,
    shuffle     =  True,
    subset      =  "validation",

    target_size =  (150, 150),
    color_mode  =  "rgb",
    class_mode  =  "categorical",
    batch_size  =  16,
)


train_generator = train_datagen.flow_from_directory (
    DATASETS_PATH,
    shuffle     =  True,
    subset      =  "training",

    target_size =  (150, 150),
    color_mode  =  "rgb",
    class_mode  =  "categorical",
    batch_size  =  16,
    
)

"""<br>
<h3>Sequential Model</h3>
"""

from keras.models import Sequential

from keras.layers import (
    Conv2D,
    MaxPooling2D,
    Flatten,
    Dropout,
    Dense
)

sequential_model = Sequential(layers = [

    Conv2D(32, (3,3), strides = (1,1), activation = 'relu', input_shape = (150, 150, 3)),
    MaxPooling2D(pool_size = (2,2), padding = 'valid'),

    Conv2D(64, (3,3), strides = (1,1), activation = 'relu'),
    MaxPooling2D(pool_size = (2,2), padding = 'valid'),

    Conv2D(128, (3,3), strides = (1,1), activation = 'relu'),
    MaxPooling2D(pool_size = (2,2), padding = 'valid'),

    Flatten(),
    Dropout(0.2),

    Dense(128, activation = 'relu'),
    Dense(3,   activation = 'softmax')
], name = "layers")

"""<br>
<h3>Compile model using optimizer</h3>
"""

from keras.optimizers import Adam

Adam(learning_rate = 0.00146, name = 'Adam')
sequential_model.compile(optimizer = 'Adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])

from tensorflow.math import exp
from keras.callbacks import LearningRateScheduler, TensorBoard

learning_rate_schedule = LearningRateScheduler(
    schedule = lambda epoch, learning_rate : learning_rate if epoch < 5 else learning_rate * exp(-0.1),
    verbose  = 1
)

tensor_board_callback = TensorBoard(
    log_dir = 'logs',
    histogram_freq = 0,
    write_graph = True,
    write_images = False,
    update_freq = 'epoch',
    embeddings_freq = 0,
    embeddings_metadata = None
)

sequential_model.summary()

"""<br>
<h3>Training Model</h3>
"""

from tensorflow import device

# Proses Training 
batch_size = 16

with device("/device:GPU:0"):
  history = sequential_model.fit(
        train_generator, 
        epochs =  10, 
        steps_per_epoch = (1314 // batch_size), 
        validation_data = validation_generator, 
        verbose = 1, 
        validation_steps = (874 // batch_size),
        callbacks = [learning_rate_schedule, tensor_board_callback]
  )

"""<br>
<h3>Accuracy And Loss Plot</h3>
"""

import matplotlib.pyplot as plt

# Get Accuracy Value
accuracy = history.history['accuracy']
val_accuracy = history.history['val_accuracy']
epochs = range(len(accuracy))

# Get Loss Value
loss = history.history['loss']
val_loss = history.history['val_loss']

# Plot
titles = ["Accuracy", "Loss"]
scales = [
    [accuracy, val_accuracy],
    [loss, val_loss]
]

for i in range(len(scales)) :
  plt.plot(epochs,scales[i][0], color = 'blue', marker='o', label = "Train", markerfacecolor='white', markersize = 5)
  plt.plot(epochs,scales[i][1], color = 'red',  marker='o', label = "Validation", markerfacecolor='white', markersize = 5)
  plt.title(label = titles[i])
  plt.legend(loc = 0)
  plt.figure()
  plt.show()

"""<br>
<h3>Testing Model</h3>
"""

import numpy as np
from google.colab import files
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from tensorflow.keras.utils import load_img, img_to_array

uploaded = files.upload()

for file_upload in uploaded.keys():

  file_path = file_upload
  image = load_img(file_path, target_size = (150, 150))
  image_plot = plt.imshow(image)
  x = np.expand_dims(a = img_to_array(image), axis=0)

  images = np.vstack(tup = [x])
  classes = sequential_model.predict(x = images, batch_size = 16)
  
  print("\n")
  print('Hasil Prediksi : ',classes[0],'\n')

  if classes[0][0] == 1:
    print('Kategori Gambar : Ini Adalah Batu\n\n')
  elif classes[0][1] == 1:
    print('Kategori Gambar : Ini Adalah Kertas\n\n')
  elif classes[0][2] == 1:
    print('Kategori Gambar : Ini Adalah Gunting\n\n')
  else :
    print('Kategori Gambar : Tidak Diketahui\n\n')