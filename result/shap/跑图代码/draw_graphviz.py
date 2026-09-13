# -*- coding: utf-8 -*-

from graphviz import Digraph


# ============================================================
# 1. 创建流程图
# ============================================================

dot = Digraph("algorithm_flowchart")

dot.attr(
    rankdir="TB",
    splines="ortho",
    bgcolor="#FAFAFA",

    # 节点间距
    nodesep="0.85",
    ranksep="0.90",

    pad="0.55",
    newrank="true",
    concentrate="false"
)


# ============================================================
# 2. 全局节点样式
# ============================================================

dot.attr(
    "node",

    shape="box",
    style="rounded,filled",

    fontname="Microsoft YaHei",
    fontsize="11",
    fontcolor="#333333",

    color="#AEB4BC",
    fillcolor="#F3F4F6",

    penwidth="1.15",
    margin="0.24,0.18"
)


# ============================================================
# 3. 全局连线样式
# ============================================================

dot.attr(
    "edge",

    fontname="Microsoft YaHei",
    fontsize="9",

    color="#8A939D",
    fontcolor="#6B7280",

    penwidth="1.05",

    arrowsize="0.65",
    arrowhead="vee"
)


# ============================================================
# 第一阶段：底层指标
# ============================================================

dot.node(
    "raw",

    "底层指标数据\n"
    "活力度、混合度与界面品质的底层指标",

    fillcolor="#F1F3F5"
)


# ============================================================
# 第二阶段：Min-Max归一化
# ============================================================

dot.node(
    "norm",

    "Min-Max 归一化\n"
    "x⁎ᵢⱼ = (xᵢⱼ − min(xⱼ)) / (max(xⱼ) − min(xⱼ))\n"
    "各底层指标统一映射至 [0,1]",

    fillcolor="#EEF3F8",
    color="#AAB8C5"
)

dot.edge("raw", "norm")


# ============================================================
# 第三阶段：CRITIC客观赋权
# ============================================================

dot.node(
    "critic",

    "CRITIC 客观赋权\n"
    "Cⱼ = σⱼ × Σₖ₌₁ᵐ(1 − rⱼₖ)\n"
    "wⱼ = Cⱼ / Σⱼ₌₁ᵐ Cⱼ\n"
    "根据指标变异性与指标间冲突性确定权重",

    fillcolor="#EEF3F8",
    color="#AAB8C5"
)

dot.edge("norm", "critic")


# ============================================================
# 第四阶段：V / M / Q
# ============================================================

dot.node(
    "V",

    "活力度 V\n"
    "V = Σᵢ₌₁ᵖ wᵢ · xᵢ",

    fillcolor="#FFF3EB",
    color="#D7A987"
)


dot.node(
    "M",

    "混合度 M\n"
    "M = Σᵢ₌₁ᵏ wᵢ · xᵢ",

    fillcolor="#FFF3EB",
    color="#D7A987"
)


dot.node(
    "Q",

    "界面品质 Q\n"
    "Q = Σᵢ₌₁ʳ wᵢ · xᵢ",

    fillcolor="#FFF3EB",
    color="#D7A987"
)


with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("V")
    s.node("M")
    s.node("Q")


dot.edge(
    "V",
    "M",
    style="invis",
    weight="30"
)

dot.edge(
    "M",
    "Q",
    style="invis",
    weight="30"
)


dot.edge("critic", "V")
dot.edge("critic", "M")
dot.edge("critic", "Q")


# ============================================================
# Q底层指标筛选
# ============================================================

dot.node(
    "Qfilter",

    "Q 底层指标筛选\n"
    "下游解释分析保留 9 项指标",

    fillcolor="#EEF4F1",
    color="#9FB5AA"
)


dot.node(
    "remove1",

    "排除\n"
    "路面状态",

    fillcolor="#F7F7F7",
    color="#C2C7CC"
)


dot.node(
    "remove2",

    "排除\n"
    "消费型停留空间占比",

    fillcolor="#F7F7F7",
    color="#C2C7CC"
)


