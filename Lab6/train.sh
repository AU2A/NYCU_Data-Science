cd semi-supervised-segmentation
accelerate launch --multi_gpu --num_processes=2 train.py --config configs/train.yaml