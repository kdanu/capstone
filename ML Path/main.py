# -*- coding: utf-8 -*-
"""Freshandstalefruit_New.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dyyEvmEw882A80D7_YCqofL1l6MExdgK
"""

from google.colab import drive
drive.mount('/content/gdrive')

import os
os.environ['KAGGLE_CONFIG_DIR']='/content/gdrive/MyDrive/kaggle_dataset'

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/gdrive/MyDrive/kaggle_dataset

!ls

!kaggle datasets download -d raghavrpotdar/fresh-and-stale-images-of-fruits-and-vegetables

!mkdir fresh-and-stale-images-of-fruits-and-vegetables
!mv fresh-and-stale-images-of-fruits-and-vegetables.zip fresh-and-stale-images-of-fruits-and-vegetables

# Commented out IPython magic to ensure Python compatibility.
# %cd fresh-and-stale-images-of-fruits-and-vegetables

!unzip fresh-and-stale-images-of-fruits-and-vegetables.zip

import numpy as np
import os
import PIL
import PIL.Image
import tensorflow as tf
import tensorflow_datasets as tfds

import pathlib
data_dir = '/content/gdrive/My Drive/kaggle_dataset/fresh-and-stale-images-of-fruits-and-vegetables'
data_dir = pathlib.Path(data_dir)

print(data_dir)

image_count = len(list(data_dir.glob('*/*.png')))
print(image_count)

image_count = len(list(data_dir.glob('*/*.jpg')))
print(image_count)

batch_size = 32
img_height = 180
img_width = 180

fresh_apple = list(data_dir.glob('fresh_apple/*'))
PIL.Image.open(str(fresh_apple[0]))

fresh_apple = list(data_dir.glob('fresh_apple/*'))
PIL.Image.open(str(fresh_apple[1]))

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_names = train_ds.class_names
print(class_names)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
  for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(images[i].numpy().astype("uint8"))
    plt.title(class_names[labels[i]])
    plt.axis("off")

for image_batch, labels_batch in train_ds:
  print(image_batch.shape)
  print(labels_batch.shape)
  break

from tensorflow.keras import layers

normalization_layer = tf.keras.layers.experimental.preprocessing.Rescaling(1./255)

normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))
first_image = image_batch[0]
# Notice the pixels values are now in `[0,1]`.
print(np.min(first_image), np.max(first_image))

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.layers import LSTM, Input, TimeDistributed
from keras.models import Model
from keras.optimizers import RMSprop, SGD



num_classes = 12

model = tf.keras.Sequential([
    layers.Conv2D(32, (3,3), strides=(1,1), activation="relu", input_shape=(180,180,3)),
    layers.BatchNormalization(axis=1),
    layers.MaxPooling2D(pool_size=(2,2)),
    layers.Dropout(0.25),
    layers.Conv2D(64, (3,3), activation="relu"),
    layers.MaxPooling2D(pool_size=(2,2)),
    layers.Dropout(0.25),
    layers.Conv2D(64, (3,3), activation="relu"),
    layers.MaxPooling2D(pool_size=(2,2)),
    layers.Dropout(0.25),
    layers.Conv2D(128, (3,3), activation="relu"),
    layers.MaxPooling2D(pool_size=(2,2)),
    layers.Dropout(0.25),
    layers.Conv2D(128, (3,3), activation="relu"),
    layers.MaxPooling2D(pool_size=(2,2)),
    layers.Dropout(0.25),
    layers.Flatten(),
    layers.Dense(512, activation="relu"),
    layers.Dense(num_classes, activation="softmax")
])

model.summary()

model.compile(
  optimizer='adam',
  loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True),
  metrics=['accuracy'])

history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=9
)

import numpy as np

from google.colab import files
from keras.preprocessing import image

uploaded=files.upload()

for fn in uploaded.keys():
 
  # predicting images
  path = fn
  img=image.load_img(path, target_size=(180, 180))
  
  x=image.img_to_array(img)
  x=np.expand_dims(x, axis=0)
  images = np.vstack([x])
  fruit_list = ["Fresh Apple", "Fresh Banana", "Fresh Orange", "Stale Apple", "Stale Banana", "Stale Orange"]
  
  classes = model.predict(images, batch_size=32)
  print(fruit_list[np.argmax(classes)])
  print('Accuracy:', np.max(classes)*100, '%')

model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)

model.save_weights("/content/gdrive/MyDrive/kaggle_dataset/model-agrostock11.h5")

#Graphic
accuracy      = history.history['accuracy']
val_accuracy  = history.history['val_accuracy']
loss     = history.history['loss']
val_loss = history.history['val_loss']

epochs   = range(len(accuracy))

plt.plot  (epochs, accuracy, label='Training Accuracy')
plt.plot  (epochs, val_accuracy, label= 'Validation Accuracy')
plt.legend(['Training Accuracy', 'Validation Accuracy'])
plt.title ('Training and Validation Accuracy')
plt.figure()

plt.plot  ( epochs, loss, label='Training Loss')
plt.plot  ( epochs, val_loss, label='Validation Loss')
plt.legend(['Training Loss', 'Validation Loss'])
plt.title ('Training and Validation Loss')

# EXERCISE: Use the tf.saved_model API to save your model in the SavedModel format. 
export_dir = 'saved_model/1'

tf.saved_model.save(model, export_dir)

# Select mode of optimization
mode = "Speed" 

if mode == 'Storage':
    optimization = tf.lite.Optimize.OPTIMIZE_FOR_SIZE
elif mode == 'Speed':
    optimization = tf.lite.Optimize.OPTIMIZE_FOR_LATENCY
else:
    optimization = tf.lite.Optimize.DEFAULT

# EXERCISE: Use the TFLiteConverter SavedModel API to initialize the converter

converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)

# Set the optimzations
converter.optimizations = [optimization]

# Invoke the converter to finally generate the TFLite model
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('./model.tflite')
tflite_model_file.write_bytes(tflite_model)

