```
conda env create -f environment.yaml
conda activate sim310
```


```
export CARLA_ROOT=/home/thoth-22/software/carla0915
export REPO_ROOT=/home/thoth-22/kei_ws/simlingo_model
```


```
# 最小限の環境作成
conda create -n sim310 python=3.10 cuda-toolkit=12.8 -c nvidia/label/cuda-12.8.0 -c conda-forge

# アクティベート
conda activate sim310

# requirements.txtからインストール
pip install -r requirements.txt

# CUDA_HOME設定
export CUDA_HOME=$CONDA_PREFIX

# flash-attnインストール
pip install flash-attn==2.8.3 --no-build-isolation

https://pypi.org/project/carla/0.9.15/#files

pip install /home/thoth-22/kei_ws/carla-0.9.15-cp310-cp310-manylinux_2_27_x86_64.whl


# リポジトリをクローン
git clone https://huggingface.co/RenzKa/simlingo

# ディレクトリに移動
cd simlingo

# LFSファイルをプル
git lfs pull


```