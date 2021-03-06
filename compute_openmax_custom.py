import os
import pickle

import numpy as np

from evt import weibull_fit_tails
from model_for_mnist import load_mnist_data
from model_for_mnist_fashion import load_mmist_fashion_data, get_av_and_score, FASHION_LABELS
from openmax import recalibrate_scores_custom
from matplotlib import pyplot as plt
from multiprocessing import Pool, cpu_count
from functools import partial


def weibull_fit():
    model_path = 'data/mnist_fashion_weibull_model_custom.pkl'
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            return pickle.load(f)

    x, y, _, _ = load_mmist_fashion_data()

    av_output, score_output = get_av_and_score(x)
    predicted_y = np.argmax(score_output, axis=1)

    labels = np.unique(y)
    av_map = {}

    for label in labels:
        av_map[label] = av_output[(y == label) & (predicted_y == y), :]

    model = weibull_fit_tails(av_map, tail_size=200)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    return model


def main():
    weibull_model = weibull_fit()

    x_known, y_known, _, _ = load_mmist_fashion_data()
    x_unknown, y_unknown, _, _ = load_mnist_data()

    input_img = x_unknown[0].squeeze()

    av, score = get_av_and_score(input_img.reshape((-1, 28, 28, 1)))
    av = av[0, :]
    score = score[0, :]

    openmax, softmax = recalibrate_scores_custom(av, score, weibull_model, weibull_model.keys(), alpha_rank=3)

    print("Softmax ")
    for i in softmax:
        print('{:10.4}    '.format(i), end='')
    print()

    print("Openmax ")
    for i in openmax:
        print('{:10.4}    '.format(i), end='')
    print()

    y_softmax = np.argmax(softmax)
    y_openmax = np.argmax(openmax)

    print('-------------------------------')
    print('Softmax label:', FASHION_LABELS[y_softmax])

    openmax_label = 'Unknown' if y_openmax >= len(FASHION_LABELS) else FASHION_LABELS[y_openmax]

    print('Openmax label:', openmax_label)

    plot_image(input_img, openmax_label)


def plot_image(image, label):
    plt.imshow(image, cmap='gray')
    plt.title(label)
    plt.show()


def calculate_openmax_accuracy():
    weibull_model = weibull_fit()

    x_test, y_test, _, _ = load_mnist_data()
    av_output, scores = get_av_and_score(x_test)

    print('Recalibrating scores...')
    av_list = [av_output[i, :] for i in range(av_output.shape[0])]
    score_list = [scores[i, :] for i in range(scores.shape[0])]
    pool = Pool(cpu_count())
    y_predicted = np.array(pool.map(partial(recalibrate_score, weibull_model=weibull_model), zip(av_list, score_list)))

    accuracy = np.mean(y_predicted != y_test)
    print('Accuracy =', accuracy)


def recalibrate_score(input_tuple, weibull_model):
    av, score = input_tuple
    openmax, _ = recalibrate_scores_custom(av, score, weibull_model, weibull_model.keys(), alpha_rank=3)
    return np.argmax(openmax)


if __name__ == '__main__':
    # main()
    calculate_openmax_accuracy()
