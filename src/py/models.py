import os

import tensorflow as tf
from tensorflow.keras import Input
from tensorflow.keras import backend as keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import LearningRateScheduler, ModelCheckpoint
from tensorflow.keras.layers import *
from tensorflow.keras.losses import *
from tensorflow.keras.models import *
from tensorflow.keras.optimizers import *


def unet_2D(width, height, neighbors, NumberFilters=64, dropout=0.1, learning_rate=0.0001):

    # tf.debugging.set_log_device_placement(True)
    strategy = tf.distribute.MirroredStrategy()
    with strategy.scope():

        inputs = Input((width, height, neighbors))
        rescale = layers.experimental.preprocessing.Rescaling(scale=1./255)(inputs)
        
        dataAug = layers.experimental.preprocessing.RandomFlip(mode="horizontal_and_vertical")(rescale)
        dataAug = layers.experimental.preprocessing.RandomRotation(0.15)(dataAug)
        dataAug = layers.experimental.preprocessing.RandomTranslation(
            height_factor=0.1, width_factor=0.1)(dataAug)

        conv1 = Conv2D(1*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(dataAug)
        # conv1 = layers.BatchNormalization()(conv1)
        conv1 = Conv2D(1*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
        # conv1 = layers.BatchNormalization()(conv1)
        conv1 = Dropout(dropout)(conv1)
        down1 = MaxPooling2D(pool_size=(2, 2))(conv1)

        conv2 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down1)
        # conv2 = layers.BatchNormalization()(conv2)
        conv2 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
        # conv2 = layers.BatchNormalization()(conv2)
        conv2 = Dropout(dropout)(conv2)
        down2 = MaxPooling2D(pool_size=(2, 2))(conv2)

        conv3 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down2)
        # conv3 = layers.BatchNormalization()(conv3)
        conv3 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
        # conv3 = layers.BatchNormalization()(conv3)
        conv3 = Dropout(dropout)(conv3)
        down3 = MaxPooling2D(pool_size=(2, 2))(conv3)

        conv4 = Conv2D(8*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down3)
        # conv4 = layers.BatchNormalization()(conv4)
        conv4 = Conv2D(8*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
        # conv4 = layers.BatchNormalization()(conv4)
        conv4 = Dropout(dropout)(conv4)
        down4 = MaxPooling2D(pool_size=(2, 2))(conv4)

        conv5 = Conv2D(16*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down4)
        # conv5 = layers.BatchNormalization()(conv5)
        conv5 = Conv2D(16*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
        # conv5 = layers.BatchNormalization()(conv5)

        up6 = Conv2DTranspose(8*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
        concat6 = concatenate([up6, conv4], axis = 3)
        concat6 = Dropout(dropout)(concat6)
        conv6 = Conv2D(8*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat6)
        # conv6 = layers.BatchNormalization()(conv6)
        conv6 = Conv2D(8*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)
        # conv6 = layers.BatchNormalization()(conv6)

        up7 = Conv2DTranspose(4*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)
        concat7 = concatenate([up7, conv3], axis = 3)
        concat7 = Dropout(dropout)(concat7)
        conv7 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat7)
        # conv7 = layers.BatchNormalization()(conv7)
        conv7 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)
        # conv7 = layers.BatchNormalization()(conv7)

        up8 = Conv2DTranspose(2*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)
        concat8 = concatenate([up8, conv2], axis = 3)
        concat8 = Dropout(dropout)(concat8)
        conv8 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat8)
        # conv8 = layers.BatchNormalization()(conv8)
        conv8 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)
        # conv8 = layers.BatchNormalization()(conv8)

        up9 = Conv2DTranspose(1*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)
        concat9 = concatenate([up9, conv1], axis = 3)
        concat9 = Dropout(dropout)(concat9)
        conv9 = Conv2D(1*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat9)
        # conv9 = layers.BatchNormalization()(conv9)
        conv9 = Conv2D(1*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
        # conv9 = layers.BatchNormalization()(conv9)

        out = Conv2D(1, 1, activation = 'sigmoid')(conv9)
        model = Model(inputs, out)

        model.compile(optimizer = Adam(lr=learning_rate), loss = losses.SparseCategoricalCrossentropy(), metrics = ['accuracy'])
        # tf.keras.utils.plot_model(model, show_shapes=True)
        model.summary()

        return model



def unet(width, height, neighbors):

    inputs = Input((width, height, neighbors))

    conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(inputs)
    # conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

    conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool1)
    # conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

    conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool2)
    # conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

    conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool3)
    # conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
    drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

    conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool4)
    # conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
    drop5 = Dropout(0.5)(conv5)

    up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))
    merge6 = concatenate([drop4,up6], axis = 3)
    conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge6)
    # conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)

    up7 = Conv2D(256, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv6))
    merge7 = concatenate([conv3,up7], axis = 3)
    conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge7)
    # conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)

    up8 = Conv2D(128, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv7))
    merge8 = concatenate([conv2,up8], axis = 3)
    conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge8)
    # conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)

    up9 = Conv2D(64, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv8))
    merge9 = concatenate([conv1,up9], axis = 3)
    conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge9)
    # conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
    conv9 = Conv2D(2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)

    conv10 = Conv2D(1, 1, activation = 'sigmoid')(conv9)


    model = Model(inputs, conv10)

    model.compile(optimizer = Adam(lr = 1e-5), loss = 'binary_crossentropy', metrics = ['accuracy']) #1e-4
    
    #model.summary()

    return model
























