import pandas as pd
import numpy as np

# 读取Excel文件（表格真实表头位于第3行，即 header=2）
file_path = '工作表-衡复风貌区调研全量总表-2026.xlsx'


df = pd.read_excel(file_path, sheet_name=0, header=2,engine='calamine')

# 清理列名中的前后空格
df.columns = df.columns.str.strip()

# 提取并构建计算所需的数据矩阵（将空白处统一转为数字 0）
data = pd.DataFrame()
data['行人样本数'] = pd.to_numeric(df.get('行人样本数'), errors='coerce').fillna(0)
data['行为集群数'] = pd.to_numeric(df.get('行为集群数'), errors='coerce').fillna(0)
data['集聚人数'] = pd.to_numeric(df.get('集聚人数'), errors='coerce').fillna(0)
data['有效停留空间面积'] = pd.to_numeric(df.get('有效停留空间面积(㎡)'), errors='coerce').fillna(0)

# 构建最终输出的四个指标
processed_df = pd.DataFrame()
processed_df['人数'] = data['行人样本数']
processed_df['行人集群数'] = data['行为集群数']

# 1. 停留密度 = 行人样本数 / 有效停留空间面积 (若面积为0则记为0)
processed_df['停留密度'] = np.where(
    data['有效停留空间面积'] == 0, 
    0, 
    data['行人样本数'] / data['有效停留空间面积']
)

# 2. 聚集比例 = 集聚人数 / 行人样本数 (若样本数为0则记为0)
processed_df['聚集比例'] = np.where(
    data['行人样本数'] == 0, 
    0, 
    data['集聚人数'] / data['行人样本数']
)

# 将处理后的四个指标存入单独的 four.csv 中
processed_df.to_csv('four.csv', index=False, encoding='utf-8-sig')
print("数据处理完成，四个指标已成功存入 four.csv 中！")