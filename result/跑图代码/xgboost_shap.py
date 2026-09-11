import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import xgboost as xgb

# ==================== 中文字体全局配置 ====================
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号


def set_chinese_font():
  import matplotlib.font_manager as fm

  system_fonts = [f.name for f in fm.fontManager.ttflist]
  preferred_fonts = [
      'SimSun',
      'Arial Unicode MS',
      'WenQuanYi Micro Hei',
      'STHeiti',
  ]
  for font in preferred_fonts:
    if font in system_fonts:
      plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
      print(f'已成功配置中文字体: {font}')
      return
  print('未找到标准中文字体，将使用默认字体。')


set_chinese_font()
# ========================================================

# 1. 数据加载与预处理
print('正在加载数据...')
df_four = pd.read_csv('four.csv')
df_gua = pd.read_csv('gua.csv')
df_mix = pd.read_csv('mixing_scores.csv')

V_raw = df_mix['混合度'].values
Q_raw = df_four['活力度'].values

# 计算全样本平均数
mean_V = np.mean(V_raw)
mean_Q = np.mean(Q_raw)

# 筛选条件：活力度 > 平均数 且 界面品质 < 平均数
mask = (V_raw > mean_V) & (Q_raw < mean_Q)

# 提取符合条件的子集
V = V_raw[mask]
Q = Q_raw[mask]
X = df_four.loc[
    mask, [col for col in df_four.columns if col != '活力度']
].reset_index(drop=True)

print(
    f'筛选后样本数量: {len(V)} (占总样本 {len(V_raw)} 的'
    f' {len(V)/len(V_raw)*100:.2f}%)'
)

# 计算不配得性 U = ln((1+V)/(1+Q))
U = np.log((1 + V) / (1 + Q))

# 2. 训练 XGBoost 回归模型
print('正在训练 XGBoost 模型...')
model = xgb.XGBRegressor(
    n_estimators=150,
    learning_rate=0.08,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
)
model.fit(X, U)

# 3. 使用兼容高版本 XGBoost 的通用 Explainer 计算 SHAP 值
print('正在计算 SHAP 值...')
explainer = shap.Explainer(model.predict, X)
shap_values = explainer(X)
shap_val_arr = shap_values.values

# 提取特征重要性排序
mean_abs_shap = np.abs(shap_val_arr).mean(axis=0)
importance_df = pd.DataFrame(
    {'Feature': X.columns, 'Mean_Abs_SHAP': mean_abs_shap}
).sort_values(by='Mean_Abs_SHAP', ascending=False)

print('\n--- 特征重要性排序 (Mean Absolute SHAP) ---')
print(importance_df.to_string(index=False))

# 4. 绘制并保存 SHAP 可视化图表
# 4.1 SHAP 总览蜂群图
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_val_arr, X, show=False)
plt.title(
    '不配得性 (U) 的 SHAP 特征影响总览图 (筛选子集)', fontsize=14, pad=15
)
plt.tight_layout()
plt.savefig('shap_summary_filtered_6.png', dpi=300)
plt.close()
print('已生成: shap_summary_filtered_6.png')

# 获取最重要的两个特征 A 和 B
top_feature_1 = importance_df.iloc[0]['Feature']
top_feature_2 = importance_df.iloc[1]['Feature']

# 4.2 特征依赖与交互图
plt.figure(figsize=(8, 5))
shap.dependence_plot(
    top_feature_1,
    shap_val_arr,
    X,
    interaction_index=top_feature_2,
    show=False,
)
plt.title(
    f'SHAP 依赖与交互图: {top_feature_1} (交互特征: {top_feature_2})',
    fontsize=12,
)
plt.tight_layout()
plt.savefig('shap_dependence_filtered_6.png', dpi=300)
plt.close()
print(
    f'已生成特征依赖图: shap_dependence_filtered_6.png ({top_feature_1} vs'
    f' {top_feature_2})'
)

# 4.3 特征 A 与 B 组合随 U 变化的趋势图（已改用与 SHAP 一致的红蓝 coolwarm 色阶）
plt.figure(figsize=(8, 6))
scatter = plt.scatter(
    X[top_feature_1],
    X[top_feature_2],
    c=U,
    cmap='coolwarm',
    s=80,
    alpha=0.9,
)
cbar = plt.colorbar(scatter)
cbar.set_label('不配得性 U 值大小', fontsize=11)
plt.xlabel(f'关键特征 A: {top_feature_1}', fontsize=12)
plt.ylabel(f'关键特征 B: {top_feature_2}', fontsize=12)
plt.title(
    f'随不配得性 (U) 增长的特征 A-B 组合趋势散点图\n({top_feature_1} vs'
    f' {top_feature_2})',
    fontsize=13,
)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('feature_combination_trend_6.png', dpi=300)
plt.close()
print(
    '已生成红蓝统一色阶的关键特征组合趋势图: feature_combination_trend_6.png'
    f' ({top_feature_1} 和 {top_feature_2})'
)