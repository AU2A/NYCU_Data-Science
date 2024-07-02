import tensorflow as tf
import numpy as np
import cv2


if __name__ == "__main__":
    predFile = "test.csv"
    model = tf.keras.models.load_model(
        "_HW2popularPhotoPrediction/model/model_40_0.99.h5"
    )

    total = 0
    correct = 0
    allImages = []
    with open(predFile, "r") as f:
        for line in f:
            total += 1
            imagePath, isPopular = line.strip().split(",")
            print(f"{imagePath}")
            try:
                img = cv2.imread(imagePath)
                img = cv2.resize(img, (224, 224))
                imgArray = tf.expand_dims(img, 0)
                predictions = model.predict(imgArray)
                score = tf.nn.softmax(predictions[0])
                label = np.argmax(score)
            except:
                print(f"Error: {imagePath}")
                continue
            print(f"{isPopular},{int(label)}")
            if int(label) == int(isPopular):
                correct += 1
            print(f"Accuracy: {correct/total}")
    print(f"Accuracy: {correct/total}")
