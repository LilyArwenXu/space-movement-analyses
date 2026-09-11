import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import seaborn as sns

# 1. 字体设置为宋体，并禁用负号乱码
plt.rcParams['font.sans-serif'] = ['SimSun', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def critic_weight(df):
  # 极差归一化处理
  norm_df = pd.DataFrame()
  for col in df.columns:
    min_val = df[col].min()
    max_val = df[col].max()
    if max_val == min_val:
      norm_df[col] = 0.0
    else:
      norm_df[col] = (df[col] - min_val) / (max_val - min_val)

  # 对比强度（标准差）
  std_vals = norm_df.std(ddof=1)

  # 冲突性指标（相关系数矩阵）
  corr_matrix = norm_df.corr()
  conflict = (1 - corr_matrix).sum(axis=1)

  # 信息量计算与权重归一化
  information_amount = std_vals * conflict
  weights = information_amount / information_amount.sum()
  return norm_df, std_vals, corr_matrix, conflict, information_amount, weights


def get_morandi_colors(n, palette):
  """根据指标数量动态适配颜色池"""
  if n <= len(palette):
    return palette[:n]
  else:
    # 若指标超过8个，利用现有色阶进行平滑插值扩展
    cmap = LinearSegmentedColormap.from_list('extended_morandi', palette)
    return [mcolors.to_hex(cmap(i / (n - 1))) for i in range(n)]


if __name__ == '__main__':
  # 读取数据（可复用于任意多指标CSV文件）
  raw_df = pd.read_csv('four.csv')
  norm_df, std, corr, conflict, info_amount, weights = critic_weight(raw_df)

  print('=== 最终计算得到的权重 ===')
  for col, w in weights.items():
    print(f'{col}: {w:.4f}')

  # ==========================================
  # 计算综合界面品质得分并写回 gua.csv
  # 公式：综合得分 = Σ (归一化指标值 * 权重)
  # ==========================================
  quality_score = 0
  for col, w in weights.items():
    quality_score += norm_df[col] * w

  # 将计算结果存入原始 DataFrame 的新列中
  raw_df['混合度'] = quality_score
  raw_df.to_csv('mixing_scores.csv', index=False, encoding='utf-8-sig')
  print('\n已成功将计算出的【界面品质】追加并保存至 mixing_scores.csv 中！')

  # 定义你提供的完整莫兰迪色阶库
  morandi_palette = [
      '#ABDBDA',
      '#5892AE',
      '#3D468C',
      '#A5A7CE',
      '#81619D',
      '#845D9E',
      '#D9AECC',
      '#B3629F',
  ]

  # 动态获取当前指标数量对应的颜色
  n_indicators = len(weights)
  bar_colors = get_morandi_colors(n_indicators, morandi_palette)

  # 热力图渐变色延续首尾过渡
  heatmap_cmap = LinearSegmentedColormap.from_list(
      'morandi_heatmap', [morandi_palette[0], morandi_palette[2]]
  )

  fig, axes = plt.subplots(1, 2, figsize=(16, 6))

  # 图1：相关系数矩阵热力图（当指标多时，调整热力图字体大小防重叠）
  annot_fontsize = 8 if n_indicators > 8 else 11
  sns.heatmap(
      corr,
      annot=True,
      cmap=heatmap_cmap,
      fmt='.2f',
      ax=axes[0],
      cbar=True,
      annot_kws={'size': annot_fontsize},
  )
  axes[0].set_title('指标间 Pearson 相关系数矩阵 (共线性分析)', fontsize=12)
  # 热力图的横纵坐标也适当旋转
  axes[0].set_xticklabels(
      axes[0].get_xticklabels(), rotation=45, ha='right', fontsize=9
  )
  axes[0].set_yticklabels(axes[0].get_yticklabels(), fontsize=9)

  # 图2：动态适配色阶的权重柱状图
  bars = axes[1].bar(weights.index, weights.values, color=bar_colors)
  axes[1].set_title('CRITIC 权重分布结果', fontsize=12)
  axes[1].set_ylabel('权重值', fontsize=11)
  axes[1].set_ylim(0, max(weights) * 1.2)

  # 旋转横坐标标签，避免文字重叠
  axes[1].set_xticks(range(len(weights.index)))
  axes[1].set_xticklabels(weights.index, rotation=45, ha='right', fontsize=10)

  # 在柱状图上方标注数值
  for bar in bars:
    height = bar.get_height()
    axes[1].annotate(
        f'{height:.3f}',
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 4),
        textcoords='offset points',
        ha='center',
        va='bottom',
        fontsize=9,
    )

  # 自动调整布局，留出底部标签空间
  plt.tight_layout()
  output_filename = 'critic_weights_analysis_2.png'
  plt.savefig(output_filename, dpi=300)
  plt.show()