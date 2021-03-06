import keras
from keras.layers import Flatten, Dense, Dropout, Activation, Conv2D, MaxPool2D, BatchNormalization
from keras.models import Sequential
from keras.models import Model

MODEL_SAVING_PATH = 'models/cnn_mnist_fashion.h5'
FASHION_LABELS = ['T-shirt', 'Trouser', 'Pullover', 'Dress', 'Coat', 'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']


def start_training():
    x_train, y_train, x_test, y_test = load_mmist_fashion_data()

    model = Sequential([
        Conv2D(64, 4, padding='same', input_shape=(28, 28, 1)),
        MaxPool2D(),
        Dropout(0.1),
        Conv2D(64, 4, padding='same'),
        MaxPool2D(),
        Dropout(0.3),
        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(64, activation='relu', name='pre_score'),
        BatchNormalization(),
        Dense(10, name='score'),
        Activation('softmax')
    ])

    # model = keras.models.load_model(MODEL_SAVING_PATH)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    cp_callback = keras.callbacks.ModelCheckpoint(MODEL_SAVING_PATH, save_weights_only=False, save_best_only=True, verbose=1)

    model.fit(x_train, y_train, batch_size=4096, epochs=10000, validation_data=(x_test, y_test), callbacks=[cp_callback])


def load_mmist_fashion_data():
    fashion_mnist = keras.datasets.fashion_mnist

    (x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')

    x_train, x_test = x_train / 255.0, x_test / 255.0

    x_train = x_train.reshape(-1, 28, 28, 1)
    x_test = x_test.reshape(-1, 28, 28, 1)

    return x_train, y_train, x_test, y_test


def get_av_and_score(x):
    model = keras.models.load_model(MODEL_SAVING_PATH)

    extracting_model = Model(inputs=model.input, outputs=[model.get_layer('pre_score').output, model.get_layer('score').output])
    av_output, score_output = extracting_model.predict(x, batch_size=4096, verbose=1)
    return av_output, score_output


def get_score_and_prob(x):
    model = keras.models.load_model(MODEL_SAVING_PATH)

    extracting_model = Model(inputs=model.input, outputs=[model.get_layer('score').output, model.output])
    score_output, prediction = extracting_model.predict(x, batch_size=4096, verbose=1)

    return score_output, prediction


if __name__ == '__main__':
    start_training()
