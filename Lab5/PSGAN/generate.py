import os

# os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from PIL import Image
from psgan import Inference, PostProcess, get_config
from tqdm import tqdm
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-path",
        help="File for the generated image",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--device",
        help="File for the generated image",
        required=True,
        type=str,
    )

    output_path = parser.parse_args().output_path
    device = parser.parse_args().device
    source = "data/non-makeup.txt"
    reference = "data/makeup.txt"
    image_path = "data/images/"
    model_path = "log/snapshot/100_1025_G.pth"
    config_file = "configs/base.yaml"

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    config = get_config()
    config.merge_from_file(config_file)
    config.freeze()

    with open(source, "r") as f:
        source_path = f.readlines()

    with open(reference, "r") as f:
        reference_path = f.readlines()

    inference = Inference(config, device, model_path)
    postprocess = PostProcess(config)

    for i in tqdm(range(len(source_path))):
        source_image = image_path + source_path[i].strip()
        reference_image = image_path + reference_path[i].strip()
        image_name = "pred_" + str(i) + ".png"
        # print(f"Processing {image_name}")

        source_image_data = Image.open(source_image).convert("RGB")
        reference_image_data = Image.open(reference_image).convert("RGB")
        image, face = inference.transfer(
            source_image_data, reference_image_data, with_face=True
        )
        try:
            source_crop = source_image_data.crop(
                (face.left(), face.top(), face.right(), face.bottom())
            )
            image = postprocess(source_crop, image)
            image = image.resize((256, 256))
            image.save(output_path + image_name)
        except:
            image = source_image_data.resize((256, 256))
            image.save(output_path + image_name)
        # exit()
