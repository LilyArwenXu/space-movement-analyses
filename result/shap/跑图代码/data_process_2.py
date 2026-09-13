import numpy as np
import pandas as pd


def calculate_shannon_entropy(df, columns):
  """计算归一化香农熵混合度 H_d = -Σ(p_k * ln p_k) / ln K_d"""
  sub_df = df[columns].fillna(0).apply(pd.to_numeric, errors='coerce').fillna(0)
  total_freq = sub_df.sum(axis=1)

  h_values = []
  for idx in range(len(sub_df)):
    tot = total_freq.iloc[idx]
    k = len(columns)

    if tot == 0 or k <= 1:
      h_values.append(0.0)
      continue

    pk = sub_df.iloc[idx] / tot
    pk_ln_pk = np.where(pk > 0, pk * np.log(pk), 0.0)
    sum_val = np.sum(pk_ln_pk)

    h = -sum_val / np.log(k)
    h_values.append(h)

  return h_values


def process_indicator_data(input_file_path, output_csv_path='mixing_scores.csv'):
  # 读取Excel文件（指定第3行作为表头）
  try:
    df = pd.read_excel(
        input_file_path, sheet_name=0, header=2, engine='calamine'
    )
  except Exception:
    df = pd.read_excel(input_file_path, sheet_name=0, header=2)

  # 清理列名空格
  df.columns = df.columns.str.strip()

  dim_indicators = {
      '年龄混合度': ['幼年人数', '青年人数', '中年人数', '老年人数'],
      '活动丰富度': [
          '观察人数',
          '光顾人数',
          '等待人数',
          '打卡人数',
          '社交人数',
          '争吵/纠纷人数',
          '饮食人数',
          '休憩人数',
          '避雨/遮阳人数',
          '工作人数',
          '娱乐人数',
          '运动人数',
          '照看人数',
          '整理人数',
      ],
      '姿态丰富度': ['落座人数', '站立/倚靠人数'],
      '社交状态混合度': ['独立人数', '集聚人数'],
      '身份倾向混合度': ['居民指数', '游客指数'],
  }

  result_df = pd.DataFrame()
  for dim_name, cols in dim_indicators.items():
    # 检查指标是否存在：指标有缺失则跳过
    missing_cols = [c for c in cols if c not in df.columns]
    if missing_cols:
      print(f"提示：跳过维度 '{dim_name}'，因为缺少以下指标列: {missing_cols}")
      continue

    # 计算香农熵混合度
    h_vals = calculate_shannon_entropy(df, cols)

    # 全域极差标准化：z = (x - min) / (max - min)，常量指标记0
    h_arr = np.array(h_vals, dtype=float)
    min_val = np.min(h_arr)
    max_val = np.max(h_arr)

    if max_val == min_val:
      z_vals = np.zeros_like(h_arr)
    else:
      z_vals = (h_arr - min_val) / (max_val - min_val)

    result_df[dim_name] = z_vals

  # 存入 CSV 文件
  result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
  print(f"数据处理完成，结果已成功存入: {output_csv_path}")
  return result_df


if __name__ == '__main__':
  # 请将文件名替换为你的实际表格路径
  process_indicator_data('工作表-衡复风貌区调研全量总表-2026.xlsx')