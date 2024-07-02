import cv2, os
from tqdm import tqdm
from skimage.metrics import structural_similarity as ssim

if not os.path.exists("output"):
    print("Please prepare parsing in the output folder")
    print("output")
    print(" ╠═image1.png")
    print(" ╚═image2.png")
    exit()

if not os.path.exists("original"):
    print("Please prepare parsing in the original folder")
    print("original")
    print(" ╠═image1.png")
    print(" ╚═image2.png")

sum = 0


for path in tqdm(os.listdir("output")):
    src = cv2.imread("original/" + path)
    src = cv2.resize(src, (256, 256))
    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    img = cv2.imread("output/" + path)
    img = cv2.resize(img, (256, 256))
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    (score, diff) = ssim(src_gray, img_gray, full=True)
    diff = (diff * 255).astype("uint8")
    sum += score

print("Average SSIM: {}".format(sum / len(os.listdir("output"))))
