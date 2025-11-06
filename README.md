# SimLingo セットアップガイド

このガイドでは、SimLingoの環境構築手順を説明します。

## 前提条件

- CARLA 0.9.15がインストールされていること
- Conda/Minicondaがインストールされていること
- Git LFSがインストールされていること
- NVIDIA GPU（CUDA対応）

## セットアップ手順

### 1. 環境変数の設定

```bash
export CARLA_ROOT=/path/to/your/carla0915
export REPO_ROOT=/path/to/your/simlingo_model
```

> **注意**: パスは各自の環境に合わせて変更してください。

### 2. Conda環境の作成

```bash
# 最小限の環境作成
conda create -n sim310 python=3.10 cuda-toolkit=12.8 -c nvidia/label/cuda-12.8.0 -c conda-forge

# 環境のアクティベート
conda activate sim310

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. CUDA環境の設定

```bash
export CUDA_HOME=$CONDA_PREFIX
```

### 4. Flash Attentionのインストール

```bash
pip install flash-attn==2.8.3 --no-build-isolation
```

> **注意**: このステップは時間がかかる場合があります。十分なメモリ（16GB以上推奨）が必要です。

### 5. CARLAパッケージのインストール

```bash
pip install /path/to/carla-0.9.15-cp310-cp310-manylinux_2_27_x86_64.whl
```

> **注意**: CARLAのwhlファイルは[PyPI](https://pypi.org/project/carla/0.9.15/#files)からダウンロードできます。

### 6. SimLingoモデルのダウンロード

```bash
# リポジトリをクローン
git clone https://huggingface.co/RenzKa/simlingo

# ディレクトリに移動
cd simlingo

# LFSファイルをプル
git lfs pull
```

## モデルの推論

```
python3 start_eval_simlingo.py
```
## 動作確認

環境が正しくセットアップされたか確認するには:

```bash
# PyTorchとCUDAの確認
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'CUDA version: {torch.version.cuda}')"

# CARLAの確認
python -c "import carla; print(f'CARLA version: {carla.__version__}')"
```

## トラブルシューティング

### Git LFSのエラーが発生する場合

```bash
# Git LFSをインストール
git lfs install

# 再度プルを試行
git lfs pull
```

### CARLAパッケージが見つからない場合

- whlファイルのパスが正しいか確認してください
- Python 3.10用のwhlファイルをダウンロードしているか確認してください

## 環境変数の永続化（オプション）

毎回環境変数を設定するのが面倒な場合、`.bashrc`または`.zshrc`に追加できます:

```bash
# ~/.bashrc または ~/.zshrc に追記
export CARLA_ROOT=/path/to/your/carla0915
export REPO_ROOT=/path/to/your/simlingo_model
export CUDA_HOME=$CONDA_PREFIX
```

変更を反映:
```bash
source ~/.bashrc  # または source ~/.zshrc
```

## システム要件

- **OS**: Linux (Ubuntu 20.04以降推奨)
- **GPU**: NVIDIA GPU (CUDA 12.8対応)
- **メモリ**: 16GB以上推奨
- **ストレージ**: 20GB以上の空き容量