# Q 与 Qfilter 同一行
with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("Q")
    s.node("Qfilter")


# 强制 Q 在左，Qfilter在右
dot.edge(
    "Q",
    "Qfilter",

    style="invis",
    weight="50"
)


# 筛选作为Q的辅助说明
dot.edge(
    "Qfilter",
    "Q",

    style="dashed",
    color="#9FB5AA",

    arrowhead="vee",
    constraint="false"
)


# remove1位于Qfilter右侧
with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("Qfilter")
    s.node("remove1")


dot.edge(
    "Qfilter",
    "remove1",

    style="invis",
    weight="50"
)


# remove2在remove1下方
dot.edge(
    "remove1",
    "remove2",

    style="invis",
    weight="50"
)


dot.edge(
    "remove1",
    "Qfilter",

    style="dashed",
    color="#C3C7CB",

    arrowhead="none",
    constraint="false"
)


dot.edge(
    "remove2",
    "Qfilter",

    style="dashed",
    color="#C3C7CB",

    arrowhead="none",
    constraint="false"
)


# ============================================================
# 第五阶段：U₁ / U₂ / U₃
# ============================================================

dot.node(
    "U1",

    "U₁ 活力度－界面品质不配得性\n"
    "U₁ = ln(1+V) − ln(1+Q)",

    fillcolor="#F8F1EC",
    color="#D1A98C"
)


dot.node(
    "U2",

    "U₂ 混合度－界面品质不配得性\n"
    "U₂ = ln(1+M) − ln(1+Q)",

    fillcolor="#F8F1EC",
    color="#D1A98C"
)


dot.node(
    "U3",

    "U₃ 活力度－混合度不配得性\n"
    "U₃ = ln(1+V) − ln(1+M)",

    fillcolor="#F8F1EC",
    color="#D1A98C"
)


with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("U1")
    s.node("U2")
    s.node("U3")


dot.edge(
    "U1",
    "U2",
    style="invis",
    weight="30"
)

dot.edge(
    "U2",
    "U3",
    style="invis",
    weight="30"
)


dot.edge("V", "U1")
dot.edge("Q", "U1")

dot.edge("M", "U2")
dot.edge("Q", "U2")

dot.edge("V", "U3")
dot.edge("M", "U3")


# ============================================================
# 第六阶段：控制变量
# ============================================================

CONTROL_FILL = "#D4E1EC"
CONTROL_BORDER = "#718CA3"
CONTROL_TEXT = "#263B4C"


dot.node(
    "C1",

    "U₁ 控制变量\n"
    "Z₁ = ln(1+V)",

    fillcolor=CONTROL_FILL,
    color=CONTROL_BORDER,
    fontcolor=CONTROL_TEXT,

    penwidth="1.45"
)


dot.node(
    "C2",

    "U₂ 控制变量\n"
    "Z₂ = ln(1+M)",

    fillcolor=CONTROL_FILL,
    color=CONTROL_BORDER,
    fontcolor=CONTROL_TEXT,

    penwidth="1.45"
)


dot.node(
    "C3",

    "U₃ 控制变量\n"
    "Z₃ = Lᵥₘ = [ln(1+V) + ln(1+M)] / 2",

    fillcolor=CONTROL_FILL,
    color=CONTROL_BORDER,
    fontcolor=CONTROL_TEXT,

    penwidth="1.45"
)


with dot.subgraph() as s:
    s.attr(rank="same")
    s.node("C1")
    s.node("C2")
    s.node("C3")


dot.edge(
    "C1",
    "C2",
    style="invis",
    weight="30"
)

dot.edge(
    "C2",
    "C3",
    style="invis",
    weight="30"
)


dot.edge("U1", "C1")
dot.edge("U2", "C2")
dot.edge("U3", "C3")


# ============================================================
# 第七阶段：XGBoost
# ============================================================

