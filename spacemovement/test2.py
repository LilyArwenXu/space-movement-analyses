import json
import re
import pandas as pd

# 1. 读取 CSV 数据文件（与 test1.py 保持一致：跳过前2行说明，第3行为实际表头）
csv_file_path = '巨富长街区调研全量总表.csv'
df = pd.read_csv(csv_file_path, header=2)

# 清理无效数据并复制
df = df.dropna(subset=['完整地址']).copy()


def extract_road_name(address):
  """精准提取“街道”二字之后的纯路名字段（完全沿用 test1.py 中的定义）"""
  if pd.isna(address):
    return '未知道路'

  addr_str = str(address)
  if '街道' in addr_str:
    after_street = addr_str.split('街道')[-1]
  else:
    after_street = addr_str

  match = re.search(r'([\u4e00-\u9fa5]+?(?:[东南西北]路|路|街|巷|大道))', after_street)
  if match:
    return match.group(1).strip()

  return '其他道路'


df['道路'] = df['完整地址'].apply(extract_road_name)

# 2. 对应 6 项界面节点评价指标字段
# 对应 CSV 字段名：界面开放度、临街互动性、视觉丰富度、历史感知度、遮荫率(%)、路面状态
csv_indicator_cols = [
    '界面开放度',
    '临街互动性',
    '视觉丰富度',
    '历史感知度',
    '遮荫率(%)',
    '路面状态',
]
display_names = [
    '界面开放度',
    '临界互动性',
    '视觉丰富度',
    '历史感知度',
    '遮阴率',
    '路面状态',
]

# 将数值列强制转为数值类型，非数值转为 0
for col in csv_indicator_cols:
  df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# 将“遮荫率(%)”(0-100%) 缩放到 0-5 分制，确保与其余 5 项指标维度量纲一致
df['遮阴率_scaled'] = df['遮荫率(%)'] / 20.0

scaled_cols = [
    '界面开放度',
    '临街互动性',
    '视觉丰富度',
    '历史感知度',
    '遮阴率_scaled',
    '路面状态',
]

# 3. 按街道分组统计各指标均值
grouped = df.groupby('道路')[scaled_cols].mean()
grouped['total'] = grouped.sum(axis=1)

# 过滤全 0 数据并按综合得分升序排列，使图表呈现良好的纵向梯队层级
grouped = grouped[grouped['total'] > 0].sort_values(by='total', ascending=True)

roads = grouped.index.tolist()

# 组装 ECharts series 数据列表
series_dict = {}
for i, col in enumerate(scaled_cols):
  disp_name = display_names[i]
  series_dict[disp_name] = [round(val, 2) for val in grouped[col].tolist()]

chart_data = {'roads': roads, 'series': series_dict}

json_str = json.dumps(chart_data, ensure_ascii=False)

# 4. 嵌入并生成 ECharts 堆叠条形图 HTML 文件
html_template = """<!DOCTYPE html>
<html lang="zh-CN" style="height: 100%">
<head>
  <meta charset="utf-8">
  <title>巨富长街区各街道界面评价权重与构成差异分析</title>
  <!-- 引入 ECharts 5 CDN -->
  <script src="https://fastly.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
</head>
<body style="height: 100%; margin: 0; background-color: #f8fafc;">
  <div id="container" style="height: 100%; width: 100%;"></div>

  <script type="text/javascript">
    const resData = __DATA_JSON__;

    const dom = document.getElementById('container');
    const myChart = echarts.init(dom);

    // 采用 test1.py 同款莫兰迪调配色系
    const colors = ['#8EA89D', '#D4A373', '#D4A5A5', '#8EAA90', '#B5838D', '#6D8299'];
    const categories = ['界面开放度', '临界互动性', '视觉丰富度', '历史感知度', '遮阴率', '路面状态'];

    // 参照 bar-y-category-stack.html 结构构建堆叠系列，并加入透明度样式
    const seriesList = categories.map((name, idx) => ({
      name: name,
      type: 'bar',
      stack: 'total', // 开启横向堆叠
      label: {
        show: true,
        fontSize: 11,
        color: '#ffffff',
        formatter: function (params) {
          return params.value > 0.4 ? params.value.toFixed(1) : '';
        }
      },
      emphasis: { focus: 'series' },
      itemStyle: { 
        color: colors[idx],
        opacity: 0.6 
      },
      data: resData.series[name]
    }));

    const option = {
      title: {
        text: '巨富长街区 - 不同街道节点界面评价权重与构成差异分析',
        subtext: '界面整体状态由六项维度加权决定（各项满分5分，遮阴率已等比换算为5分制，悬浮可查看具体权重占比）',
        left: 'center',
        top: '20px',
        textStyle: { fontSize: 18, fontWeight: 'bold', color: '#1e293b' },
        subtextStyle: { fontSize: 12, color: '#64748b' }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: function (params) {
          let total = params.reduce((sum, p) => sum + p.value, 0);
          let html = `<div style="font-weight:bold;margin-bottom:6px;border-bottom:1px solid #eee;padding-bottom:4px;">${params[0].name}</div>`;
          html += `<div style="font-size:12px;color:#64748b;margin-bottom:6px;">综合评估加权总分: <b style="color:#0f172a">${total.toFixed(2)}</b> / 30 分</div>`;
          params.forEach(p => {
            let percent = total > 0 ? ((p.value / total) * 100).toFixed(1) : '0.0';
            html += `<div style="display:flex;justify-content:space-between;align-items:center;gap:15px;margin:3px 0;font-size:12px;">
              <span>${p.marker} ${p.seriesName}</span>
              <span style="font-weight:bold;">${p.value.toFixed(2)} 分 <span style="color:#64748b;font-weight:normal;">(权重 ${percent}%)</span></span>
            </div>`;
          });
          return html;
        }
      },
      legend: {
        top: '65px',
        data: categories,
        textStyle: { color: '#334155' }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        top: '110px',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '加权综合得分 (满分30分)',
        nameLocation: 'middle',
        nameGap: 30,
        splitLine: { lineStyle: { type: 'dashed', color: '#cbd5e1' } }
      },
      yAxis: {
        type: 'category',
        data: resData.roads,
        axisLabel: { fontSize: 12, color: '#334155' }
      },
      series: seriesList
    };

    myChart.setOption(option);
    window.addEventListener('resize', () => myChart.resize());
  </script>
</body>
</html>
"""

html_content = html_template.replace('__DATA_JSON__', json_str)

# 写入文件
output_html_path = 'street_interface_weights.html'
with open(output_html_path, 'w', encoding='utf-8') as f:
  f.write(html_content)

print(f'分析图表已成功生成: {output_html_path}')