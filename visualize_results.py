#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実験結果の可視化スクリプト
隠れ層次元 vs MSE平均値、隠れ層次元 vs メモリ使用量、隠れ層次元 vs コンパイル時間の3種類のグラフを生成
120次元までと600次元までの2種類を作成
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import platform

# 日本語フォントの設定（macOS用）
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'Hiragino Sans'

# 実験データの定義
data = {
    'dense': {  # 密行列形式
        'dimensions': [40, 50, 60],
        'mse_mean': [595.95, 406.93, 305.48],
        'memory_percent': [44, 56, 70],
        'compile_time': [4.303, 4.589, 4.831]
    },
    'csr': {  # CSR圧縮
        'dimensions': [40, 80, 120, 160, 200, 400, 600],
        'mse_mean': [518.58, 464.86, 620.49, 589.08, 493.35, 864.40, 670.69],
        'memory_percent': [25, 29, 32, 34, 37, 52, 67],
        'compile_time': [3.783, 4.037, 4.062, 4.042, 4.027, 4.316, 4.802]
    },
    'quantized': {  # CSR+量子化
        'dimensions': [40, 80, 120, 160, 200, 400, 600],  # MSE測定済みは120次元まで
        'mse_mean': [408.97, 270.68, 244.83, None, None, None, None],  # 160次元以降はMSE測定未実施
        'memory_percent': [24, 27, 30, 36, 36, 51, 66],  # 全次元のメモリ使用量データ
        'compile_time': [3.772, 3.809, 4.028, 4.033, 4.033, 4.307, 4.801]  # 全次元のコンパイル時間データ
    }
}

# データをフィルタリングする関数
def filter_data(data_dict, max_dim, include_memory_only=False, include_compile_time=False):
    """指定された最大次元までのデータをフィルタリング
    
    Args:
        data_dict: 元のデータ辞書
        max_dim: 最大次元
        include_memory_only: Trueの場合、MSEがNoneでもメモリデータがあれば含める（メモリグラフ用）
        include_compile_time: Trueの場合、コンパイル時間データがあれば含める（コンパイル時間グラフ用）
    """
    filtered = {}
    for key, values in data_dict.items():
        dims = []
        mse = []
        memory = []
        compile_time = []
        
        for i, d in enumerate(values['dimensions']):
            if d <= max_dim:
                if include_compile_time:
                    # コンパイル時間グラフ用：コンパイル時間データがあれば含める
                    if i < len(values.get('compile_time', [])) and values['compile_time'][i] is not None:
                        dims.append(d)
                        mse.append(values['mse_mean'][i] if i < len(values.get('mse_mean', [])) else None)
                        memory.append(values['memory_percent'][i] if i < len(values.get('memory_percent', [])) else None)
                        compile_time.append(values['compile_time'][i])
                elif include_memory_only:
                    # メモリグラフ用：メモリデータがあれば含める
                    if i < len(values['memory_percent']) and values['memory_percent'][i] is not None:
                        dims.append(d)
                        mse.append(values['mse_mean'][i] if i < len(values['mse_mean']) else None)
                        memory.append(values['memory_percent'][i])
                        compile_time.append(values['compile_time'][i] if i < len(values.get('compile_time', [])) else None)
                else:
                    # MSEグラフ用：MSEがNoneでないもののみ含める
                    if i < len(values['mse_mean']) and values['mse_mean'][i] is not None:
                        dims.append(d)
                        mse.append(values['mse_mean'][i])
                        memory.append(values['memory_percent'][i] if i < len(values['memory_percent']) else None)
                        compile_time.append(values['compile_time'][i] if i < len(values.get('compile_time', [])) else None)
        
        filtered[key] = {
            'dimensions': dims,
            'mse_mean': mse,
            'memory_percent': memory,
            'compile_time': compile_time
        }
    return filtered

