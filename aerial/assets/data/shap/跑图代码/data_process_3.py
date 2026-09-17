import numpy as np
import pandas as pd

# 读取Excel文件（兼顾多级表头或标准表头，若有两三行表头可设置 header=[0, 1, 2] 或通过拼接展平）
file_path = '工作表-衡复风貌区调研全量总表-2026.xlsx'

try:
  # 尝试读取多级表头并展平为单层字符串列名
  df = pd.read_excel(file_path, sheet_name=0, header=2, engine='calamine')
except Exception:
  df = pd.read_excel(file_path, sheet_name=0, header=2, engine='calamine')

# 清理列名中的前后空格
df.columns = df.columns.str.strip()


# 定义一个安全提取并转为数值列的辅助函数（支持模糊匹配或精确匹配）
def get_numeric_col(dataframe, col_name):
  # 精确匹配
  if col_name in dataframe.columns:
    return pd.to_numeric(dataframe[col_name], errors='coerce').fillna(0)

  # 模糊匹配（防止多级表头拼接后带有一些前缀或后缀）
  matched_cols = [c for c in dataframe.columns if col_name in c]
  if matched_cols:
    target_col = matched_cols[0]
    print(
        f"提示: 未找到精确列 '{col_name}'，已通过模糊匹配使用列: '{target_col}'"
    )
    return pd.to_numeric(dataframe[target_col], errors='coerce').fillna(0)
  else:
    print(
        f"提示: 表格中未找到列 '{col_name}'，已自动用 0 填充。请检查列名是否正确。"
    )
    return pd.Series(0, index=dataframe.index)


# 提取并构建计算所需的数据矩阵（将空白处统一转为数字 0）
data = pd.DataFrame()
data['有效停留空间面积(㎡)'] = get_numeric_col(df, '有效停留空间面积(㎡)')
data['可承载停留人数(人)'] = get_numeric_col(df, '可承载停留人数(人)')
data['消费型停留空间占比(%)'] = get_numeric_col(df, '消费型停留空间占比(%)')
data['遮荫率(%)'] = get_numeric_col(df, '遮荫率(%)')
data['声环境舒适度'] = get_numeric_col(df, '声环境舒适度')
data['气味环境'] = get_numeric_col(df, '气味环境')
data['视觉丰富度'] = get_numeric_col(df, '视觉丰富度')
data['历史感知度'] = get_numeric_col(df, '历史感知度')
data['路面状态'] = get_numeric_col(df, '路面状态')
data['界面开放度'] = get_numeric_col(df, '界面开放度')
data['临街互动性'] = get_numeric_col(df, '临街互动性')

# 构建最终输出的指标集合
processed_df = pd.DataFrame()
for col in data.columns:
  processed_df[col] = data[col]

# 将处理后的指标存入 gua.csv 中
processed_df.to_csv('gua.csv', index=False, encoding='utf-8-sig')
print('数据处理完成，指标已成功存入 gua.csv 中！[cite: 3]')