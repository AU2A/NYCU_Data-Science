from PIL import Image
import numpy as np
import os

if not os.path.exists("parsing"):
    print("Please prepare parsing in the parsing folder")
    print("parsing")
    print(" ╠═makeup")
    print(" ║  ╠═image1.png")
    print(" ║  ╚═image2.png")
    print(" ╚═non-makeup")
    print("    ╠═image1.png")
    print("    ╚═image2.png")
    exit()

if not os.path.exists("parsing_PSGAN"):
    os.mkdir("parsing_PSGAN")
    os.mkdir("parsing_PSGAN/makeup")
    os.mkdir("parsing_PSGAN/non-makeup")

for dict in ["makeup", "non-makeup"]:
    for file in os.listdir("parsing/" + dict + "/"):
        print(file)
        seg = np.array(Image.open("parsing/" + dict + "/" + file))
        new = np.zeros_like(seg)
        new[seg == 0] = 0
        new[seg == 1] = 5
        new[seg == 2] = 3
        new[seg == 3] = 11
        new[seg == 4] = 1
        new[seg == 5] = 12
        new[seg == 6] = 4
        new[seg == 7] = 2
        new[seg == 8] = 6
        new[seg == 9] = 7
        new[seg == 10] = 13
        new[seg == 11] = 8
        new[seg == 12] = 10
        new[seg == 13] = 9
        img = Image.fromarray(new)
        img.save("parsing_PSGAN/" + dict + "/" + file)
