from tensorflow.keras.layers import Conv2D, Dense, Dropout
from tensorflow.keras.layers import BatchNormalization, Activation, MaxPooling2D, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.applications.xception import Xception
from tensorflow.keras.optimizers import Adam

from modules.SGDW import SGDW
from modules.vortexPooling import vortex_pooling

def create_model(show_summary = True, img_size = 224, num_classes = 101):
    input_rgb_shape = (img_size, img_size, 3)

    base_model = Xception(input_shape = input_rgb_shape, weights = 'imagenet' , include_top = False )
    
    input_layer = base_model.output
    
    input_layer = Conv2D(128, kernel_size=3, strides=1, padding='same', dilation_rate = (1,1)) (input_layer)
    vortex = vortex_pooling(input_layer)  

    layer1 = MaxPooling2D((2, 2), name="MaxPooling2D")(vortex)
    layer1 = GlobalAveragePooling2D () (layer1)
    layer1 = Dense(512, activation = 'relu' ) (layer1)
    layer1 = Dropout(rate = 0.2 ) (layer1)

    layer2 = Dense(512) (layer1)
    layer2 = BatchNormalization() (layer2)
    layer2 = Activation("relu") (layer2)
    layer2 = Dropout(rate = 0.2 ) (layer2)

    outputLayer = Dense (num_classes, activation = 'softmax', name='classifier') (layer2)
    model = Model (inputs = base_model.input, outputs = outputLayer)

    #
    # Custom SGDW is giving issues on Apple Silicon see https://github.com/keras-team/keras/issues/18224
    # Fallback to Kera's Adam optimizer
    #
    optimizer = Adam(ema_momentum=0.9, learning_rate=0.01, weight_decay=1e-4)
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['acc'])
    if show_summary:
        model.summary()
    return model