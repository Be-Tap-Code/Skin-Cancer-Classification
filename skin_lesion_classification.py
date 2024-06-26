# -*- coding: utf-8 -*-
"""Skin Lesion Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19A97XkdsTl6y82w1VK05toblWRVD9L1F
"""

import os
import math
import random
# import warnings

import matplotlib.pyplot as plt
import seaborn as sns

import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow import keras
from glob import glob

# Reading the data from HAM_metadata.csv
skin_df = pd.read_csv('../input/skin-cancer-mnist-ham10000/HAM10000_metadata.csv')
skin_df = skin_df[['image_id', 'dx']]

skin_df

skin_df.dtypes

lesion_type_dict = {
    'nv': 'Melanocytic nevi',
    'mel': 'Melanoma',
    'bkl': 'Benign keratosis-like lesions ',
    'bcc': 'Basal cell carcinoma',
    'akiec': 'Actinic keratoses',
    'vasc': 'Vascular lesions',
    'df': 'Dermatofibroma'
}
base_skin_dir = '../input/skin-cancer-mnist-ham10000'

# Merge images from both folders into one dictionary

imageid_path_dict = {os.path.splitext(os.path.basename(x))[0]: x
                     for x in glob(os.path.join(base_skin_dir, '*', '*.jpg'))}

# Create new columns for readability

skin_df['path'] = skin_df['image_id'].map(imageid_path_dict.get)
skin_df['cell_type'] = skin_df['dx'].map(lesion_type_dict.get)
skin_df['cell_type_idx'] = pd.Categorical(skin_df['cell_type']).codes

cell_type_idx_mapping = dict(zip(skin_df['cell_type_idx'], skin_df['cell_type']))

skin_df.head()

np.sum(skin_df.isna())

cell_type_mapping = dict(zip(skin_df['cell_type'], skin_df['cell_type_idx']))

# Print the mapping
for cell_type, idx in cell_type_mapping.items():
    print(f"{cell_type},\t\tIndex: {idx}")

"""# Data preprocessing"""

# Plot distribution of skin lesion types

n_samples_by_types = skin_df['dx'].value_counts()
types = lesion_type_dict.values()

plt.bar(n_samples_by_types.index, n_samples_by_types.values)
plt.xlabel('Skin Lesion Type')
plt.ylabel('Count')

plt.title('Distribution of Skin Lesion Types')

plt.show()

"""# Load and resize image"""

SIZE = 128
CHANNELS = 3

"""# Handling Imbalanced Data"""

from sklearn.utils import resample


df_0 = skin_df[skin_df['dx'] == 'nv']
df_1 = skin_df[skin_df['dx'] == 'mel']
df_2 = skin_df[skin_df['dx'] == 'bkl']
df_3 = skin_df[skin_df['dx'] == 'bcc']
df_4 = skin_df[skin_df['dx'] == 'akiec']
df_5 = skin_df[skin_df['dx'] == 'vasc']
df_6 = skin_df[skin_df['dx'] == 'df']

n_samples=800
df_0_balanced = resample(df_0, replace=True, n_samples=n_samples, random_state=42)
df_1_balanced = resample(df_1, replace=True, n_samples=n_samples, random_state=42)
df_2_balanced = resample(df_2, replace=True, n_samples=n_samples, random_state=42)
df_3_balanced = resample(df_3, replace=True, n_samples=n_samples, random_state=42)
df_4_balanced = resample(df_4, replace=True, n_samples=n_samples, random_state=42)
df_5_balanced = resample(df_5, replace=True, n_samples=n_samples, random_state=42)
df_6_balanced = resample(df_6, replace=True, n_samples=n_samples, random_state=42)


# df_0_balanced = resample(df_0, replace=False, n_samples=2000, random_state=42)
# df_1_balanced = resample(df_1, replace=False, n_samples=1000, random_state=42)
# df_2_balanced = resample(df_2, replace=False, n_samples=1000, random_state=42)
# df_3_balanced = resample(df_3, replace=False, n_samples=500, random_state=42)
# df_4_balanced = resample(df_4, replace=False, n_samples=300, random_state=42)
# df_5_balanced = resample(df_5, replace=False, n_samples=100, random_state=42)
# df_6_balanced = resample(df_6, replace=False, n_samples=100, random_state=42)

#Combined back to a single dataframe
skin_df_balanced = pd.concat([df_0_balanced, df_1_balanced,
                              df_2_balanced, df_3_balanced,
                              df_4_balanced, df_5_balanced, df_6_balanced])

skin_df_balanced

skin_df.shape

from skimage import feature
import cv2

