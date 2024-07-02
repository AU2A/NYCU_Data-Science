import sys, json, cv2, time
import numpy as np
import tensorflow as tf

outputStatus = False


if __name__ == "__main__":
    startTime = time.time()
    if sys.argv[1]:
        predFile = sys.argv[1]
        model = tf.keras.models.load_model("model/model_40_0.99.h5")

        with open(predFile, "r") as f:
            imagePaths = json.load(f)

        imagePredictions = []

        for imagePath in imagePaths["image_paths"]:
            if outputStatus:
                print(imagePath)
            try:
                img = cv2.imread(imagePath)
                img = cv2.resize(img, (224, 224))
                imgArray = tf.expand_dims(img, 0)
                predictions = model.predict(imgArray)
                score = tf.nn.softmax(predictions[0])
                label = np.argmax(score)
                imagePredictions.append(int(label))
            except:
                imagePredictions.append(int(0))

        result = {"image_predictions": imagePredictions}
        print(
            json.dumps(result, indent=4, ensure_ascii=False),
            end="",
            file=open("image_predictions.json", "w"),
        )
    else:
        print("No file input")
        sys.exit(1)
    if outputStatus:
        print(f"Time: {time.time()-startTime}")