def unet_2D_deeper(width, height, neighbors, NumberFilters=32, dropout=0.1, learning_rate=0.0001):

    # tf.debugging.set_log_device_placement(True)
    strategy = tf.distribute.MirroredStrategy()
    with strategy.scope():

        inputs = Input((width, height, neighbors))
        rescale = layers.experimental.preprocessing.Rescaling(scale=1./255)(inputs)
        
        dataAug = layers.experimental.preprocessing.RandomFlip(mode="horizontal_and_vertical")(rescale)
        dataAug = layers.experimental.preprocessing.RandomRotation(0.15)(dataAug)
        dataAug = layers.experimental.preprocessing.RandomTranslation(
            height_factor=0.1, width_factor=0.1)(dataAug)

        conv1 = Conv2D(1*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(dataAug)
        conv1 = layers.BatchNormalization()(conv1)
        conv1 = Dropout(dropout)(conv1)
        down1 = MaxPooling2D(pool_size=(2, 2))(conv1)

        conv2 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down1)
        conv2 = layers.BatchNormalization()(conv2)
        conv2 = Dropout(dropout)(conv2)
        down2 = MaxPooling2D(pool_size=(2, 2))(conv2)

        conv3 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down2)
        conv3 = layers.BatchNormalization()(conv3)
        conv3 = Dropout(dropout)(conv3)
        down3 = MaxPooling2D(pool_size=(2, 2))(conv3)

        conv4 = Conv2D(8*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down3)
        conv4 = layers.BatchNormalization()(conv4)
        conv4 = Dropout(dropout)(conv4)
        down4 = MaxPooling2D(pool_size=(2, 2))(conv4)

        conv5 = Conv2D(16*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down4)
        conv5 = layers.BatchNormalization()(conv5)
        conv5 = Dropout(dropout)(conv5)
        down5 = MaxPooling2D(pool_size=(2, 2))(conv5)

        conv6 = Conv2D(32*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down5)
        conv6 = layers.BatchNormalization()(conv6)

        up7 = Conv2DTranspose(16*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)
        concat7 = concatenate([up7, conv5], axis = 3)
        concat7 = Dropout(dropout)(concat7)
        conv7 = Conv2D(16*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat7)
        conv7 = layers.BatchNormalization()(conv7)

        up8 = Conv2DTranspose(8*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)
        concat8 = concatenate([up8, conv4], axis = 3)
        concat8 = Dropout(dropout)(concat8)
        conv8 = Conv2D(8*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat8)
        conv8 = layers.BatchNormalization()(conv8)

        up9 = Conv2DTranspose(4*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)
        concat9 = concatenate([up9, conv3], axis = 3)
        concat9 = Dropout(dropout)(concat9)
        conv9 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat9)
        conv9 = layers.BatchNormalization()(conv9)

        up10 = Conv2DTranspose(2*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
        concat10 = concatenate([up10, conv2], axis = 3)
        concat10 = Dropout(dropout)(concat10)
        conv10 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat10)
        conv10 = layers.BatchNormalization()(conv10)

        up11 = Conv2DTranspose(2*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv10)
        concat11 = concatenate([up11, conv1], axis = 3)
        concat11 = Dropout(dropout)(concat11)
        conv11 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat11)
        conv11 = layers.BatchNormalization()(conv11)

        out = Conv2D(1, 1, activation = 'sigmoid')(conv11)
        model = Model(inputs, out)

        model.compile(optimizer = Adam(lr=learning_rate), loss = 'binary_crossentropy', metrics = ['accuracy'])
        model.summary()

        return model



