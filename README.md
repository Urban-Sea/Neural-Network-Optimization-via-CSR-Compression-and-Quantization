# CSR圧縮と量子化によるニューラルネットワーク最適化

## 概要

Arduino Uno R4 WiFi上で動作するRGBスキャナーのためのニューラルネットワークを、CSR（Compressed Sparse Row）形式と量子化により圧縮・最適化するプロジェクトです。

## 目標

1. **CSR形式の実装**: L1正則化による疎化を活かし、メモリ使用量を削減
2. **量子化の適用**: CSR圧縮モデルに対して量子化を適用し、さらなる圧縮を実現
3. **次元拡張**: 隠れ層次元を40から100-200へ拡張可能にする
4. **MSE評価**: 「非圧縮」「CSR圧縮」「CSR+量子化」のMSEを比較

## ファイル構成

```
Lec.1/
├── Arduino/                          # Arduino実装コード
│   ├── AI_Before/                    # ニューラルネットワークなし（ベースライン）
│   │   └── AI_Before.ino
│   ├── AI_Model/                     # 通常の密行列形式
│   │   ├── AI_Model.ino
│   │   └── model_parameters.h
│   ├── AI_CSR/                       # CSR形式で圧縮
│   │   ├── AI_CSR.ino
│   │   ├── model_parameters_csr40.h
│   │   ├── model_parameters_csr80.h
│   │   ├── model_parameters_csr120.h
│   │   ├── model_parameters40.h
│   │   ├── model_parameters80.h
│   │   └── model_parameters120.h
│   └── AI_CSR_Quantized/            # CSR+量子化形式
│       └── AI_CSR_Quantized.ino
│
├── train_L1_normalization.ipynb      # 学習とCSR/量子化パラメータ生成
├── mse_calculator.html                # MSE評価ツール（ブラウザで実行）
├── model_parameters.h                # 生成されたパラメータ（密行列形式）
├── model_parameters_csr.h            # 生成されたパラメータ（CSR形式）
│
├── ppm/                              # PPM画像データ
│   ├── AI_Model.data/                # AI_Modelの実験結果
│   │   ├── nn1.ppm ~ nn10.ppm
│   │   └── ...
│   ├── reference_image1.ppm          # MSE評価用の参照画像
│   ├── csr_40_0.01/                  # CSR 40次元、閾値0.01の実験結果
│   │   ├── csr1.ppm ~ csr7.ppm
│   │   └── ...
│   ├── csr_80_0.01/                  # CSR 80次元、閾値0.01の実験結果
│   │   ├── 1.ppm ~ 10.ppm
│   │   └── ...
│   ├── csr_120_0.01/                 # CSR 120次元、閾値0.01の実験結果
│   │   ├── 1.ppm ~ 3.ppm
│   │   └── ...
│   ├── 使わない/                      # 使用しないデータ
│   └── ...                           # その他のPPMファイル
│
├── img/                              # 参照画像
│   ├── reference_image1_cmyk_large.png
│   └── reference_image2_cmyk_large.png
│
├── report/                           # レポート関連
│   ├── pre/                          # プレゼン資料
│   │   ├── bugg.tex, bugg.pdf
│   │   └── ...
│   └── stg/                          # ステージング資料
│       ├── stg.tex, stg.pdf
│       └── ...
│
├── scanner.c                         # スキャナー実装（C言語）
├── scanner_before.c                  # スキャナー実装（旧版）
├── scanner_AI_before.c               # AIなしスキャナー実装
├── requirements.txt                  # Python依存関係
└── README.md                         # このファイル
```

### 主要ディレクトリの説明

#### Arduinoコード
- **`Arduino/AI_Before/`**: ニューラルネットワークなしのベースライン実装
- **`Arduino/AI_Model/`**: 通常の密行列形式のニューラルネットワーク実装
- **`Arduino/AI_CSR/`**: CSR形式で圧縮したニューラルネットワーク実装（40/80/120次元のパラメータファイルを含む）
- **`Arduino/AI_CSR_Quantized/`**: CSR+量子化形式のニューラルネットワーク実装

#### 学習・評価
- **`train_L1_normalization.ipynb`**: モデルの学習、CSR形式への変換、量子化パラメータの生成を行うJupyter Notebook
- **`mse_calculator.html`**: MSE評価ツール（ブラウザで実行、参照画像とスキャン結果を比較）

#### データファイル
- **`ppm/`**: 実験で使用するPPM画像ファイル
  - `AI_Model.data/`: 通常の密行列形式での実験結果
  - `csr_40_0.01/`, `csr_80_0.01/`, `csr_120_0.01/`: 各次元・閾値でのCSR実験結果