def compute_hog_features1(image):
    """ Tính đặc trưng HOG cho một ảnh. """
    channel_1 = image[:, :, 0]
    channel_2 = image[:, :, 1]
    channel_3 = image[:, :, 2]

    hog_features_1 = feature.hog(cv2.resize(channel_1, (128, 128)), orientations=9, pixels_per_cell=(8, 8),
                                cells_per_block=(2, 2), transform_sqrt=True, block_norm="L1")
    hog_features_2 = feature.hog(cv2.resize(channel_2, (128, 128)), orientations=9, pixels_per_cell=(8, 8),
                                cells_per_block=(2, 2), transform_sqrt=True, block_norm="L1")
    hog_features_3 = feature.hog(cv2.resize(channel_3, (128, 128)), orientations=9, pixels_per_cell=(8, 8),
                                cells_per_block=(2, 2), transform_sqrt=True, block_norm="L1")

    hog_features_combined = np.hstack((hog_features_1, hog_features_2, hog_features_3))
    return hog_features_combined

from multiprocessing import Pool
from PIL import Image

def load_resized_image(image_path):
        image = Image.open(image_path)
        resized_image = image.resize((SIZE, SIZE))
        return compute_hog_features1(np.asarray(resized_image))
#         return np.asarray(resized_image)


def load_images_parallel(paths):
    """Loads and resizes images in parallel using multiprocessing."""
    with Pool() as p:
        images = p.map(load_resized_image, paths)

    return images

# test = skin_df.sample(n=100)

# test

# images = load_images_parallel(skin_df['path'])

images = load_images_parallel(skin_df_balanced['path'])

images[0].shape

import matplotlib.pyplot as plt
id = 0
print(skin_df['image_id'].iloc[id], skin_df['dx'].iloc[id])
im = images[id]
plt.imshow(im)

"""# Normalize data and convert labels to one-hot vectors"""

# X = np.asarray(skin_df_balanced['image'].tolist())
X = np.asarray(images)
print(X.shape)
X = X / 255

from keras.utils import to_categorical

# y = skin_df['cell_type_idx']
y = skin_df_balanced['cell_type_idx']
y_cat = to_categorical(y, num_classes=7)
y_cat

"""# Train test split"""

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size = 0.2, random_state=42)

input_shape = (SIZE, SIZE, CHANNELS)
n_classes = 7

"""# Visualize"""

# cannot easily visualize filters lower down
from keras.applications.vgg16 import VGG16
from matplotlib import pyplot
# load the model
model = VGG16()
# retrieve weights from the second hidden layer
filters, biases = model.layers[1].get_weights()
# normalize filter values to 0-1 so we can visualize them
f_min, f_max = filters.min(), filters.max()
filters = (filters - f_min) / (f_max - f_min)
# plot first few filters
n_filters, ix = 6, 1
for i in range(n_filters):
    # get the filter
    f = filters[:, :, :, i]
    # plot each channel separately
    for j in range(3):
    # specify subplot and turn of axis
        ax = pyplot.subplot(n_filters, 3, ix)
        ax.set_xticks([])
        ax.set_yticks([])
        # plot filter channel in grayscale
        pyplot.imshow(f[:, :, j], cmap='gray')
        ix += 1
# show the figure
pyplot.show()

# visualize feature maps output from each block in the vgg model
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import Model
from matplotlib import pyplot
from numpy import expand_dims
# load the model
model = VGG16()
# redefine model to output right after the first hidden layer
ixs = [2, 5, 9, 13, 17]
outputs = [model.layers[i].output for i in ixs]
model = Model(inputs=model.inputs, outputs=outputs)
# load the image with the required shape
img = load_img(skin_df['path'][0], target_size=(224, 224))
# convert the image to an array
img = img_to_array(img)
# expand dimensions so that it represents a single 'sample'
img = expand_dims(img, axis=0)
# prepare the image (e.g. scale pixel values for the vgg)
img = preprocess_input(img)
# get feature map for first hidden layer
feature_maps = model.predict(img)
# plot the output from each block
square = 8
for fmap in feature_maps:
    # plot all 64 maps in an 8x8 squares
    ix = 1
    for _ in range(square):
        for _ in range(square):
        # specify subplot and turn of axis
            ax = pyplot.subplot(square, square, ix)
            ax.set_xticks([])
            ax.set_yticks([])
            # plot filter channel in grayscale
            pyplot.imshow(fmap[0, :, :, ix-1], cmap='gray')
            ix += 1
# show the figure
pyplot.show()

"""# Feat Extractor"""

from keras.applications.vgg16 import VGG16
model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape, classes=n_classes)

model.summary()

# Dùng pre-trained model để lấy ra các feature của ảnh
features = model.predict(X)

# Giống bước flatten trong CNN, chuyển từ tensor 3 chiều sau ConvNet sang vector 1 chiều
features = features.reshape((features.shape[0], 512*4*4))

