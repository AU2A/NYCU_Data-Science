import dlib, cv2, pickle, os
import numpy as np
import matplotlib.pyplot as plt

if not os.path.exists("images"):
    print("Please prepare images in the images folder")
    print("images")
    print(" ╠═makeup")
    print(" ║  ╠═image1.png")
    print(" ║  ╚═image2.png")
    print(" ╚═non-makeup")
    print("    ╠═image1.png")
    print("    ╚═image2.png")
    exit()

if not os.path.exists("landmarks"):
    os.mkdir("landmarks")
    os.mkdir("landmarks/makeup")
    os.mkdir("landmarks/non-makeup")


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

for dict in ["makeup", "non-makeup"]:
    for file in os.listdir("images/" + dict + "/"):
        print(file)
        img = cv2.imread("images/" + dict + "/" + file)
        gray = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        point = np.zeros((68, 2), dtype=int)
        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            landmarks = predictor(image=gray, box=face)

            for n in range(0, 68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                point[n] = [y, x]

        file_path = "landmarks/" + dict + "/" + file

        with open(file_path, "wb") as file:
            pickle.dump(point, file)
