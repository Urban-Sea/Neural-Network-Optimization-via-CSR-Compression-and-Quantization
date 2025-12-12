#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実験結果の可視化スクリプト
README.mdに記載されている実験結果をグラフ化します。
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import platform
import matplotlib.font_manager as fm

# 日本語フォントの設定
def setup_japanese_font():
    """日本語フォントを設定する（フォントパスを直接指定）"""
    system = platform.system()
    import os
    
    if system == 'Darwin':  # macOS
        # macOSのヒラギノフォントのパスを直接指定
        font_paths = [
            '/System/Library/Fonts/ヒラギノ角ゴシック W0.ttc',
            '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
            '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # フォントプロパティを直接設定
                    prop = fm.FontProperties(fname=font_path)
                    font_name = prop.get_name()
                    rcParams['font.family'] = font_name
                    # フォントパスも設定（より確実な方法）
                    rcParams['font.sans-serif'] = [font_name, 'Hiragino Sans', 'AppleGothic', 'Arial Unicode MS']
                    print(f"日本語フォントを設定しました: {font_name} ({font_path})")
                    return
                except Exception as e:
                    print(f"フォント設定エラー ({font_path}): {e}")
                    continue
        
        # フォールバック: フォント名で設定
        japanese_fonts = ['Hiragino Sans', 'AppleGothic']
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        for font in japanese_fonts:
            if font in available_fonts:
                rcParams['font.family'] = font
                rcParams['font.sans-serif'] = [font, 'Hiragino Sans', 'AppleGothic']
                print(f"日本語フォントを設定しました（フォント名）: {font}")
                return
        
        print("警告: 日本語フォントが見つかりません。デフォルトフォントを使用します。")
        rcParams['font.family'] = 'DejaVu Sans'
    
    elif system == 'Windows':
        rcParams['font.family'] = 'MS Gothic'
        rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
        print("日本語フォントを設定しました: MS Gothic")
    
    else:  # Linux
        japanese_fonts = ['Noto Sans CJK JP', 'IPAexGothic', 'IPAPGothic']
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        for font in japanese_fonts:
            if font in available_fonts:
                rcParams['font.family'] = font
                rcParams['font.sans-serif'] = [font]
                print(f"日本語フォントを設定しました: {font}")
                return
        print("警告: 日本語フォントが見つかりません。デフォルトフォントを使用します。")
        rcParams['font.family'] = 'DejaVu Sans'

# 日本語フォントを設定
setup_japanese_font()

# 負の符号が正しく表示されるように設定
rcParams['axes.unicode_minus'] = False

# 日本語フォントプロパティを取得（全グラフで使用）
def get_japanese_font():
    """日本語フォントのFontPropertiesを取得"""
    system = platform.system()
    import os
    
    if system == 'Darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/ヒラギノ角ゴシック W0.ttc',
            '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                return fm.FontProperties(fname=font_path)
        # フォールバック
        return fm.FontProperties(family='Hiragino Sans')
    elif system == 'Windows':
        return fm.FontProperties(family='MS Gothic')
    else:
        return fm.FontProperties(family='Noto Sans CJK JP')

japanese_font_prop = get_japanese_font()

# 実験データの定義
data = {
    'dense': {  # 密行列形式
        'dimensions': [40, 50, 60],
        'mse_mean': [595.95, 406.93, 305.48],
        'mse_min': [277.67, 231.11, 138.00],
        'mse_max': [792.85, 535.59, 423.22],
        'memory_bytes': [14524, 18444, 23164],
        'memory_percent': [44, 56, 70],
        'compile_time': [4.303, 4.589, 4.831]
    },
    'csr': {  # CSR圧縮
        'dimensions': [40, 80, 120, 160, 200, 400, 600],
        'mse_mean': [518.58, 464.86, 620.49, 589.08, 493.35, 864.40, 670.69],
        'mse_min': [324.00, 225.19, 295.37, 295.52, 291.41, 390.89, 253.44],
        'mse_max': [692.37, 729.26, 814.33, 1179.59, 979.85, 1978.81, 2143.81],
        'memory_bytes': [8488, 9508, 10520, 11332, 12332, 17204, 21976],
        'memory_percent': [25, 29, 32, 34, 37, 52, 67],
        'compile_time': [3.783, 4.037, 4.062, 4.042, 4.027, 4.316, 4.802]
    },
    'quantized': {  # CSR+量子化
        'dimensions': [40, 80, 120],
        'mse_mean': [408.97, 270.68, 244.83],
        'mse_min': [278.78, 200.22, 169.37],
        'mse_max': [588.15, 323.96, 310.63],
        'memory_bytes': [8160, 9148, 10132],
        'memory_percent': [24, 27, 30],
        'compile_time': [3.772, 3.809, 4.028]
    }
}

# グラフのスタイル設定
plt.style.use('seaborn-v0_8-darkgrid')
fig_size = (12, 8)

# 図1: 隠れ層次元 vs MSE平均値
fig1, ax1 = plt.subplots(figsize=fig_size)
ax1.plot(data['dense']['dimensions'], data['dense']['mse_mean'], 
         marker='o', linewidth=2, markersize=8, label='密行列形式（非圧縮）', color='#1f77b4')
ax1.plot(data['csr']['dimensions'], data['csr']['mse_mean'], 
         marker='s', linewidth=2, markersize=8, label='CSR圧縮', color='#ff7f0e')
ax1.plot(data['quantized']['dimensions'], data['quantized']['mse_mean'], 
         marker='^', linewidth=2, markersize=8, label='CSR+量子化', color='#2ca02c')

ax1.set_xlabel('隠れ層次元', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax1.set_ylabel('MSE平均値', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax1.set_title('隠れ層次元とMSE平均値の関係', fontsize=14, fontweight='bold', fontproperties=japanese_font_prop)
ax1.legend(prop=japanese_font_prop, fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(30, 650)

plt.tight_layout()
plt.savefig('mse_vs_dimension.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: mse_vs_dimension.png")
plt.close()

# 図2: 隠れ層次元 vs メモリ使用量（%）
fig2, ax2 = plt.subplots(figsize=fig_size)
ax2.plot(data['dense']['dimensions'], data['dense']['memory_percent'], 
         marker='o', linewidth=2, markersize=8, label='密行列形式（非圧縮）', color='#1f77b4')
ax2.plot(data['csr']['dimensions'], data['csr']['memory_percent'], 
         marker='s', linewidth=2, markersize=8, label='CSR圧縮', color='#ff7f0e')
ax2.plot(data['quantized']['dimensions'], data['quantized']['memory_percent'], 
         marker='^', linewidth=2, markersize=8, label='CSR+量子化', color='#2ca02c')

# メモリ上限（32KB = 100%）の線を追加
ax2.axhline(y=100, color='r', linestyle='--', linewidth=2, label='メモリ上限（32KB）', alpha=0.7)

ax2.set_xlabel('隠れ層次元', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax2.set_ylabel('メモリ使用量（%）', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax2.set_title('隠れ層次元とメモリ使用量の関係', fontsize=14, fontweight='bold', fontproperties=japanese_font_prop)
ax2.legend(prop=japanese_font_prop, fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 110)
ax2.set_xlim(30, 650)

plt.tight_layout()
plt.savefig('memory_vs_dimension.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: memory_vs_dimension.png")
plt.close()

# 図3: 隠れ層次元 vs コンパイル時間
fig3, ax3 = plt.subplots(figsize=fig_size)
ax3.plot(data['dense']['dimensions'], data['dense']['compile_time'], 
         marker='o', linewidth=2, markersize=8, label='密行列形式（非圧縮）', color='#1f77b4')
ax3.plot(data['csr']['dimensions'], data['csr']['compile_time'], 
         marker='s', linewidth=2, markersize=8, label='CSR圧縮', color='#ff7f0e')
ax3.plot(data['quantized']['dimensions'], data['quantized']['compile_time'], 
         marker='^', linewidth=2, markersize=8, label='CSR+量子化', color='#2ca02c')

ax3.set_xlabel('隠れ層次元', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax3.set_ylabel('コンパイル時間（秒）', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax3.set_title('隠れ層次元とコンパイル時間の関係', fontsize=14, fontweight='bold', fontproperties=japanese_font_prop)
ax3.legend(prop=japanese_font_prop, fontsize=11)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(30, 650)

plt.tight_layout()
plt.savefig('compile_time_vs_dimension.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: compile_time_vs_dimension.png")
plt.close()

# 図4: 同一次元での圧縮手法比較（40次元）
fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(14, 6))

# 40次元での比較
dim_40 = ['密行列形式', 'CSR圧縮', 'CSR+量子化']
mse_40 = [595.95, 518.58, 408.97]
memory_40 = [44, 25, 24]

x_pos = np.arange(len(dim_40))
width = 0.35

bars1 = ax4a.bar(x_pos - width/2, mse_40, width, label='MSE平均値', color='#3498db', alpha=0.8)
ax4a.set_xlabel('圧縮手法（40次元）', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)
ax4a.set_ylabel('MSE平均値', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)
ax4a.set_title('40次元での圧縮手法別MSE比較', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax4a.set_xticks(x_pos)
ax4a.set_xticklabels(dim_40, rotation=15, ha='right', fontproperties=japanese_font_prop)
ax4a.grid(True, alpha=0.3, axis='y')

# バーの上に値を表示
for i, v in enumerate(mse_40):
    ax4a.text(i, v + 10, f'{v:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold', fontproperties=japanese_font_prop)

bars2 = ax4b.bar(x_pos - width/2, memory_40, width, label='メモリ使用量', color='#e74c3c', alpha=0.8)
ax4b.set_xlabel('圧縮手法（40次元）', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)
ax4b.set_ylabel('メモリ使用量（%）', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)
ax4b.set_title('40次元での圧縮手法別メモリ使用量比較', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax4b.set_xticks(x_pos)
ax4b.set_xticklabels(dim_40, rotation=15, ha='right', fontproperties=japanese_font_prop)
ax4b.grid(True, alpha=0.3, axis='y')
ax4b.set_ylim(0, 50)

# バーの上に値を表示
for i, v in enumerate(memory_40):
    ax4b.text(i, v + 1, f'{v}%', ha='center', va='bottom', fontsize=10, fontweight='bold', fontproperties=japanese_font_prop)

plt.tight_layout()
plt.savefig('comparison_40dim.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: comparison_40dim.png")
plt.close()

# 図5: 同一次元での圧縮手法比較（80次元）
fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(14, 6))

# 80次元での比較（密行列形式は70次元でコンパイルエラーなので、CSRとCSR+量子化のみ）
dim_80 = ['CSR圧縮', 'CSR+量子化']
mse_80 = [464.86, 270.68]
memory_80 = [29, 27]

x_pos = np.arange(len(dim_80))
width = 0.5

bars1 = ax5a.bar(x_pos, mse_80, width, color='#3498db', alpha=0.8)
ax5a.set_xlabel('圧縮手法（80次元）', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)
ax5a.set_ylabel('MSE平均値', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)
ax5a.set_title('80次元での圧縮手法別MSE比較', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax5a.set_xticks(x_pos)
ax5a.set_xticklabels(dim_80, rotation=15, ha='right', fontproperties=japanese_font_prop)
ax5a.grid(True, alpha=0.3, axis='y')

# バーの上に値を表示
for i, v in enumerate(mse_80):
    ax5a.text(i, v + 10, f'{v:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold', fontproperties=japanese_font_prop)

bars2 = ax5b.bar(x_pos, memory_80, width, color='#e74c3c', alpha=0.8)
ax5b.set_xlabel('圧縮手法（80次元）', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)
ax5b.set_ylabel('メモリ使用量（%）', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)
ax5b.set_title('80次元での圧縮手法別メモリ使用量比較', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax5b.set_xticks(x_pos)
ax5b.set_xticklabels(dim_80, rotation=15, ha='right', fontproperties=japanese_font_prop)
ax5b.grid(True, alpha=0.3, axis='y')
ax5b.set_ylim(0, 35)

# バーの上に値を表示
for i, v in enumerate(memory_80):
    ax5b.text(i, v + 1, f'{v}%', ha='center', va='bottom', fontsize=10, fontweight='bold', fontproperties=japanese_font_prop)

plt.tight_layout()
plt.savefig('comparison_80dim.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: comparison_80dim.png")
plt.close()

# 図6: MSEの範囲（最小値〜最大値）をエラーバーで表示
fig6, ax6 = plt.subplots(figsize=fig_size)

# 40次元での比較
dimensions_40 = ['密行列形式\n(40次元)', 'CSR圧縮\n(40次元)', 'CSR+量子化\n(40次元)']
mse_mean_40 = [595.95, 518.58, 408.97]
mse_min_40 = [277.67, 324.00, 278.78]
mse_max_40 = [792.85, 692.37, 588.15]
mse_error_lower_40 = [mse_mean_40[i] - mse_min_40[i] for i in range(len(mse_mean_40))]
mse_error_upper_40 = [mse_max_40[i] - mse_mean_40[i] for i in range(len(mse_mean_40))]

x_pos = np.arange(len(dimensions_40))
bars = ax6.bar(x_pos, mse_mean_40, yerr=[mse_error_lower_40, mse_error_upper_40], 
               capsize=10, alpha=0.7, color=['#1f77b4', '#ff7f0e', '#2ca02c'])

ax6.set_xlabel('圧縮手法', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax6.set_ylabel('MSE', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax6.set_title('40次元での圧縮手法別MSE比較（最小値〜最大値）', fontsize=14, fontweight='bold', fontproperties=japanese_font_prop)
ax6.set_xticks(x_pos)
ax6.set_xticklabels(dimensions_40, fontproperties=japanese_font_prop)
ax6.grid(True, alpha=0.3, axis='y')

# バーの上に平均値を表示
for i, v in enumerate(mse_mean_40):
    ax6.text(i, v + 50, f'平均: {v:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold', fontproperties=japanese_font_prop)

plt.tight_layout()
plt.savefig('mse_comparison_40dim_with_range.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: mse_comparison_40dim_with_range.png")
plt.close()

# 図7: メモリ使用量とMSEのトレードオフ（40次元）
fig7, ax7 = plt.subplots(figsize=(10, 8))

methods_40 = ['密行列形式', 'CSR圧縮', 'CSR+量子化']
memory_40 = [44, 25, 24]
mse_40 = [595.95, 518.58, 408.97]
colors_40 = ['#1f77b4', '#ff7f0e', '#2ca02c']

for i, method in enumerate(methods_40):
    ax7.scatter(memory_40[i], mse_40[i], s=300, color=colors_40[i], alpha=0.7, label=method)
    ax7.annotate(method, (memory_40[i], mse_40[i]), 
                xytext=(5, 5), textcoords='offset points', fontsize=11, fontweight='bold', fontproperties=japanese_font_prop)

ax7.set_xlabel('メモリ使用量（%）', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax7.set_ylabel('MSE平均値', fontsize=12, fontweight='bold', fontproperties=japanese_font_prop)
ax7.set_title('40次元でのメモリ使用量とMSEのトレードオフ', fontsize=14, fontweight='bold', fontproperties=japanese_font_prop)
ax7.grid(True, alpha=0.3)
ax7.invert_xaxis()  # メモリ使用量が少ない方が良いので、X軸を反転

plt.tight_layout()
plt.savefig('memory_mse_tradeoff_40dim.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: memory_mse_tradeoff_40dim.png")
plt.close()

# 図8: 全データの統合比較（MSE vs 次元、3手法）
fig8, ax8 = plt.subplots(figsize=fig_size)

# 密行列形式
ax8.plot(data['dense']['dimensions'], data['dense']['mse_mean'], 
         marker='o', linewidth=2.5, markersize=10, label='密行列形式（非圧縮）', 
         color='#1f77b4', linestyle='-', markerfacecolor='white', markeredgewidth=2)

# CSR圧縮
ax8.plot(data['csr']['dimensions'], data['csr']['mse_mean'], 
         marker='s', linewidth=2.5, markersize=10, label='CSR圧縮', 
         color='#ff7f0e', linestyle='-', markerfacecolor='white', markeredgewidth=2)

# CSR+量子化
ax8.plot(data['quantized']['dimensions'], data['quantized']['mse_mean'], 
         marker='^', linewidth=2.5, markersize=10, label='CSR+量子化', 
         color='#2ca02c', linestyle='-', markerfacecolor='white', markeredgewidth=2)

ax8.set_xlabel('隠れ層次元', fontsize=13, fontweight='bold', fontproperties=japanese_font_prop)
ax8.set_ylabel('MSE平均値', fontsize=13, fontweight='bold', fontproperties=japanese_font_prop)
ax8.set_title('圧縮手法別の隠れ層次元とMSE平均値の関係', fontsize=15, fontweight='bold', fontproperties=japanese_font_prop)
ax8.legend(prop=japanese_font_prop, fontsize=12, loc='best')
ax8.grid(True, alpha=0.3, linestyle='--')
ax8.set_xlim(30, 650)

plt.tight_layout()
plt.savefig('mse_all_methods.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: mse_all_methods.png")
plt.close()

# 図9: メモリ使用量の比較（全手法）
fig9, ax9 = plt.subplots(figsize=fig_size)

ax9.plot(data['dense']['dimensions'], data['dense']['memory_percent'], 
         marker='o', linewidth=2.5, markersize=10, label='密行列形式（非圧縮）', 
         color='#1f77b4', linestyle='-', markerfacecolor='white', markeredgewidth=2)
ax9.plot(data['csr']['dimensions'], data['csr']['memory_percent'], 
         marker='s', linewidth=2.5, markersize=10, label='CSR圧縮', 
         color='#ff7f0e', linestyle='-', markerfacecolor='white', markeredgewidth=2)
ax9.plot(data['quantized']['dimensions'], data['quantized']['memory_percent'], 
         marker='^', linewidth=2.5, markersize=10, label='CSR+量子化', 
         color='#2ca02c', linestyle='-', markerfacecolor='white', markeredgewidth=2)

ax9.axhline(y=100, color='r', linestyle='--', linewidth=2, label='メモリ上限（32KB）', alpha=0.7)

ax9.set_xlabel('隠れ層次元', fontsize=13, fontweight='bold', fontproperties=japanese_font_prop)
ax9.set_ylabel('メモリ使用量（%）', fontsize=13, fontweight='bold', fontproperties=japanese_font_prop)
ax9.set_title('圧縮手法別の隠れ層次元とメモリ使用量の関係', fontsize=15, fontweight='bold', fontproperties=japanese_font_prop)
ax9.legend(prop=japanese_font_prop, fontsize=12, loc='best')
ax9.grid(True, alpha=0.3, linestyle='--')
ax9.set_ylim(0, 110)
ax9.set_xlim(30, 650)

plt.tight_layout()
plt.savefig('memory_all_methods.png', dpi=300, bbox_inches='tight')
print("グラフを保存しました: memory_all_methods.png")
plt.close()

print("\nすべてのグラフを生成しました！")
print("生成されたファイル:")
print("  - mse_vs_dimension.png")
print("  - memory_vs_dimension.png")
print("  - compile_time_vs_dimension.png")
print("  - comparison_40dim.png")
print("  - comparison_80dim.png")
print("  - mse_comparison_40dim_with_range.png")
print("  - memory_mse_tradeoff_40dim.png")
print("  - mse_all_methods.png")
print("  - memory_all_methods.png")