from sklearn.model_selection import train_test_split
# Chia traing set, test set tỉ lệ 80-20
X_train, X_test, y_train, y_test = train_test_split(features, y, test_size=0.2, random_state=42)

y_train

# Define the callbacks
best_weight_filepath = "/kaggle/working/best_weight.weights.h5"

from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
# Grid search để tìm các parameter tốt nhất cho model. C = 1/lamda, hệ số trong regularisation. Solver là kiểu optimize
# https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
params = {'C' : [0.1, 1.0, 10.0, 100.0]}
model = GridSearchCV(LogisticRegression(multi_class='multinomial'), params)
model.fit(X_train, y_train)
print('Best parameter for the model {}'.format(model.best_params_))

from sklearn.metrics import classification_report
# Đánh giá model
preds = model.predict(X_test)
print(classification_report(y_test, preds))

"""# Finetuning"""

# Thêm thư viện
from sklearn.metrics import classification_report
from keras.applications import VGG16
from sklearn.model_selection import train_test_split
from keras.optimizers import SGD
from keras.optimizers import RMSprop
from keras.applications import VGG16
from keras.layers import Input
from keras.models import Model
from keras.layers import Dense, Dropout, Flatten
import numpy as np
import random
import os
from keras.metrics import Precision, Recall, Accuracy

# Load model VGG 16 của ImageNet dataset, include_top=False để bỏ phần Fully connected layer ở cuối.
baseModel = VGG16(weights='imagenet', include_top=False, input_shape=input_shape, classes=n_classes)

# Xây thêm các layer
# Lấy output của ConvNet trong VGG16
fcHead = baseModel.output

# Flatten trước khi dùng FCs
fcHead = Flatten(name='flatten')(fcHead)

# Thêm FC
fcHead = Dense(256, activation='relu')(fcHead)
fcHead = Dropout(0.5)(fcHead)

# Output layer với softmax activation
fcHead = Dense(7, activation='softmax')(fcHead)

# Xây dựng model bằng việc nối ConvNet của VGG16 và fcHead
model = Model(inputs=baseModel.input, outputs=fcHead)

model.summary()

# Chia traing set, test set tỉ lệ 80-20
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

from tensorflow.keras.preprocessing.image import ImageDataGenerator
# augmentation cho training data
aug_train = ImageDataGenerator(rescale=1./255, channel_shift_range=5, vertical_flip=True,
                         zoom_range=0.2, horizontal_flip=True, fill_mode='nearest')
# augementation cho test
aug_test= ImageDataGenerator(rescale=1./255)

from keras.callbacks import EarlyStopping, ModelCheckpoint

# Define the callbacks
best_weight_filepath = "/kaggle/working/best_weight.weights.h5"

checkpoint = ModelCheckpoint(
    filepath=best_weight_filepath,
    monitor="val_loss",  # monitor metric to determine 'best'
    save_best_only=True,
    save_weights_only=True,  # save only weights, not full model
)

y_train.shape

# freeze VGG model
for layer in baseModel.layers:
    layer.trainable = False

optimizer = RMSprop(learning_rate=0.0001)
model.compile(optimizer=optimizer, loss = 'categorical_crossentropy', metrics = ['accuracy'])
numOfEpoch = 10

# model.fit(aug_train.flow(X_train, y_train, batch_size=32),
#                         steps_per_epoch=len(X_train)//32,
#                         validation_data=(aug_test.flow(X_test, y_test, batch_size=32)),
#                         validation_steps=len(X_test)//32,
#                         epochs=numOfEpoch)
model.fit(X_train, y_train, batch_size=32,
                        steps_per_epoch=len(X_train)//32,
                        validation_split=0.25,
                        validation_steps=len(X_test)//32,
                        epochs=numOfEpoch,
                        callbacks=[checkpoint])

# unfreeze some last CNN layer:
for layer in baseModel.layers[15:]:
    layer.trainable = True

numOfEpoch = 25
optimizer = SGD(0.001)
model.compile(optimizer=optimizer, loss = 'categorical_crossentropy', metrics = ['accuracy'])
# model.fit(aug_train.flow(X_train, y_train, batch_size=32),
#                         steps_per_epoch=len(X_train)//32,
#                         validation_data=(aug_test.flow(X_test, y_test, batch_size=32)),
#                         validation_steps=len(X_test)//32,
#                         epochs=numOfEpoch)

model.fit(X_train, y_train, batch_size=32,
                        steps_per_epoch=len(X_train)//32,
                        validation_split=0.25,
                        validation_steps=len(X_test)//32,
                        epochs=numOfEpoch,
                        callbacks=[checkpoint])

last_weight_filepath = "/kaggle/working/last_weight.weights.h5"
model.save_weights(last_weight_filepath)

