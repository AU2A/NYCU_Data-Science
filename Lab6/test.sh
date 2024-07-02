cd semi-supervised-segmentation

python3 train.py --config configs/train.yaml --save-path ../prediction --test --opts MODEL.CHECKPOINT ../model.pth

python3 create_submission.py --pred ../prediction --save-file ../submission.csv