dot.node(
    "XGB1",

    "U₁ XGBoost\n"
    "Û₁ = f(XQ, Z₁)",

    fillcolor="#EDF2F7",
    color="#9FAEBC"
)


dot.node(
    "XGB2",

    "U₂ XGBoost\n"
    "Û₂ = f(XQ, Z₂)",

    fillcolor="#EDF2F7",
    color="#9FAEBC"
)


dot.node(
    "XGB3",

    "U₃ XGBoost\n"
    "Û₃ = f(XQ, Z₃)",

    fillcolor="#EDF2F7",
    color="#9FAEBC"
)


with dot.subgraph() as s:
    s.attr(rank="same")

    s.node("XGB1")
    s.node("XGB2")
    s.node("XGB3")


dot.edge(
    "XGB1",
    "XGB2",
    style="invis",
    weight="30"
)

dot.edge(
    "XGB2",
    "XGB3",
    style="invis",
    weight="30"
)


dot.edge("C1", "XGB1")
dot.edge("C2", "XGB2")
dot.edge("C3", "XGB3")


# Q筛选后的9项指标进入模型
dot.edge(
    "Qfilter",
    "XGB1",
    color="#B4C1BB"
)

dot.edge(
    "Qfilter",
    "XGB2",
    color="#B4C1BB"
)

dot.edge(
    "Qfilter",
    "XGB3",
    color="#B4C1BB"
)


# ============================================================
# 第八阶段：5折交叉验证
# ============================================================

dot.node(
    "CV",

    "5 折交叉验证\n"
    "评价模型泛化能力",

    fillcolor="#F1F3F5",
    color="#ADB3BA"
)


# ============================================================
# 为三个 XGBoost 设置独立的下方路由点
#
# 目的：
# 先强制连线从 XGBoost 方框底边垂直出去，
# 再由路由点汇入 5 折交叉验证。
#
# 避免 ortho 自动布线穿进 XGB1 / XGB3 方框内部。
# ============================================================

dot.node(
    "XGB1_ROUTE",
    "",
    shape="point",
    width="0.01",
    height="0.01",
    fixedsize="true",
    style="invis"
)

dot.node(
    "XGB2_ROUTE",
    "",
    shape="point",
    width="0.01",
    height="0.01",
    fixedsize="true",
    style="invis"
)

dot.node(
    "XGB3_ROUTE",
    "",
    shape="point",
    width="0.01",
    height="0.01",
    fixedsize="true",
    style="invis"
)


# 三个路由点处于同一水平层
with dot.subgraph() as s:
    s.attr(rank="same")

    s.node("XGB1_ROUTE")
    s.node("XGB2_ROUTE")
    s.node("XGB3_ROUTE")


# 保持三个路由点的左右顺序
dot.edge(
    "XGB1_ROUTE",
    "XGB2_ROUTE",
    style="invis",
    weight="50"
)

dot.edge(
    "XGB2_ROUTE",
    "XGB3_ROUTE",
    style="invis",
    weight="50"
)


# ============================================================
# 第一段：
# XGBoost 方框底边 → 各自下方路由点
#
# 这三条短线强制垂直向下
# ============================================================

dot.edge(
    "XGB1",
    "XGB1_ROUTE",

    tailport="s",

    arrowhead="none",

    color="#8A939D",
    penwidth="1.05",

    weight="100"
)

dot.edge(
    "XGB2",
    "XGB2_ROUTE",

    tailport="s",

    arrowhead="none",

    color="#8A939D",
    penwidth="1.05",

    weight="100"
)

dot.edge(
    "XGB3",
    "XGB3_ROUTE",

    tailport="s",

    arrowhead="none",

    color="#8A939D",
    penwidth="1.05",

    weight="100"
)


# ============================================================
# 第二段：
# 三个路由点 → 5折交叉验证
# ============================================================

dot.edge(
    "XGB1_ROUTE",
    "CV",

    color="#8A939D",
    penwidth="1.05",

    arrowsize="0.65",
    arrowhead="vee"
)