model.evaluate(X_test, y_test)

last_weight_filepath = "/kaggle/working/last_weight.weights.h5"
best_weight_filepath = "/kaggle/working/best_weight.weights.h5"

sorted_dict = dict(sorted(cell_type_idx_mapping.items()))

import numpy as np
from keras import backend as K
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.metrics import classification_report

model.load_weights(last_weight_filepath)
predictions = model.predict(X_test)

num_classes = predictions.shape[1]  # Assuming predictions are already one-hot encoded

predictions = np.argmax(predictions, axis=1)
y_test = np.argmax(y_test, axis=1)

report = classification_report(y_test, predictions, target_names=sorted_dict.values())

print(report)

"""# Model VGG16 Training"""

from keras.applications.vgg16 import VGG16
model = VGG16(weights=None, include_top=True, input_shape=input_shape, classes=n_classes)

model.summary()

from keras.metrics import Precision, Recall, Accuracy
from keras.optimizers import Adam

optimizer = Adam(learning_rate=0.0001)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy', Precision(), Recall()])

batch_size = 64
numOfEpoch = 35

# Define the checkpoint callback
from keras.callbacks import EarlyStopping, ModelCheckpoint

# Define the callbacks
best_weight_filepath = "/kaggle/working/best_weight.weights.h5"

checkpoint = ModelCheckpoint(
    filepath=best_weight_filepath,
    monitor="val_loss",  # monitor metric to determine 'best'
    save_best_only=True,
    save_weights_only=True,  # save only weights, not full model
)

from tensorflow.keras.preprocessing.image import ImageDataGenerator
# augmentation cho training data
aug_train = ImageDataGenerator(vertical_flip=True,zoom_range=0.2, horizontal_flip=True, fill_mode='nearest')


# augementation cho test
aug_test= ImageDataGenerator()

his = model.fit(aug_train.flow(X_train, y_train, batch_size=batch_size),
                        steps_per_epoch=len(X_train)//batch_size,
                        validation_data=(aug_test.flow(X_test, y_test, batch_size=batch_size)),
                        callbacks=[checkpoint],
                        validation_steps=len(X_test)//batch_size,
                        epochs=numOfEpoch)

# !rm -rf /kaggle/working/*

# his = model.fit(X_train, y_train, batch_size=batch_size, epochs=numOfEpoch, callbacks=[checkpoint], validation_split=0.25)

last_weight_filepath = "/kaggle/working/last_weight.weights.h5"
model.save_weights(last_weight_filepath)

"""# Evaluate"""

model.evaluate(X_test, y_test)

last_weight_filepath = "/kaggle/working/last_weight.weights.h5"
best_weight_filepath = "/kaggle/working/best_weight.weights.h5"

sorted_dict = dict(sorted(cell_type_idx_mapping.items()))

# summarize history for accuracy
plt.plot(his.history['accuracy'])
plt.plot(his.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

# summarize history for loss
plt.plot(his.history['loss'])
plt.plot(his.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

# summarize history for recall
plt.plot(his.history['recall'])
plt.plot(his.history['val_recall'])
plt.title('model recall')
plt.ylabel('recall')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

# precision
plt.plot(his.history['precision'])
plt.plot(his.history['val_precision'])
plt.title('model precision')
plt.ylabel('precision')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

import numpy as np
from keras import backend as K
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.metrics import classification_report

model.load_weights(last_weight_filepath)
predictions = model.predict(X_test)

num_classes = predictions.shape[1]  # Assuming predictions are already one-hot encoded

predictions = np.argmax(predictions, axis=1)
y_test = np.argmax(y_test, axis=1)

report = classification_report(y_test, predictions, target_names=sorted_dict.values())

print(report)

"""# Random Forest"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

sorted_dict = dict(sorted(cell_type_idx_mapping.items()))

y_pred = clf.predict(X_test)
report = classification_report(y_test, y_pred, target_names=sorted_dict.values())
print(report)

"""# KNN"""

from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train,y_train)

sorted_dict = dict(sorted(cell_type_idx_mapping.items()))

y_pred = knn.predict(X_test)
report = classification_report(y_test, y_pred, target_names=sorted_dict.values())
print(report)

"""# SVM"""

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=123)

from sklearn import svm
from sklearn.metrics import classification_report
svm_model = svm.SVC(kernel='poly')  # Bạn có thể thử các kernel khác như 'rbf', 'poly', etc.

# Huấn luyện mô hình
svm_model.fit(X_train, y_train)

sorted_dict = dict(sorted(cell_type_idx_mapping.items()))

y_pred = svm_model.predict(X_test)
report = classification_report(y_test, y_pred, target_names=sorted_dict.values())
print(report)