# グラフ作成関数
def create_graphs(max_dimension, suffix):
    """指定された最大次元までのグラフを作成"""
    # MSEグラフ用：MSEが測定されているもののみ
    filtered_data_mse = filter_data(data, max_dimension, include_memory_only=False)
    # メモリグラフ用：メモリデータがあれば含める
    filtered_data_memory = filter_data(data, max_dimension, include_memory_only=True)
    # コンパイル時間グラフ用：コンパイル時間データがあれば含める
    filtered_data_compile = filter_data(data, max_dimension, include_compile_time=True)
    
    # 図1: 隠れ層次元 vs MSE平均値
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(filtered_data_mse['dense']['dimensions'], filtered_data_mse['dense']['mse_mean'], 
             marker='o', linewidth=2, markersize=8, label='密行列形式（非圧縮）', color='blue')
    ax1.plot(filtered_data_mse['csr']['dimensions'], filtered_data_mse['csr']['mse_mean'], 
             marker='s', linewidth=2, markersize=8, label='CSR圧縮', color='green')
    ax1.plot(filtered_data_mse['quantized']['dimensions'], filtered_data_mse['quantized']['mse_mean'], 
             marker='^', linewidth=2, markersize=8, label='CSR+量子化', color='orange')
    
    ax1.set_xlabel('隠れ層次元', fontsize=12, fontweight='bold')
    ax1.set_ylabel('MSE平均値', fontsize=12, fontweight='bold')
    ax1.set_title('隠れ層次元とMSE平均値の関係', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11, loc='lower right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(30, max_dimension + 50)
    
    # 背景を透明に
    fig1.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    
    plt.tight_layout()
    filename = f'mse_vs_dimension_{suffix}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"グラフを保存しました: {filename}")
    plt.close()
    
    # 図2: 隠れ層次元 vs メモリ使用量（%）
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(filtered_data_memory['dense']['dimensions'], filtered_data_memory['dense']['memory_percent'], 
             marker='o', linewidth=2, markersize=8, label='密行列形式（非圧縮）', color='blue')
    ax2.plot(filtered_data_memory['csr']['dimensions'], filtered_data_memory['csr']['memory_percent'], 
             marker='s', linewidth=2, markersize=8, label='CSR圧縮', color='green')
    ax2.plot(filtered_data_memory['quantized']['dimensions'], filtered_data_memory['quantized']['memory_percent'], 
             marker='^', linewidth=2, markersize=8, label='CSR+量子化', color='orange')
    
    # メモリ上限（32KB = 100%）の線を追加
    ax2.axhline(y=100, color='r', linestyle='--', linewidth=2, label='メモリ上限（32KB）', alpha=0.7)
    
    ax2.set_xlabel('隠れ層次元', fontsize=12, fontweight='bold')
    ax2.set_ylabel('メモリ使用量（%）', fontsize=12, fontweight='bold')
    ax2.set_title('隠れ層次元とメモリ使用量の関係', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11, loc='lower right')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 110)
    ax2.set_xlim(30, max_dimension + 50)
    
    # 背景を透明に
    fig2.patch.set_facecolor('white')
    ax2.set_facecolor('white')
    
    plt.tight_layout()
    filename = f'memory_vs_dimension_{suffix}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"グラフを保存しました: {filename}")
    plt.close()
    
    # 図3: 隠れ層次元 vs コンパイル時間（秒）
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.plot(filtered_data_compile['dense']['dimensions'], filtered_data_compile['dense']['compile_time'], 
             marker='o', linewidth=2, markersize=8, label='密行列形式（非圧縮）', color='blue')
    ax3.plot(filtered_data_compile['csr']['dimensions'], filtered_data_compile['csr']['compile_time'], 
             marker='s', linewidth=2, markersize=8, label='CSR圧縮', color='green')
    ax3.plot(filtered_data_compile['quantized']['dimensions'], filtered_data_compile['quantized']['compile_time'], 
             marker='^', linewidth=2, markersize=8, label='CSR+量子化', color='orange')
    
    ax3.set_xlabel('隠れ層次元', fontsize=12, fontweight='bold')
    ax3.set_ylabel('コンパイル時間（秒）', fontsize=12, fontweight='bold')
    ax3.set_title('隠れ層次元とコンパイル時間の関係', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=11, loc='lower right')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(30, max_dimension + 50)
    
    # 背景を透明に
    fig3.patch.set_facecolor('white')
    ax3.set_facecolor('white')
    
    plt.tight_layout()
    filename = f'compile_time_vs_dimension_{suffix}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"グラフを保存しました: {filename}")
    plt.close()

# 120次元までのグラフを作成
print("120次元までのグラフを生成中...")
create_graphs(120, '120dim')

# 600次元までのグラフを作成
print("\n600次元までのグラフを生成中...")
create_graphs(600, '600dim')

print("\nすべてのグラフを生成しました！")
print("生成されたファイル:")
print("  - mse_vs_dimension_120dim.png")
print("  - memory_vs_dimension_120dim.png")
print("  - compile_time_vs_dimension_120dim.png")
print("  - mse_vs_dimension_600dim.png")
print("  - memory_vs_dimension_600dim.png")
print("  - compile_time_vs_dimension_600dim.png")