dot.edge(
    "XGB2_ROUTE",
    "CV",

    color="#8A939D",
    penwidth="1.05",

    arrowsize="0.65",
    arrowhead="vee"
)

dot.edge(
    "XGB3_ROUTE",
    "CV",

    color="#8A939D",
    penwidth="1.05",

    arrowsize="0.65",
    arrowhead="vee"
)


# ============================================================
# 第九阶段：模型评价指标 + TreeSHAP
# ============================================================

# ------------------------------------------------------------
# R²、RMSE、MAE 合并为一个方框
# ------------------------------------------------------------

dot.node(
    "Metrics",

    "模型评价指标\n"
    "决定系数 R²：R² = 1 − Σ(yᵢ − ŷᵢ)² / Σ(yᵢ − ȳ)²\n"
    "均方根误差 RMSE：RMSE = √[Σ(yᵢ − ŷᵢ)² / n]\n"
    "平均绝对误差 MAE：MAE = Σ|yᵢ − ŷᵢ| / n",

    fillcolor="#F7F7F7",
    color="#AEB4BC"
)


# ------------------------------------------------------------
# TreeSHAP
# ------------------------------------------------------------

dot.node(
    "SHAP",

    "TreeSHAP\n"
    "f(x) = φ₀ + Σφⱼ\n"
    "分解各Q底层指标对不配得性U的贡献",

    fillcolor="#F4F0F7",
    color="#B5A7BF"
)


# ------------------------------------------------------------
# Metrics 与 SHAP 并排
# ------------------------------------------------------------

with dot.subgraph() as s:
    s.attr(rank="same")

    s.node("Metrics")
    s.node("SHAP")


# 强制 Metrics 在左，TreeSHAP 在右
dot.edge(
    "Metrics",
    "SHAP",

    style="invis",
    weight="60"
)


# ------------------------------------------------------------
# CV 同时连接两个并排节点
# ------------------------------------------------------------

dot.edge(
    "CV:s",
    "Metrics:n"
)

dot.edge(
    "CV:s",
    "SHAP:n"
)


# ============================================================
# 第十阶段：SHAP蜂群图 + Dependence
# ============================================================

dot.node(
    "Bee",

    "SHAP 蜂群图\n"
    "识别单一指标重要性与贡献方向",

    fillcolor="#F4F0F7",
    color="#B5A7BF"
)


dot.node(
    "Dep",

    "SHAP Dependence + LOWESS\n"
    "Top3 单一指标响应形态\n"
    "非线性 / 平台期 / 拐点 / 潜在阈值",

    fillcolor="#FAF7FB",
    color="#C8B9D1"
)


dot.edge("SHAP", "Bee")


with dot.subgraph() as s:
    s.attr(rank="same")

    s.node("Bee")
    s.node("Dep")


dot.edge(
    "Bee",
    "Dep",

    style="dashed",
    color="#B8A8C2",

    constraint="false"
)


# ============================================================
# 第十一阶段：TreeSHAP Interaction + 真实U散点
# ============================================================

dot.node(
    "Inter",

    "TreeSHAP Interaction\n"
    "纵坐标 Iⱼₖ = mean(|φⱼₖ|)\n"
    "衡量两两指标的联合贡献强度",

    fillcolor="#F8EEF1",
    color="#C4A6AF"
)


dot.node(
    "Scatter",

    "真实 U 散点图\n"
    "检查真实不配得性分布\n"
    "与样本密度",

    fillcolor="#FCF7F8",
    color="#D2B5BD"
)


dot.edge("Bee", "Inter")


with dot.subgraph() as s:
    s.attr(rank="same")

    s.node("Inter")
    s.node("Scatter")


dot.edge(
    "Inter",
    "Scatter",

    style="dashed",
    color="#C5ADB5",

    constraint="false"
)


# ============================================================
# 第十二阶段：Top10 → Top1
# ============================================================

