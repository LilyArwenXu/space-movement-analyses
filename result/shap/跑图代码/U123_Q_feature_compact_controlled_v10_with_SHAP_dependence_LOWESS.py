# -*- coding: utf-8 -*-
"""
Q底层指标 → U1/U2/U3：控制干扰变量后的精简分析版
=================================================

研究目标
--------
研究界面品质 Q 的底层指标（及其组合）分别与：
    U1 = ln(1+V) - ln(1+Q)
    U2 = ln(1+M) - ln(1+Q)
    U3 = ln(1+V) - ln(1+M)
之间的关系。

本版做了两个重要调整：
1. 控制不属于研究重点、但会强烈影响U的“另一端”变量：
       U1 控制 ln(1+V)
       U2 控制 ln(1+M)
       U3 控制 L_VM = [ln(1+V)+ln(1+M)]/2
   这些控制变量进入模型，但不进入 Q 指标 SHAP 排名，也不进入 Q-Q 组合筛选。

2. 大幅减少图片，只保留每个U最核心的7类图：
       ① SHAP蜂群图
       ② SHAP Dependence + LOWESS（Top3单指标，合并为一张图）
       ③ SHAP Interaction Top10渐变棒棒糖图
       ④ Top1组合真实U散点图
       ⑤ Top1组合的 GAM Tensor 曲面
       ⑥ Top1组合的 2D ALE 图
       ⑦ Top1组合的构成项分解图（两张小图合成一张）

此外：
- 所有交叉验证指标、Top指标、Top组合、GAM统计量、各图文件名，
  都会自动写入 analysis_summary.txt。
- U1/U2/U3 对应的图会在 TXT 中分开写清楚。

依赖：
    pip install numpy pandas matplotlib scikit-learn xgboost shap pygam statsmodels

输入：
    gua.csv
    four.csv
    mixing_scores.csv
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from statsmodels.nonparametric.smoothers_lowess import lowess

import xgboost as xgb
import shap
from pygam import LinearGAM, s, te

warnings.filterwarnings("ignore")


# ============================================================
# 1. 配置
# ============================================================

GUA_FILE = "gua.csv"
FOUR_FILE = "four.csv"
MIX_FILE = "mixing_scores.csv"

INDEX_COL = "index"
Q_COL = "界面品质"
V_COL = "活力度"
M_COL = "混合度"

NORMALIZE_Q_FEATURES = True

# ============================================================
# 从“Q底层指标解释分析”中排除的指标
# ============================================================
# 注意：
# 1. 这里只是不再把这些指标作为 SHAP / Interaction / GAM / ALE 的解释变量；
# 2. 原始“界面品质 Q”数值保持不变，不重新计算Q；
# 3. 本研究排除两个指标：
#    （1）路面状态：
#        大多数样本路面状态均较完好，整体取值偏高、差异度有限，
#        容易形成普遍抬升，对点位差异的辨识作用较弱。
#    （2）消费型停留空间占比：
#        该指标不仅反映物质界面本身，还受到人的消费、停留和使用行为影响，
#        因而不完全属于纯粹的界面品质特征。为保持解释变量在概念上的一致性，
#        本研究不将其纳入后续Q底层指标解释分析。
EXCLUDED_Q_FEATURES = [
    "路面状态",
    "消费型停留空间占比(%)",
]

XGB_PARAMS = dict(
    n_estimators=150,
    learning_rate=0.08,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    objective="reg:squarederror",
    n_jobs=-1,
)

N_SPLITS = 5
RANDOM_STATE = 42

# 每个U只研究交互强度最高的1组，显著减少输出图数量
TOP_PAIRS = 1

# 每个U绘制SHAP重要性最高的前3个单指标依赖图，并叠加LOWESS趋势线
SHAP_DEPENDENCE_TOP_N = 3
LOWESS_FRAC = 0.50

GAM_PAIR_SPLINES = 6
GAM_CONTROL_SPLINES = 4
GAM_LAM_GRID = np.logspace(-2, 3, 7)

SURFACE_GRID_SIZE = 50
ALE_BINS = 8
DPI = 300

OUT_DIR = Path("analysis_U123_Q_features_compact")

SUBDIRS = {
    "shap": OUT_DIR / "01_SHAP",
    "interaction": OUT_DIR / "02_Interaction",
    "gam": OUT_DIR / "03_GAM",
    "ale": OUT_DIR / "04_ALE",
    "decomp": OUT_DIR / "05_Decomposition",
    "tables": OUT_DIR / "06_Tables",
}
for p in SUBDIRS.values():
    p.mkdir(parents=True, exist_ok=True)

REPORT_FILE = OUT_DIR / "analysis_summary.txt"


# ============================================================
# 2. 中文字体
# ============================================================

def set_chinese_font():
    preferred = [
        "Microsoft YaHei", "SimHei", "SimSun",
        "Arial Unicode MS", "WenQuanYi Micro Hei", "STHeiti"
    ]
    existing = {f.name for f in fm.fontManager.ttflist}
    for font in preferred:
        if font in existing:
            plt.rcParams["font.sans-serif"] = [font]
            print(f"[字体] 使用中文字体：{font}")
            break
    plt.rcParams["axes.unicode_minus"] = False

set_chinese_font()


# ============================================================
# 3. 报告写入辅助
# ============================================================

REPORT_LINES = []

def report(line=""):
    """同时打印到终端，并写入最终TXT报告缓存。"""
    print(line)
    REPORT_LINES.append(str(line))

def save_report():
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(REPORT_LINES), encoding="utf-8")
    print(f"\n[报告] 已写入：{REPORT_FILE.resolve()}")


# ============================================================
# 4. 数据工具
# ============================================================

def require_columns(df, required, file_name):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(
            f"{file_name} 缺少必要列：{missing}\n"
            f"实际列名：{list(df.columns)}"
        )

def minmax_dataframe(df):
    """
    每个Q底层指标独立做 Min-Max：
        z = (x-min)/(max-min)
    """
    out = pd.DataFrame(index=df.index)
    for col in df.columns:
        x = pd.to_numeric(df[col], errors="coerce")
        xmin, xmax = x.min(), x.max()
        if np.isclose(xmax, xmin):
            out[col] = 0.0
        else:
            out[col] = (x - xmin) / (xmax - xmin)
    return out

def safe_name(text):
    for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        text = text.replace(ch, "_")
    return text


# ============================================================
# 5. 读取与对齐
# ============================================================

def load_and_merge_data():
    report("=" * 80)
    report("Q底层指标 → U1/U2/U3：控制变量 + SHAP + Interaction + GAM + ALE")
    report("=" * 80)
    report("")
    report("【1. 数据读取与对齐】")

    gua = pd.read_csv(GUA_FILE)
    four = pd.read_csv(FOUR_FILE)
    mix = pd.read_csv(MIX_FILE)

    gua.columns = gua.columns.astype(str).str.strip()
    four.columns = four.columns.astype(str).str.strip()
    mix.columns = mix.columns.astype(str).str.strip()

    require_columns(gua, [Q_COL], GUA_FILE)
    require_columns(four, [V_COL], FOUR_FILE)
    require_columns(mix, [M_COL], MIX_FILE)

    has_index = (
        INDEX_COL in gua.columns
        and INDEX_COL in four.columns
        and INDEX_COL in mix.columns
    )

    if has_index:
        index_used = INDEX_COL
        report(f"[对齐] 三个CSV均含 {INDEX_COL}，按该列一对一合并。")
    else:
        lengths = {
            GUA_FILE: len(gua),
            FOUR_FILE: len(four),
            MIX_FILE: len(mix),
        }
        if len(set(lengths.values())) != 1:
            raise ValueError(
                "三个CSV缺少共同index，且行数不同，不能安全对齐。\n"
                f"行数：{lengths}"
            )
        index_used = "__sample_id__"
        gua = gua.copy()
        four = four.copy()
        mix = mix.copy()
        gua[index_used] = np.arange(len(gua))
        four[index_used] = np.arange(len(four))
        mix[index_used] = np.arange(len(mix))
        report("[对齐] CSV缺少index，但三表行数一致，按当前行顺序创建 sample_id 对齐。")
        report("[提醒] 这要求三个CSV第n行确实对应同一个点位。")

    exclude = {Q_COL, index_used}
    if INDEX_COL in gua.columns:
        exclude.add(INDEX_COL)

    # 先得到Q的全部底层指标
    q_features_all = [c for c in gua.columns if c not in exclude]

    # 再排除本研究不纳入后续解释分析的指标
    q_features = [
        c for c in q_features_all
        if c not in EXCLUDED_Q_FEATURES
    ]

    # 检查用户指定排除项是否确实存在于原始Q底层指标中
    missing_excluded = [
        c for c in EXCLUDED_Q_FEATURES
        if c not in q_features_all
    ]
    if missing_excluded:
        report(
            f"[提醒] 以下指定排除指标在 gua.csv 中未找到：{missing_excluded}"
        )

    report(f"[Q底层指标] 原始共 {len(q_features_all)} 个")
    report(f"[排除指标] {EXCLUDED_Q_FEATURES}")
    report(f"[实际进入分析] 共 {len(q_features)} 个")
    report(
        "[排除原因1：路面状态] 大多数样本的路面状态均较完好，"
        "该指标整体取值偏高、区分度有限，容易形成普遍抬升，"
        "因此不再将其作为后续不配得性解释变量。"
    )
    report(
        "[排除原因2：消费型停留空间占比] 该指标受到消费、停留和使用行为影响，"
        "并非完全由物质界面品质本身决定。为了使后续解释变量更集中于"
        "界面品质本身，本研究不再将其纳入SHAP、Interaction、GAM和ALE分析。"
    )
    report(
        "[说明] 仅从底层指标解释分析中排除，原始界面品质Q不重新计算。"
    )

    base = gua[[index_used] + q_features + [Q_COL]].copy()
    base = base.merge(
        four[[index_used, V_COL]],
        on=index_used, how="inner", validate="one_to_one"
    )
    base = base.merge(
        mix[[index_used, M_COL]],
        on=index_used, how="inner", validate="one_to_one"
    )

    if index_used != "sample_id":
        base = base.rename(columns={index_used: "sample_id"})

    numeric_cols = q_features + [Q_COL, V_COL, M_COL]
    for col in numeric_cols:
        base[col] = pd.to_numeric(base[col], errors="coerce")

    before = len(base)
    base = base.dropna(subset=numeric_cols).reset_index(drop=True)
    if before != len(base):
        report(f"[清洗] 因缺失值删除 {before-len(base)} 行。")

    V = base[V_COL].to_numpy(float)
    M = base[M_COL].to_numpy(float)
    Q = base[Q_COL].to_numpy(float)

    if np.any(V <= -1) or np.any(M <= -1) or np.any(Q <= -1):
        raise ValueError("V/M/Q存在 <= -1 的值，无法计算 ln(1+x)。")

    # 三类不配得性
    base["ln1p_V"] = np.log1p(V)
    base["ln1p_M"] = np.log1p(M)
    base["ln1p_Q"] = np.log1p(Q)

    base["U1"] = base["ln1p_V"] - base["ln1p_Q"]
    base["U2"] = base["ln1p_M"] - base["ln1p_Q"]
    base["U3"] = base["ln1p_V"] - base["ln1p_M"]

    # U3的“共同水平”控制项：
    # 控制V/M整体高低，但不直接控制V-M差异本身。
    base["L_VM"] = (base["ln1p_V"] + base["ln1p_M"]) / 2.0

    identity_error = np.abs(
        base["U1"] - base["U2"] - base["U3"]
    ).max()

    report(f"[样本] 共同样本数：{len(base)}")
    report(f"[Q底层指标] 共 {len(q_features)} 个")
    report(f"[恒等式检查] max|U1-U2-U3| = {identity_error:.12g}")

    X_q_raw = base[q_features].copy()
    X_q = minmax_dataframe(X_q_raw) if NORMALIZE_Q_FEATURES else X_q_raw.copy()

    report("[Q指标尺度] 已按各指标全域 min/max 转为 [0,1]。")

    return base, X_q, q_features


# ============================================================
# 6. 三类U对应的控制变量
# ============================================================

CONTROL_CONFIG = {
    "U1": {
        "control_col": "ln1p_V",
        "control_label": "ln(1+V)",
        "meaning": "控制不同点位活力度V本身的差异，只解释Q底层指标部分",
    },
    "U2": {
        "control_col": "ln1p_M",
        "control_label": "ln(1+M)",
        "meaning": "控制不同点位混合度M本身的差异，只解释Q底层指标部分",
    },
    "U3": {
        "control_col": "L_VM",
        "control_label": "L_VM=[ln(1+V)+ln(1+M)]/2",
        "meaning": "控制V/M总体水平高低，但保留V-M之间的不配得差异",
    },
}

DECOMPOSITION = {
    "U1": [
        ("ln1p_V", "ln(1+V)：活力度端"),
        ("ln1p_Q", "ln(1+Q)：界面品质端"),
    ],
    "U2": [
        ("ln1p_M", "ln(1+M)：混合度端"),
        ("ln1p_Q", "ln(1+Q)：界面品质端"),
    ],
    "U3": [
        ("ln1p_V", "ln(1+V)：活力度端"),
        ("ln1p_M", "ln(1+M)：混合度端"),
    ],
}


# ============================================================
# 7. XGBoost + 交叉验证
# ============================================================

def make_xgb_model():
    return xgb.XGBRegressor(**XGB_PARAMS)

def build_model_matrix(base, X_q, u_name):
    """
    模型输入 = 排除指定指标后的Q底层指标 + 1个控制变量。

    控制变量只是 nuisance/control variable：
    - 它进入模型以减少U中另一端的干扰；
    - 但后续SHAP排名只展示Q指标；
    - SHAP Interaction也只筛Q-Q组合。
    """
    cfg = CONTROL_CONFIG[u_name]
    X_model = X_q.copy()
    X_model["__CONTROL__"] = base[cfg["control_col"]].to_numpy(float)
    return X_model

def evaluate_xgb_cv(X_model, y):
    kf = KFold(
        n_splits=N_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE
    )
    pred = cross_val_predict(
        make_xgb_model(),
        X_model,
        y,
        cv=kf,
        n_jobs=1
    )
    return {
        "R2": r2_score(y, pred),
        "RMSE": np.sqrt(mean_squared_error(y, pred)),
        "MAE": mean_absolute_error(y, pred),
    }


# ============================================================
# 8. SHAP：只显示Q底层指标
# ============================================================

def fit_xgb_and_shap(X_model, X_q, y, u_name):
    model = make_xgb_model()
    model.fit(X_model, y)

    explainer = shap.TreeExplainer(model)
    shap_all = explainer.shap_values(X_model)
    if isinstance(shap_all, list):
        shap_all = shap_all[0]

    # Q指标永远位于模型矩阵前面，控制变量在最后一列
    n_q = X_q.shape[1]
    shap_q = shap_all[:, :n_q]

    mean_abs = np.abs(shap_q).mean(axis=0)
    importance = pd.DataFrame({
        "Feature": X_q.columns,
        "Mean_Abs_SHAP": mean_abs
    }).sort_values("Mean_Abs_SHAP", ascending=False)

    # 只保留一张SHAP蜂群图，不再额外画bar图
    plt.figure(figsize=(10, 6.8))
    shap.summary_plot(
        shap_q,
        X_q,
        show=False,
        max_display=len(X_q.columns)
    )
    plt.title(
        f"{u_name}：Q底层指标 SHAP 总览\n"
        f"控制变量：{CONTROL_CONFIG[u_name]['control_label']}",
        fontsize=12, pad=14
    )
    plt.tight_layout()

    path = SUBDIRS["shap"] / f"{u_name}_SHAP_summary.png"
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close()

    importance.to_csv(
        SUBDIRS["tables"] / f"{u_name}_SHAP_importance.csv",
        index=False,
        encoding="utf-8-sig"
    )

    return model, shap_q, importance, path


# ============================================================
# 8.5 SHAP Dependence + LOWESS：TopN单指标响应形态
# ============================================================

def plot_shap_dependence_lowess(X_q, shap_q, importance, u_name):
    """
    对SHAP重要性排名前N的Q底层指标绘制依赖图：
        横轴 = 归一化后的指标值
        纵轴 = 该指标对应的SHAP值
        散点 = 每个样本
        LOWESS曲线 = 指标值与SHAP贡献之间的总体非线性趋势

    该图只用于解释单指标响应形态，不用于替代SHAP Interaction。
    """
    top_features = importance.head(SHAP_DEPENDENCE_TOP_N)["Feature"].tolist()
    n = len(top_features)

    fig, axes = plt.subplots(1, n, figsize=(5.2 * n, 4.8), squeeze=False)
    axes = axes.ravel()

    # SHAP summary常用的蓝-紫-粉色系
    point_color = "#7B6FD0"
    lowess_color = "#FF0D57"

    for ax, feature in zip(axes, top_features):
        j = X_q.columns.get_loc(feature)
        x = X_q[feature].to_numpy(dtype=float)
        y = np.asarray(shap_q[:, j], dtype=float)

        # 原始样本散点
        ax.scatter(
            x, y,
            s=28, alpha=0.55,
            color=point_color,
            edgecolors="white", linewidths=0.35,
            zorder=2
        )

        # LOWESS平滑趋势
        order = np.argsort(x)
        x_sorted = x[order]
        y_sorted = y[order]
        smoothed = lowess(
            endog=y_sorted,
            exog=x_sorted,
            frac=LOWESS_FRAC,
            it=1,
            return_sorted=True
        )
        ax.plot(
            smoothed[:, 0], smoothed[:, 1],
            color=lowess_color, linewidth=1.5,
            label=f"LOWESS (frac={LOWESS_FRAC:.2f})",
            zorder=3
        )

        # SHAP = 0基准线
        ax.axhline(0, color="#666666", linestyle="--", linewidth=1.0, alpha=0.8)

        ax.set_xlabel(f"{feature}（归一化）")
        ax.set_ylabel("SHAP value")
        ax.set_title(feature, fontsize=11)
        ax.grid(alpha=0.16)
        ax.legend(frameon=False, fontsize=8, loc="best")

    fig.suptitle(
        f"{u_name}：Top{n} Q底层指标 SHAP Dependence + LOWESS\n"
        f"控制变量：{CONTROL_CONFIG[u_name]['control_label']}",
        fontsize=12
    )
    fig.tight_layout(rect=[0, 0, 1, 0.90])

    path = SUBDIRS["shap"] / f"{u_name}_SHAP_dependence_Top{n}_LOWESS.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    # 同时保存TopN名称，便于报告引用
    return path, top_features


# ============================================================
# 9. SHAP Interaction：只研究Q-Q组合
# ============================================================

def shap_interaction(model, X_model, X_q, u_name):
    """
    计算 TreeSHAP interaction，并绘制 Top10 横向棒棒糖图。

    本版只调整配色：
    - 仍然保留原来的圆点端头；
    - 仍然保留原来的横向棒棒糖布局；
    - 颜色从上到下由粉红逐渐过渡到蓝色，
      与SHAP summary的粉-蓝视觉风格保持一致；
    - 完整组合结果仍保存到CSV。
    """
    from matplotlib.colors import LinearSegmentedColormap

    explainer = shap.TreeExplainer(model)
    inter_all = explainer.shap_interaction_values(X_model)
    if isinstance(inter_all, list):
        inter_all = inter_all[0]

    n_q = X_q.shape[1]
    inter_q = inter_all[:, :n_q, :n_q]

    mean_abs = np.abs(inter_q).mean(axis=0)
    np.fill_diagonal(mean_abs, 0.0)

    cols = list(X_q.columns)
    pair_rows = []

    for i in range(n_q):
        for j in range(i + 1, n_q):
            pair_rows.append({
                "Feature_1": cols[i],
                "Feature_2": cols[j],
                "Mean_Abs_SHAP_Interaction": mean_abs[i, j],
            })

    pair_df = pd.DataFrame(pair_rows).sort_values(
        "Mean_Abs_SHAP_Interaction",
        ascending=False
    ).reset_index(drop=True)

    matrix_df = pd.DataFrame(mean_abs, index=cols, columns=cols)
    matrix_df.to_csv(
        SUBDIRS["tables"] / f"{u_name}_SHAP_interaction_matrix.csv",
        encoding="utf-8-sig"
    )
    pair_df.to_csv(
        SUBDIRS["tables"] / f"{u_name}_all_pair_interactions.csv",
        index=False,
        encoding="utf-8-sig"
    )

    top_n = min(10, len(pair_df))
    plot_df = pair_df.head(top_n).copy()
    plot_df["Pair"] = (
        plot_df["Feature_1"].astype(str)
        + " × "
        + plot_df["Feature_2"].astype(str)
    )

    # 第一名显示在最上方
    plot_df = plot_df.iloc[::-1].reset_index(drop=True)

    y_pos = np.arange(len(plot_df))
    x_val = plot_df["Mean_Abs_SHAP_Interaction"].to_numpy(float)

    # SHAP风格：弱交互蓝色，强交互粉红色
    shap_cmap = LinearSegmentedColormap.from_list(
        "shap_pink_blue",
        ["#1E88E5", "#7B6FD0", "#D85A9E", "#FF0D57"]
    )
    # plot_df已经反序，因此底部为弱、顶部为强
    colors = [shap_cmap(v) for v in np.linspace(0.0, 1.0, top_n)]

    fig, ax = plt.subplots(figsize=(10.5, 6.8))

    # 横线
    for y, x, color in zip(y_pos, x_val, colors):
        ax.hlines(
            y=y,
            xmin=0,
            xmax=x,
            color=color,
            linewidth=2.2,
            alpha=0.72,
            zorder=1
        )

    # 圆点端头
    ax.scatter(
        x_val,
        y_pos,
        s=75,
        c=colors,
        zorder=3
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_df["Pair"], fontsize=9)
    ax.set_xlabel("Mean |SHAP interaction|")
    ax.set_ylabel("")
    ax.set_title(
        f"{u_name}：Q底层指标 Top{top_n} 两两交互组合\n"
        f"控制变量：{CONTROL_CONFIG[u_name]['control_label']}",
        fontsize=12
    )

    # 数值标签仍保持原来的形式，放在圆点右侧
    xmax = max(float(x_val.max()), 1e-12)
    for y, x in zip(y_pos, x_val):
        ax.text(
            x + xmax * 0.015,
            y,
            f"{x:.4f}",
            va="center",
            fontsize=8
        )

    ax.set_xlim(0, xmax * 1.18)
    ax.grid(axis="x", alpha=0.22)
    fig.tight_layout()

    path = (
        SUBDIRS["interaction"]
        / f"{u_name}_SHAP_interaction_Top10_lollipop_gradient.png"
    )
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    return pair_df, path


# ============================================================
# 9.5 Top1组合的真实U散点图
# ============================================================

def plot_real_u_scatter(df, u_name, f1, f2):
    """
    真实U散点图：
    横轴 = Top1组合中的第一个Q底层指标
    纵轴 = Top1组合中的第二个Q底层指标
    颜色 = 真实U值

    该图直接使用观测到的真实U，不依赖模型预测，
    用于辅助检查Top1交互组合在原始样本中的真实分布。
    """
    x = df[f1].to_numpy(dtype=float)
    y = df[f2].to_numpy(dtype=float)
    u = df[u_name].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(8.4, 6.8))

    sc = ax.scatter(
        x,
        y,
        c=u,
        cmap="coolwarm",
        s=58,
        alpha=0.82,
        edgecolors="white",
        linewidths=0.45
    )

    cbar = fig.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label(f"真实 {u_name}")

    ax.set_xlabel(f1)
    ax.set_ylabel(f2)
    ax.set_title(
        f"{u_name}：Top1指标组合的真实U散点分布\n"
        f"{f1} × {f2}",
        fontsize=12
    )

    ax.grid(alpha=0.18)
    fig.tight_layout()

    path = (
        SUBDIRS["interaction"]
        / f"{u_name}_Top1_{safe_name(f1)}__{safe_name(f2)}_real_U_scatter.png"
    )
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    return path


# ============================================================
# 10. GAM
# ============================================================

def build_gam_terms_with_control(feature_names, f1, f2):
    """
    主U模型：
        te(f1,f2)
        + s(其他Q底层指标)
        + s(控制变量)

    这里不追求显式公式，而是得到稳定的二维非线性联合曲面。
    """
    i = feature_names.index(f1)
    j = feature_names.index(f2)
    control_idx = feature_names.index("__CONTROL__")

    terms = te(
        i, j,
        n_splines=[GAM_PAIR_SPLINES, GAM_PAIR_SPLINES]
    )

    for k in range(len(feature_names)):
        if k not in (i, j, control_idx):
            terms += s(k, n_splines=GAM_CONTROL_SPLINES)

    terms += s(control_idx, n_splines=GAM_CONTROL_SPLINES)
    return terms

def fit_gam_with_control(X_model, y, f1, f2):
    names = list(X_model.columns)
    terms = build_gam_terms_with_control(names, f1, f2)

    gam = LinearGAM(terms)
    gam.gridsearch(
        X_model.to_numpy(),
        np.asarray(y),
        lam=GAM_LAM_GRID,
        progress=False
    )
    return gam

def make_pair_grid(X_model, f1, f2):
    x1 = np.linspace(X_model[f1].min(), X_model[f1].max(), SURFACE_GRID_SIZE)
    x2 = np.linspace(X_model[f2].min(), X_model[f2].max(), SURFACE_GRID_SIZE)
    g1, g2 = np.meshgrid(x1, x2)

    base = X_model.median(axis=0).to_numpy()
    grid_X = np.tile(base, (g1.size, 1))

    i = X_model.columns.get_loc(f1)
    j = X_model.columns.get_loc(f2)
    grid_X[:, i] = g1.ravel()
    grid_X[:, j] = g2.ravel()

    return g1, g2, grid_X

def plot_gam_surface(gam, X_model, X_q, f1, f2, u_name):
    g1, g2, grid_X = make_pair_grid(X_model, f1, f2)

    # te() 是第0项
    effect = np.asarray(
        gam.partial_dependence(term=0, X=grid_X)
    ).reshape(g1.shape)

    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    ct = ax.contourf(g1, g2, effect, levels=20, cmap="coolwarm")
    ax.scatter(
        X_q[f1], X_q[f2],
        c="black", s=12, alpha=0.25
    )
    fig.colorbar(ct, ax=ax, label=f"{u_name}：GAM二维联合部分效应")
    ax.set_xlabel(f"{f1}（归一化）")
    ax.set_ylabel(f"{f2}（归一化）")
    ax.set_title(
        f"{u_name}：Top1组合 GAM Tensor 曲面\n"
        f"{f1} × {f2}\n"
        f"控制：其余Q指标 + {CONTROL_CONFIG[u_name]['control_label']}"
    )
    fig.tight_layout()

    path = (
        SUBDIRS["gam"] /
        f"{u_name}_Top1_{safe_name(f1)}__{safe_name(f2)}_GAM.png"
    )
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    stats = gam.statistics_
    pvals = stats.get("p_values", [])
    tensor_p = pvals[0] if len(pvals) else np.nan

    pseudo_r2 = stats.get("pseudo_r2", np.nan)
    if hasattr(pseudo_r2, "get"):
        pseudo_r2 = pseudo_r2.get("explained_deviance", np.nan)

    return path, {
        "Tensor_p": tensor_p,
        "Explained_Deviance": pseudo_r2,
        "AIC": stats.get("AIC", np.nan),
        "GCV": stats.get("GCV", np.nan),
        "EDoF": stats.get("edof", np.nan),
    }


# ============================================================
# 11. 二阶ALE：仍基于“包含控制变量”的XGBoost模型
# ============================================================

def second_order_ale(model, X_model, f1, f2, bins=ALE_BINS):
    """
    ALE时只扰动f1/f2。
    其余Q指标和控制变量保持每个样本自己的原值。
    """
    a = X_model[f1].to_numpy()
    b = X_model[f2].to_numpy()

    e1 = np.unique(np.quantile(a, np.linspace(0, 1, bins + 1)))
    e2 = np.unique(np.quantile(b, np.linspace(0, 1, bins + 1)))

    if len(e1) < 4 or len(e2) < 4:
        raise ValueError("变量不同取值太少，无法稳定计算二维ALE。")

    n1, n2 = len(e1)-1, len(e2)-1

    bi1 = np.digitize(a, e1[1:-1], right=False)
    bi2 = np.digitize(b, e2[1:-1], right=False)
    bi1 = np.clip(bi1, 0, n1-1)
    bi2 = np.clip(bi2, 0, n2-1)

    delta = np.zeros((n1, n2))
    counts = np.zeros((n1, n2))

    for i in range(n1):
        for j in range(n2):
            idx = np.where((bi1 == i) & (bi2 == j))[0]
            if len(idx) == 0:
                continue

            cell = X_model.iloc[idx].copy()

            x00 = cell.copy()
            x10 = cell.copy()
            x01 = cell.copy()
            x11 = cell.copy()

            x00[f1], x00[f2] = e1[i],   e2[j]
            x10[f1], x10[f2] = e1[i+1], e2[j]
            x01[f1], x01[f2] = e1[i],   e2[j+1]
            x11[f1], x11[f2] = e1[i+1], e2[j+1]

            p00 = model.predict(x00)
            p10 = model.predict(x10)
            p01 = model.predict(x01)
            p11 = model.predict(x11)

            delta[i, j] = np.mean(p11 - p10 - p01 + p00)
            counts[i, j] = len(idx)

    accumulated = np.cumsum(np.cumsum(delta, axis=0), axis=1)

    total = counts.sum()
    weights = counts / total if total > 0 else counts

    row_mean = np.zeros(n1)
    col_mean = np.zeros(n2)

    for i in range(n1):
        w = weights[i, :]
        if w.sum() > 0:
            row_mean[i] = np.sum(accumulated[i, :] * w) / w.sum()

    for j in range(n2):
        w = weights[:, j]
        if w.sum() > 0:
            col_mean[j] = np.sum(accumulated[:, j] * w) / w.sum()

    global_mean = np.sum(accumulated * weights)

    ale2 = (
        accumulated
        - row_mean[:, None]
        - col_mean[None, :]
        + global_mean
    )

    xc = (e1[:-1] + e1[1:]) / 2
    yc = (e2[:-1] + e2[1:]) / 2

    return xc, yc, ale2

def plot_ale(model, X_model, X_q, f1, f2, u_name):
    xc, yc, surface = second_order_ale(
        model, X_model, f1, f2, bins=ALE_BINS
    )

    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    im = ax.imshow(
        surface.T,
        origin="lower",
        aspect="auto",
        cmap="coolwarm",
        extent=[xc.min(), xc.max(), yc.min(), yc.max()]
    )
    ax.scatter(
        X_q[f1], X_q[f2],
        c="black", s=12, alpha=0.22
    )
    fig.colorbar(im, ax=ax, label=f"{u_name}：二阶ALE联合效应")
    ax.set_xlabel(f"{f1}（归一化）")
    ax.set_ylabel(f"{f2}（归一化）")
    ax.set_title(
        f"{u_name}：Top1组合 2D ALE\n"
        f"{f1} × {f2}\n"
        "用于辅助验证GAM联合效应形状"
    )
    fig.tight_layout()

    path = (
        SUBDIRS["ale"] /
        f"{u_name}_Top1_{safe_name(f1)}__{safe_name(f2)}_ALE.png"
    )
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    return path


# ============================================================
# 12. 构成项分解：两张小图合成一张，减少图数量
# ============================================================

def build_gam_terms_q_only(feature_names, f1, f2):
    """
    构成项分解时不加入 nuisance control。

    原因：
    例如研究 ln(1+V) 这一端时，
    如果再把 ln(1+V) 自己作为控制变量，就会变成恒等式。

    因此这里回答的是：
        在控制其他Q底层指标后，
        重点组合分别与U两端的构成量如何关联？
    """
    i = feature_names.index(f1)
    j = feature_names.index(f2)

    terms = te(
        i, j,
        n_splines=[GAM_PAIR_SPLINES, GAM_PAIR_SPLINES]
    )
    for k in range(len(feature_names)):
        if k not in (i, j):
            terms += s(k, n_splines=GAM_CONTROL_SPLINES)
    return terms

def fit_gam_q_only(X_q, y, f1, f2):
    terms = build_gam_terms_q_only(list(X_q.columns), f1, f2)
    gam = LinearGAM(terms)
    gam.gridsearch(
        X_q.to_numpy(),
        np.asarray(y),
        lam=GAM_LAM_GRID,
        progress=False
    )
    return gam

def plot_decomposition(base, X_q, f1, f2, u_name):
    """
    一张图里放两个并排子图：
      U1：V端 vs Q端
      U2：M端 vs Q端
      U3：V端 vs M端

    这样既保留机制解释，又避免一对组合输出两张图片。
    """
    comps = DECOMPOSITION[u_name]

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.6))

    for ax, (col, label) in zip(axes, comps):
        y = base[col].to_numpy(float)
        gam = fit_gam_q_only(X_q, y, f1, f2)

        # 构造网格
        x1 = np.linspace(X_q[f1].min(), X_q[f1].max(), SURFACE_GRID_SIZE)
        x2 = np.linspace(X_q[f2].min(), X_q[f2].max(), SURFACE_GRID_SIZE)
        g1, g2 = np.meshgrid(x1, x2)

        base_row = X_q.median(axis=0).to_numpy()
        grid_X = np.tile(base_row, (g1.size, 1))

        i = X_q.columns.get_loc(f1)
        j = X_q.columns.get_loc(f2)
        grid_X[:, i] = g1.ravel()
        grid_X[:, j] = g2.ravel()

        effect = np.asarray(
            gam.partial_dependence(term=0, X=grid_X)
        ).reshape(g1.shape)

        ct = ax.contourf(g1, g2, effect, levels=20, cmap="coolwarm")
        ax.scatter(
            X_q[f1], X_q[f2],
            c="black", s=10, alpha=0.20
        )
        fig.colorbar(ct, ax=ax, shrink=0.85)
        ax.set_xlabel(f"{f1}（归一化）")
        ax.set_ylabel(f"{f2}（归一化）")
        ax.set_title(label)

    fig.suptitle(
        f"{u_name}：Top1组合的构成项分解\n"
        f"{f1} × {f2}\n"
        "比较同一组合对不配得性两端的响应差异",
        fontsize=12
    )
    fig.tight_layout(rect=[0, 0, 1, 0.90])

    path = (
        SUBDIRS["decomp"] /
        f"{u_name}_Top1_{safe_name(f1)}__{safe_name(f2)}_Decomposition.png"
    )
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    return path


# ============================================================
# 13. 单个U完整分析
# ============================================================

def analyze_one_u(base, X_q, u_name):
    cfg = CONTROL_CONFIG[u_name]
    y = base[u_name].to_numpy(float)
    X_model = build_model_matrix(base, X_q, u_name)

    report("")
    report("=" * 72)
    report(f"【{u_name} 分析】")
    report("=" * 72)
    report(f"目标：{u_name}")
    report(f"控制变量：{cfg['control_label']}")
    report(f"控制含义：{cfg['meaning']}")

    # ---------- 交叉验证 ----------
    metrics = evaluate_xgb_cv(X_model, y)
    report("")
    report("[交叉验证]")
    report(f"CV R²   = {metrics['R2']:.4f}")
    report(f"CV RMSE = {metrics['RMSE']:.6f}")
    report(f"CV MAE  = {metrics['MAE']:.6f}")

    # ---------- SHAP ----------
    model, shap_q, importance, shap_path = fit_xgb_and_shap(
        X_model, X_q, y, u_name
    )

    report("")
    report("[SHAP：Q底层指标重要性 Top5]")
    for rank, (_, row) in enumerate(importance.head(5).iterrows(), 1):
        report(
            f"{rank}. {row['Feature']} "
            f"(Mean|SHAP|={row['Mean_Abs_SHAP']:.6f})"
        )

    # ---------- SHAP Dependence + LOWESS ----------
    dependence_path, dependence_features = plot_shap_dependence_lowess(
        X_q=X_q,
        shap_q=shap_q,
        importance=importance,
        u_name=u_name
    )
    report("")
    report("[SHAP Dependence + LOWESS]")
    report("绘制指标：" + "、".join(dependence_features))
    report(
        "解释：用于观察单个Q底层指标从低到高变化时，其SHAP贡献如何变化，"
        "并通过LOWESS识别非线性、阈值、平台期或拐点。"
    )

    # ---------- Interaction ----------
    pair_df, inter_path = shap_interaction(
        model, X_model, X_q, u_name
    )

    top = pair_df.iloc[0]
    f1 = top["Feature_1"]
    f2 = top["Feature_2"]
    inter_strength = top["Mean_Abs_SHAP_Interaction"]

    report("")
    report("[Top1 二元组合]")
    report(f"{f1} × {f2}")
    report(f"Mean|SHAP interaction| = {inter_strength:.6f}")

    # ---------- 真实U散点图 ----------
    real_u_scatter_path = plot_real_u_scatter(
        base, u_name, f1, f2
    )

    # ---------- GAM ----------
    gam = fit_gam_with_control(
        X_model, y, f1, f2
    )
    gam_path, gam_stats = plot_gam_surface(
        gam, X_model, X_q, f1, f2, u_name
    )

    report("")
    report("[GAM Tensor]")
    report(f"Tensor项 p值 = {gam_stats['Tensor_p']:.6g}")
    report(
        f"Explained deviance = "
        f"{gam_stats['Explained_Deviance']:.4f}"
        if pd.notna(gam_stats["Explained_Deviance"])
        else "Explained deviance = NaN"
    )
    report(
        "解释：GAM图用于观察在控制其余Q指标和控制变量后，"
        "Top1组合在不同取值区域如何共同推高/压低U。"
    )

    # ---------- ALE ----------
    try:
        ale_path = plot_ale(
            model, X_model, X_q, f1, f2, u_name
        )
        ale_note = (
            "ALE图用于从XGBoost角度辅助验证GAM二维联合效应的"
            "主要方向/高低区域是否一致。"
        )
    except Exception as e:
        ale_path = None
        ale_note = f"ALE生成失败：{repr(e)}"

    # ---------- 构成项分解 ----------
    decomp_path = plot_decomposition(
        base, X_q, f1, f2, u_name
    )

    # ---------- 把对应图片在TXT里写清楚 ----------
    report("")
    report(f"[{u_name} 对应图表]")
    report(f"图1 SHAP蜂群图：{shap_path}")
    report(
        "    用途：判断哪些Q底层指标最重要，以及高/低指标值通常把U往哪个方向推动。"
    )
    report(f"图2 SHAP Dependence + LOWESS：{dependence_path}")
    report(
        "    用途：展开SHAP排名前3的单指标响应形态，观察指标值从低到高时SHAP贡献的"
        "非线性趋势、可能阈值、平台期和拐点。"
    )
    report(f"图3 SHAP Interaction Top10渐变棒棒糖图：{inter_path}")
    report(
        "    用途：按Mean|SHAP interaction|从高到低展示前10组组合，并筛选Top1组合；完整结果保存在CSV中。"
    )
    report(f"图4 Top1组合真实U散点图：{real_u_scatter_path}")
    report(
        "    用途：直接查看Top1两个指标在真实样本中的组合位置，以及对应真实U值的高低分布；"
        "该图不依赖模型预测，是对SHAP交互结果的原始数据辅助验证。"
    )
    report(f"图5 Top1 GAM Tensor曲面：{gam_path}")
    report(
        f"    用途：重点解释 {f1} × {f2} 在控制其余Q指标及"
        f"{cfg['control_label']} 后的二维联合效应。"
    )

    if ale_path is not None:
        report(f"图6 Top1 2D ALE：{ale_path}")
        report(f"    用途：{ale_note}")
    else:
        report(f"图6 Top1 2D ALE：未生成。{ale_note}")

    report(f"图7 Top1 构成项分解图：{decomp_path}")
    if u_name == "U1":
        report(
            "    用途：比较同一指标组合对 ln(1+V) 与 ln(1+Q) 两端的响应，"
            "解释V-Q不配得为什么形成。"
        )
    elif u_name == "U2":
        report(
            "    用途：比较同一指标组合对 ln(1+M) 与 ln(1+Q) 两端的响应，"
            "解释M-Q不配得为什么形成。"
        )
    else:
        report(
            "    用途：比较同一指标组合对 ln(1+V) 与 ln(1+M) 两端的响应，"
            "解释V-M不配得为什么形成。"
        )

    # 保存该U最核心结果表
    importance.to_csv(
        SUBDIRS["tables"] / f"{u_name}_SHAP_importance.csv",
        index=False, encoding="utf-8-sig"
    )
    pair_df.to_csv(
        SUBDIRS["tables"] / f"{u_name}_pair_ranking.csv",
        index=False, encoding="utf-8-sig"
    )

    return {
        "Outcome": u_name,
        "Control": cfg["control_label"],
        "CV_R2": metrics["R2"],
        "CV_RMSE": metrics["RMSE"],
        "CV_MAE": metrics["MAE"],
        "Top_Feature": importance.iloc[0]["Feature"],
        "Dependence_TopN": " | ".join(dependence_features),
        "Top_Pair_1": f1,
        "Top_Pair_2": f2,
        "Top_Pair_Interaction": inter_strength,
        "GAM_Tensor_p": gam_stats["Tensor_p"],
        "GAM_Explained_Deviance": gam_stats["Explained_Deviance"],
    }


# ============================================================
# 14. 主程序
# ============================================================

def main():
    base, X_q, q_features = load_and_merge_data()

    report("")
    report("【2. 本版输出原则】")
    report("每个U只保留7类核心图，并新增SHAP Dependence + LOWESS；不再输出：")
    report("- U分布图")
    report("- U之间的散点图")
    report("- 单独SHAP重要性bar图")
    report("- Top组合bar图")
    report("- 每个Top组合的真实U彩色散点图")
    report("- Top2/Top3的GAM/ALE/分解图")
    report("")
    report("每个U只对SHAP Interaction排名第1的组合做GAM、ALE和构成项分解。")

    all_rows = []

    for u_name in ["U1", "U2", "U3"]:
        row = analyze_one_u(
            base=base,
            X_q=X_q,
            u_name=u_name
        )
        all_rows.append(row)

    summary_df = pd.DataFrame(all_rows)
    summary_path = SUBDIRS["tables"] / "U123_core_results.csv"
    summary_df.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig"
    )

    report("")
    report("=" * 80)
    report("【3. 指标排除说明】")
    report("=" * 80)
    report(
        "本研究将“路面状态”和“消费型停留空间占比”从Q底层指标的后续解释分析中排除。"
    )
    report(
        "路面状态：多数样本均较完好，整体取值偏高、差异度有限，"
        "容易形成普遍抬升，对点位差异的辨识作用较弱。"
    )
    report(
        "消费型停留空间占比：该指标受到人的消费、停留及使用行为影响，"
        "并非完全由物质界面品质本身决定。为保持Q底层解释变量的概念一致性，"
        "后续不再将其作为界面品质解释指标。"
    )
    report(
        "需要强调：以上两个指标只从SHAP、Interaction、GAM、ALE等底层解释分析中排除；"
        "原始界面品质Q仍保持原有定义和数值，不重新计算。"
    )

    report("")
    report("=" * 80)
    report("【4. 三类不配得性的解释边界】")
    report("=" * 80)
    report(
        "U1：Q底层指标与U1既存在Q构成上的结构联系，也存在与V相关的现实空间关联；"
        "本模型用 ln(1+V) 作为控制变量排除V本身在点位间的大幅波动。"
    )
    report(
        "U2：同理，本模型用 ln(1+M) 作为控制变量排除M本身在点位间的大幅波动。"
    )
    report(
        "U3：U3定义中没有Q，因此Q底层指标与U3的结果应解释为统计关联/空间响应关系，"
        "不能写成“通过Q直接导致U3”。"
    )
    report(
        "U3控制 L_VM=[ln(1+V)+ln(1+M)]/2，目的是控制V/M总体水平高低，"
        "但保留V-M之间真正的不配得差异。"
    )

    report("")
    report("【5. 核心结果汇总表】")
    report(str(summary_path))
    report("")
    report(summary_df.to_string(index=False))

    save_report()

    print("\n全部完成。")
    print(f"输出目录：{OUT_DIR.resolve()}")
    print(f"分析文字：{REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main()