def unet_2D_larger(width, height, neighbors, NumberFilters=64, dropout=0.1, learning_rate=0.0001):

    # tf.debugging.set_log_device_placement(True)
    strategy = tf.distribute.MirroredStrategy()
    with strategy.scope():

        inputs = Input((width, height, neighbors))
        rescale = layers.experimental.preprocessing.Rescaling(scale=1./255)(inputs)
        
        dataAug = layers.experimental.preprocessing.RandomFlip(mode="horizontal_and_vertical")(rescale)
        dataAug = layers.experimental.preprocessing.RandomRotation(0.15)(dataAug)
        dataAug = layers.experimental.preprocessing.RandomTranslation(
            height_factor=0.1, width_factor=0.1)(dataAug)

        conv1 = Conv2D(1*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(dataAug)
        conv1 = layers.BatchNormalization()(conv1)
        conv1 = Conv2D(1*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
        conv1 = layers.BatchNormalization()(conv1)
        conv1 = Dropout(dropout)(conv1)
        conv1 = Conv2D(1*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
        conv1 = layers.BatchNormalization()(conv1)
        conv1 = Dropout(dropout)(conv1)
        down1 = MaxPooling2D(pool_size=(2, 2))(conv1)

        conv2 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down1)
        conv2 = layers.BatchNormalization()(conv2)
        conv2 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
        conv2 = layers.BatchNormalization()(conv2)
        conv2 = Dropout(dropout)(conv2)
        conv2 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
        conv2 = layers.BatchNormalization()(conv2)
        conv2 = Dropout(dropout)(conv2)
        down2 = MaxPooling2D(pool_size=(2, 2))(conv2)

        conv3 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down2)
        conv3 = layers.BatchNormalization()(conv3)
        conv3 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
        conv3 = layers.BatchNormalization()(conv3)
        conv3 = Dropout(dropout)(conv3)
        conv3 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
        conv3 = layers.BatchNormalization()(conv3)
        conv3 = Dropout(dropout)(conv3)
        down3 = MaxPooling2D(pool_size=(2, 2))(conv3)

        conv4 = Conv2D(8*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(down3)
        conv4 = layers.BatchNormalization()(conv4)
        conv4 = Conv2D(8*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
        conv4 = layers.BatchNormalization()(conv4)

        up5 = Conv2DTranspose(4*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
        concat5 = concatenate([up5, conv3], axis = 3)
        concat5 = Dropout(dropout)(concat5)
        conv5 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat5)
        conv5 = layers.BatchNormalization()(conv5)
        conv5 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
        conv5 = layers.BatchNormalization()(conv5)
        conv5 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
        conv5 = layers.BatchNormalization()(conv5)

        up6 = Conv2DTranspose(4*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
        concat6 = concatenate([up6, conv2], axis = 3)
        concat6 = Dropout(dropout)(concat6)
        conv6 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat6)
        conv6 = layers.BatchNormalization()(conv6)
        conv6 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)
        conv6 = layers.BatchNormalization()(conv6)
        conv6 = Conv2D(4*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)
        conv6 = layers.BatchNormalization()(conv6)

        up7 = Conv2DTranspose(2*NumberFilters, 3, strides = (2, 2), activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)
        concat7 = concatenate([up7, conv1], axis = 3)
        concat7 = Dropout(dropout)(concat7)
        conv7 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(concat7)
        conv7 = layers.BatchNormalization()(conv7)
        conv7 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)
        conv7 = layers.BatchNormalization()(conv7)
        conv7 = Conv2D(2*NumberFilters, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)
        conv7 = layers.BatchNormalization()(conv7)

        out = Conv2D(1, 1, activation = 'sigmoid')(conv7)
        model = Model(inputs, out)

        model.compile(optimizer = Adam(lr=learning_rate), loss = 'binary_crossentropy', metrics = ['accuracy'])
        model.summary()

        return model