- **`img/`**: 参照画像（PNG形式）
- **`ppm/reference_image1.ppm`**: MSE評価で使用する基準画像（PPM形式）

## 使用方法

### 前提条件

- Python 3.x がインストールされていること
- Jupyter Notebook が利用可能であること
- Arduino IDE がインストールされていること
- Arduino Uno R4 WiFi が接続されていること

### ステップ1: 環境セットアップ

1. **依存パッケージのインストール**
   ```bash
   pip install -r requirements.txt
   ```
   または、Notebook内のCell 1-2で自動インストールされます

### ステップ2: モデルの学習とパラメータ生成

`train_L1_normalization.ipynb`を開き、以下の順序で実行します：

#### 2.1 データ準備
- **Cell 3**: 必要なライブラリをインポート
- **Cell 4**: PPMファイルを読み込み（参照画像の準備）
- **Cell 5**: 推論用データの準備

#### 2.2 モデル学習
- **Cell 6**: ニューラルネットワークの学習
  - `HIDDEN_DIM`を設定（例: 40, 80, 120, 200）
  - 学習を実行すると、`model_parameters.h`が生成されます
  - このファイルは`Arduino/AI_Model/`にコピーして使用します

#### 2.3 CSR形式への変換
- **Cell 7**: CSR形式パラメータの生成
  - `PRUNING_THRESHOLD = 0.01`（固定）で設定
  - 実行すると、`model_parameters_csr.h`が生成されます
  - このファイルは`Arduino/AI_CSR/`にコピーして使用します

#### 2.4 量子化（オプション）
- **Cell 8**: 量子化パラメータの生成
  - `USE_QUANTIZATION = True`に設定
  - 実行すると、`model_parameters_csr_quantized.h`が生成されます
  - このファイルは`Arduino/AI_CSR_Quantized/`にコピーして使用します

### ステップ3: Arduinoへのデプロイ

#### 3.1 パラメータファイルの配置

生成されたパラメータファイルを対応するArduinoフォルダにコピーします：

| 生成ファイル | コピー先 | 用途 |
|------------|---------|------|
| `model_parameters.h` | `Arduino/AI_Model/` | 密行列形式モデル |
| `model_parameters_csr.h` | `Arduino/AI_CSR/` | CSR形式モデル |
| `model_parameters_csr_quantized.h` | `Arduino/AI_CSR_Quantized/` | CSR+量子化モデル |

**注意**: 複数の次元で学習した場合、ファイル名を変更して管理してください
- 例: `model_parameters_csr40.h`, `model_parameters_csr80.h`, `model_parameters_csr120.h`

#### 3.2 Arduinoコードの設定

各Arduinoフォルダ内の`.ino`ファイルを開き、以下を確認・設定します：

1. **`HIDDEN_DIM`マクロの確認**
   ```cpp
   #define HIDDEN_DIM 40  // 学習時と同じ値に設定
   ```

2. **パラメータファイルのインクルード**
   ```cpp
   #include "model_parameters_csr.h"  // 使用するファイル名に合わせる
   ```

#### 3.3 コンパイルとアップロード

1. Arduino IDEで`.ino`ファイルを開く
2. ボードを「Arduino Uno R4 WiFi」に設定
3. シリアルポートを選択
4. 「検証」でコンパイルエラーがないか確認
5. 「アップロード」でArduinoに書き込む

### ステップ4: 実験と評価

#### 4.1 スキャン実行

Arduinoにアップロード後、スキャナーを実行してPPMファイルを生成します。

#### 4.2 MSE評価

生成されたPPMファイルを`ppm/`フォルダ内の適切なサブフォルダに保存し、MSEを計算します：

- **評価ツール**: `mse_calculator.html`をブラウザで開く
- **参照画像**: `ppm/reference_image1.ppm`を使用
- **手順**:
  1. `mse_calculator.html`をブラウザで開く
  2. 参照画像（`ppm/reference_image1.ppm`）をドラッグ&ドロップ
  3. スキャンしたPPMファイルをドラッグ&ドロップ
  4. MSE値を記録

#### 4.3 結果の記録

実験結果は`ppm/`フォルダ内に整理して保存します：
- `AI_Model.data/`: 密行列形式の結果
- `csr_40_0.01/`: CSR 40次元、閾値0.01の結果
- `csr_80_0.01/`: CSR 80次元、閾値0.01の結果
- `csr_120_0.01/`: CSR 120次元、閾値0.01の結果

### 次元変更の手順

異なる次元で実験する場合：