dot.node(
    "Top10",

    "Q-Q 两两指标组合排序\n"
    "Rankⱼₖ = mean(|φⱼₖ|)\n"
    "提取 Top10 组合",

    fillcolor="#F8EEF1",
    color="#C4A6AF"
)


dot.node(
    "Top1",

    "筛选 Top1 指标组合\n"
    "进入二维联合效应分析",

    fillcolor="#F8EEF1",
    color="#C4A6AF"
)


dot.edge("Inter", "Top10")
dot.edge("Top10", "Top1")


# ============================================================
# 第十三阶段：GAM Tensor + ALE
# ============================================================

dot.node(
    "GAM",

    "GAM Tensor\n"
    "Uₖ = β₀ + te(Xᵢ, Xⱼ) + Σₗ≠ᵢ,ⱼ s(Xₗ) + s(Zₖ) + ε\n"
    "分析Top1两指标的二维联合效应",

    fillcolor="#EEF5F5",
    color="#9EB7B7"
)


dot.node(
    "ALE",

    "二维二阶 ALE\n"
    "辅助验证 GAM 所揭示的\n"
    "局部联合效应",

    fillcolor="#F5F9F9",
    color="#B1C5C5"
)


dot.edge("Top1", "GAM")


with dot.subgraph() as s:
    s.attr(rank="same")

    s.node("GAM")
    s.node("ALE")


dot.edge(
    "GAM",
    "ALE",

    style="dashed",
    color="#AFC1C1",

    constraint="false"
)


# ============================================================
# 第十四阶段：不配得性构成项分解
# ============================================================

dot.node(
    "Decomp",

    "不配得性构成项分解\n"
    "比较不配得性两端构成项的变化",

    fillcolor="#EEF5F5",
    color="#9EB7B7"
)


dot.edge("GAM", "Decomp")


# ============================================================
# 第十五阶段：U₁ / U₂ / U₃ 构成项
# ============================================================

dot.node(
    "D_U1",

    "U₁ 构成项\n"
    "U₁ = ln(1+V) − ln(1+Q)\n"
    "V端 ↔ Q端",

    fillcolor="#F4F6F6",
    color="#B7C1C1"
)


dot.node(
    "D_U2",

    "U₂ 构成项\n"
    "U₂ = ln(1+M) − ln(1+Q)\n"
    "M端 ↔ Q端",

    fillcolor="#F4F6F6",
    color="#B7C1C1"
)


dot.node(
    "D_U3",

    "U₃ 构成项\n"
    "U₃ = ln(1+V) − ln(1+M)\n"
    "V端 ↔ M端",

    fillcolor="#F4F6F6",
    color="#B7C1C1"
)


with dot.subgraph() as s:
    s.attr(rank="same")

    s.node("D_U1")
    s.node("D_U2")
    s.node("D_U3")


dot.edge(
    "D_U1",
    "D_U2",
    style="invis",
    weight="30"
)

dot.edge(
    "D_U2",
    "D_U3",
    style="invis",
    weight="30"
)


dot.edge("Decomp", "D_U1")
dot.edge("Decomp", "D_U2")
dot.edge("Decomp", "D_U3")


# ============================================================
# 第十六阶段：综合解释
# ============================================================

dot.node(
    "Result",

    "综合解释\n"
    "单指标效应 · 两两组合效应 · 不配得性形成机制",

    fillcolor="#E9EFF4",
    color="#97A6B3",

    penwidth="1.35"
)


dot.edge("D_U1", "Result")
dot.edge("D_U2", "Result")
dot.edge("D_U3", "Result")


# ============================================================
# 第十七阶段：输出
# ============================================================

# PNG
dot.format = "png"

dot.render(
    "algorithm_flowchart_text",
    cleanup=True
)


# SVG
dot.format = "svg"

dot.render(
    "algorithm_flowchart_text",
    cleanup=True
)


print("流程图生成完成：")
print("algorithm_flowchart_text.png")
print("algorithm_flowchart_text.svg")