1. **Cell 6で`HIDDEN_DIM`を変更**（例: 40 → 80）
2. **Cell 6を実行**して学習（`model_parameters.h`を生成）
3. **Cell 7を実行**してCSRパラメータを生成（`model_parameters_csr.h`を生成）
4. **生成ファイルをリネーム**（例: `model_parameters_csr80.h`）
5. **Arduinoコードの`HIDDEN_DIM`を同じ値に設定**
6. **対応するパラメータファイルをインクルード**
7. **コンパイル・アップロードして実験**


## パラメータファイル

- `model_parameters.h`: 通常の密行列形式（全層）
- `model_parameters_csr.h`: CSR形式（2層目のみ）
- `model_parameters_csr_quantized.h`: 量子化CSR形式（2層目のみ）

## 注意事項

- `HIDDEN_DIM`は学習時とArduinoコードで一致させること
- 次元を大きくするとメモリ使用量が増加するため、Arduinoの制約を確認
- 量子化はCSR形式のパラメータに対して適用
- **プルーニング閾値は0.01で固定**（Cell 7で`PRUNING_THRESHOLD = 0.01`を設定）

## 実験の進め方

### 1. モデルの学習とパラメータ生成

各次元（40, 80, 120など）で以下の手順を実行します：

1. **Cell 6で`HIDDEN_DIM`を設定**してモデルを学習
   - 例: `HIDDEN_DIM = 40` → `model_parameters.h`を生成
2. **Cell 7でCSR形式パラメータを生成**
   - `PRUNING_THRESHOLD = 0.01`（固定）
   - 例: `model_parameters_csr.h`を生成
3. **生成ファイルをリネーム**して管理
   - 例: `model_parameters_csr40.h`, `model_parameters_csr80.h`, `model_parameters_csr120.h`

### 2. Arduinoへのデプロイと実験

1. **パラメータファイルをArduinoフォルダにコピー**
   - `model_parameters.h` → `Arduino/AI_Model/`
   - `model_parameters_csr40.h`など → `Arduino/AI_CSR/`
2. **Arduinoコードの設定**
   - `HIDDEN_DIM`マクロを学習時と同じ値に設定
   - 対応するパラメータファイルをインクルード
3. **コンパイル・アップロード**
4. **スキャン実行**してPPMファイルを生成

### 3. MSE評価と結果の記録

1. **MSE評価**
   - `mse_calculator.html`をブラウザで開く
   - 参照画像（`ppm/reference_image1.ppm`）をドラッグ&ドロップ
   - スキャンしたPPMファイルをドラッグ&ドロップ
   - MSE値を記録

2. **結果の保存**
   - 各実験結果を`ppm/`フォルダ内の適切なサブフォルダに保存
   - `AI_Model.data/`: 密行列形式の結果
   - `csr_40_0.01/`: CSR 40次元の結果
   - `csr_80_0.01/`: CSR 80次元の結果
   - `csr_120_0.01/`: CSR 120次元の結果

## 実験結果


### AI_Model（密行列形式、40次元）

| ファイル | MSE |
|---------|-----|
| nn1.ppm | 484.04 |
| nn2.ppm | 713.74 |
| nn3.ppm | 733.93 |
| nn4.ppm | 1559.96 |
| nn5.ppm | 782.33 |
| nn6.ppm | 715.63 |
| nn7.ppm | 523.63 |
| nn8.ppm | 792.85 |
| nn9.ppm | 905.85 |
| nn10.ppm | 882.15 |

- **最小値**: 484.04
- **最大値**: 1559.96
- **平均値**: 730.13


### CSR_model（40次元、プルーニング閾値0.01）

| ファイル | MSE |
|---------|-----|
| csr1.ppm | 600.00 |
| csr2.ppm | 517.48 |
| csr3.ppm | 1070.74 |
| csr4.ppm | 659.04 |

- **最小値**: -
- **最大値**: -
- **平均値**: -

**補足**: .hファイル作成時間 -


### CSR_model（80次元、プルーニング閾値0.01）

| ファイル | MSE |
|---------|-----|
| 1.ppm | 644.59 |
| 2.ppm | 459.37 |
| 3.ppm | 361.33 |
| 4.ppm | 225.19 |
| 5.ppm | 729.26 |
| 6.ppm | 408.15 |
| 7.ppm | 380.59 |
| 8.ppm | 499.85 |
| 9.ppm | 437.44 |
| 10.ppm | 472.85 |

- **最小値**: 225.19
- **最大値**: 729.26
- **平均値**: 464.86

**補足**: .hファイル作成時間 14.3秒


### CSR_model（120次元、プルーニング閾値0.01）

- **最小値**: -
- **最大値**: -
- **平均値**: -

**補足**: .hファイル作成時間 15.1秒

実験結果を記録中...







