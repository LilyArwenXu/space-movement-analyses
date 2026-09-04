import json  # 导入内置的 json 模块，用于处理 Python 对象与 JSON 字符串之间的序列化和反序列化
import re  # 导入内置的正则表达式模块，用于文本清洗、模式匹配和提取路名
import pandas as pd  # 导入第三方数据分析库 pandas，并简写为 pd，用于表格数据的读取和处理

# 1. 读取 CSV 文件（跳过前2行说明，第3行为实际表头）
csv_file_path = (
    '巨富长街区调研全量总表.csv'  # 定义要读取的 CSV 数据文件路径
)
df = pd.read_csv(
    csv_file_path, header=2
)  # 使用 pandas 读取 CSV 文件，跳过前 2 行说明文字，将第 3 行设为实际的列名

# 清理并过滤无效数据
df = df.dropna(
    subset=['完整地址']
)  # 筛除“完整地址”列中包含空值（NaN）的行，保证后续处理的数据均含有地址
df['行人样本数'] = (
    pd.to_numeric(df['行人样本数'], errors='coerce').fillna(0)
)  # 将“行人样本数”列强制转换为数值类型，无法转换的异常值转为 NaN 并统一填充为 0
df['界面整体状态'] = (
    pd.to_numeric(df['界面整体状态'], errors='coerce').fillna(0)
)  # 将“界面整体状态”列强制转换为数值类型，无法转换的转为 0


def extract_road_name(address):
  """精准提取“街道”二字之后的纯路名字段（如：'汾阳路'、'永嘉路'、'安福路'等）"""
  if pd.isna(address):  # 如果传入的地址为空值（NaN）
    return '未知道路'  # 返回默认标识“未知道路”

  addr_str = str(address)  # 将地址转换为字符串类型
  if '街道' in addr_str:  # 如果地址文本中包含“街道”关键字
    after_street = addr_str.split('街道')[
        -1
    ]  # 按照“街道”进行切分，只取最后一部分（即街道名称后面的地址段）
  else:
    after_street = addr_str  # 如果没有“街道”关键字则保持原样

  # 使用正则表达式从后方文本中精准匹配出以“路”、“街”、“巷”、“大道”等结尾的纯路名
  match = re.search(r'([\u4e00-\u9fa5]+?(?:[东南西北]路|路|街|巷|大道))', after_street)
  if match:
    return match.group(1).strip()  # 成功匹配则返回提取到的纯路名（如“汾阳路”）

  return '其他道路'  # 如果未匹配到符合规范的路名则统一归为“其他道路”


df['道路'] = df['完整地址'].apply(
    extract_road_name
)  # 对“完整地址”列逐行应用上述自定义函数，生成分类用的“道路”列

# 2. 按道路分组统计点位
grouped = df.groupby('道路')  # 按照新生成的“道路”列对 DataFrame 中的数据进行分组
max_points_count = max(
    len(group) for _, group in grouped
)  # 计算所有道路分组中包含点位数量最多的那条路的点位数，用于后续动态确定坐标轴边界
STEP = (
    0.0005  # 定义同轴各个点位之间的横坐标固定间距步长，使点在轴上分布更集中
)

# 3. 计算各点位居中对齐后的坐标
streets_data = {}  # 初始化一个空字典，用于存放每条道路对应的点位坐标及详细信息列表
for road, group in grouped:  # 遍历每一个道路分组（road为道路名, group为对应的数据行集合）
  points = (
      []
  )  # 初始化临时列表，用来存放当前道路下各个点位的详细信息字典
  for _, row in group.iterrows():  # 遍历当前道路分组中的每一行数据
    full_addr = str(row['完整地址'])  # 获取当前行的完整地址字符串
    short_addr = (
        full_addr.split('街道')[-1] if '街道' in full_addr else full_addr
    )  # 截取“街道”后面的精简地址，用于后续悬浮提示展示

    points.append({
        'full_address': full_addr,  # 字典保存当前点位的完整地址
        'short_address': short_addr,  # 字典保存当前点位的精简地址
        'count': float(row['行人样本数']),  # 字典保存转换成浮点数的行人样本数
        'status': float(row['界面整体状态']),  # 字典保存转换成浮点数的界面整体状态值
    })

  n = len(points)  # 获取当前道路包含的点位总数
  start_x = (
      -((n - 1) * STEP) / 2.0
  )  # 计算当前道路点位在横轴上的起始位置，使其以坐标原点 0 对称居中分布

  data_list = (
      []
  )  # 初始化一个列表，用于存放当前道路中所有点位最终组装好的数据数组
  for i, pt in enumerate(points):  # 遍历当前道路的每个点位及其对应的索引
    x_val = start_x + i * STEP  # 依次计算当前点位排布后的具体横坐标值
    # 计算当前点位在该街道点位中的“区位比例”（即当前索引 / 总点位数，若总数仅1个则比例设为0.5）
    ratio = (i / (n - 1)) if n > 1 else 0.5
    # 存储格式: [x轴位置, 行人样本数, 短地址, 完整地址, 界面整体状态, 区位比例]
    data_list.append([
        x_val,
        pt['count'],
        pt['short_address'],
        pt['full_address'],
        pt['status'],
        ratio,
    ])

  streets_data[road] = (
      data_list  # 将当前道路的所有点位数据列表存入总字典中，键为道路名
  )

max_bound = (
    max_points_count * STEP
) / 1.8 + STEP  # 根据最大点位数计算单轴的边界极值，确保视图两侧留白合理
res_data = {
    'axisBounds': {
        'min': -max_bound,
        'max': max_bound,
    },  # 定义所有单轴坐标的统一最小和最大边界
    'streets': streets_data,  # 挂载处理好的各道路点位数据字典
}

# 4. 生成 HTML
json_str = json.dumps(
    res_data, ensure_ascii=False
)  # 将 Python 整理好的结构化数据转换为标准的 JSON 字符串，并保持中文字符不乱码

html_template = """<!DOCTYPE html>
<html lang="zh-CN" style="height: 100%">
<head>
  <meta charset="utf-8">
  <title>巨富长街区各道路点位行人样本与状态关联分析图</title>
  <!-- 引入 ECharts CDN -->
  <script src="https://fastly.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
</head>
<body style="height: 100%; margin: 0; background-color: #f8fafc;">
  <!-- 根据道路的数量，将容器高度设为 2000px，确保纵向空间充裕、不挤压 -->
  <div id="main" style="height: 2000px; width: 100%;"></div>

  <script type="text/javascript">
    const resData = __DATA_JSON__; // 注入上一步由 Python 生成并转换的 JSON 数据常量

    // 采用明亮温和的莫兰迪色系搭配数组
    const colorPalette = [
      '#8EA89D', '#D4A373', '#D4A5A5', '#8EAA90', '#B5838D', 
      '#E5989B', '#6D8299', '#B4C5E4', '#938BA1', '#E3CAA5', '#CEAB93'
    ]; // 定义多色板，用于循环渲染不同道路散点的颜色

    const streetsData = resData.streets; // 从总数据中获取道路点位集合
    const bounds = resData.axisBounds; // 获取坐标轴统一边界
    const streets = Object.keys(streetsData); // 获取所有道路名称构成的数组
    const count = streets.length; // 获取道路总条数

    const singleAxisList = []; // 初始化左侧单轴配置数组
    const gridList = [];       // 初始化右侧小散点图的网格(grid)数组
    const xAxisList = [];      // 初始化右侧小散点图的横坐标(xAxis)数组
    const yAxisList = [];      // 初始化右侧小散点图的纵坐标(yAxis)数组
    const seriesList = [];     // 初始化图表系列(series)数组
    const graphicList = [];    // 初始化图形文本与方框标签数组

    streets.forEach((street, idx) => {
      // 计算当前道路行距离顶部的百分比位置
      const topPercent = (idx + 1) * (90 / (count + 1)) + 5; 
      const currentColor = colorPalette[idx % colorPalette.length]; // 获取当前道路对应的莫兰迪颜色

      // 1. 第一个图：左侧单轴 (SingleAxis) 配置（占 60% 宽度，单轴起始留出文本空间，右边界终止于 40.5%）
      singleAxisList.push({
        type: 'value',
        min: bounds.min,
        max: bounds.max,
        top: topPercent + '%',
        height: '0%',
        left: 250,      // 单轴从 250px 处开始绘制，为左侧 120px 处起的路名文本留足空间
        right: '50%',  // 单轴右边界终止于区域处
        axisLabel: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLine: {
          lineStyle: {
            color: '#ccd6e0',
            width: 1.5
          }
        }
      });

      // 2. 左侧主散点 (行人样本数) 配置
      seriesList.push({
        singleAxisIndex: idx,
        coordinateSystem: 'singleAxis',
        type: 'scatter',
        data: streetsData[street],
        symbolSize: function (dataItem) {
          const val = dataItem[1];
          return Math.max(Math.sqrt(val) * 12, 8);
        },
        itemStyle: {
          color: currentColor,
          opacity: 0.5,
          shadowBlur: 4,
          shadowColor: 'rgba(0, 0, 0, 0.1)'
        },
        emphasis: {
          itemStyle: {
            opacity: 1,
            borderColor: '#333',
            borderWidth: 2
          }
        }
      });

      // 3. 左侧附加散点 (“界面整体状态”) 配置：深色空心圆圈
      seriesList.push({
        singleAxisIndex: idx,
        coordinateSystem: 'singleAxis',
        type: 'scatter',
        data: streetsData[street],
        symbolSize: function (dataItem) {
          const statusVal = dataItem[4];
          return Math.max(statusVal * 4, 2);
        },
        itemStyle: {
          color: 'transparent',
          borderColor: '#1e293b',
          borderWidth: 0.5,
          opacity: 0.6
        },
        emphasis: {
          itemStyle: {
            borderColor: '#0f172a',
            borderWidth: 2,
            opacity: 1
          }
        }
      });

      // 4. 轴左侧道路名称标签配置 (明确距离页面左侧 120px)
      graphicList.push({
        type: 'text',
        left: 120, // 路名标签距左边缘固定 120px
        top: topPercent + '%',
        style: {
          text: street,
          font: 'bold 13px sans-serif',
          fill: '#333',
          textAlign: 'left',
          textVerticalAlign: 'middle'
        }
      });

      const gridTopPx = (topPercent / 100) * 2000 - 25; // 居中微调高度

      // 5. 第二个图：中间小散点图配置 (X=界面整体状态, Y=行人样本数，占 14% 宽度：从 60.5% 到 74.5%)
      gridList.push({
        left: '55%',
        width: '14%',
        top: gridTopPx + 'px',
        height: '50px'
      });

      xAxisList.push({
        gridIndex: idx * 2,
        type: 'value',
        min: 0,
        max: 5,
        axisLabel: { show: false },
        axisTick: { show: false },
        axisLine: { show: true },
        splitLine: { show: true }
      });

      yAxisList.push({
        gridIndex: idx * 2,
        type: 'value',
        axisLabel: { show: false },
        axisTick: { show: false },
        axisLine: { show: true },
        splitLine: { show: false }
      });

      const subScatterData1 = streetsData[street].map(item => [item[4], item[1], item[2], item[3]]);
      seriesList.push({
        xAxisIndex: idx * 2,
        yAxisIndex: idx * 2,
        type: 'scatter',
        data: subScatterData1,
        symbolSize: 6,
        itemStyle: { color: currentColor, opacity: 0.8 }
      });

      graphicList.push({
        type: 'rect',
        left: '60.5%',
        width: '14%',
        top: gridTopPx + 'px',
        shape: { height: 50, r: 0 },
        style: { stroke: '#cbd5e1', fill: '#ffffff', lineWidth: 1 }
      });

      // 6. 第三个图：右侧回归分析图配置（横坐标改为区位比例: 0 ~ 1）
      gridList.push({
        left: '75.5%',
        right: 120, // 整体图最右侧留空 120px
        top: gridTopPx + 'px',
        height: '50px'
      });

      xAxisList.push({
        gridIndex: idx * 2 + 1,
        type: 'value',
        min: 0,   // 区位比例最小值为 0
        max: 1,   // 区位比例最大值为 1
        axisLabel: { show: false },
        axisTick: { show: false },
        axisLine: { show: true },
        splitLine: { show: true }
      });

      yAxisList.push({
        gridIndex: idx * 2 + 1,
        type: 'value',
        axisLabel: { show: false },
        axisTick: { show: false },
        axisLine: { show: true },
        splitLine: { show: false }
      });

      // 提取第三个图的数据：X轴为区位比例(item[5])，Y轴为(样本数/状态评分，若状态为0则为0，对应 item[4] === 0 ? 0 : item[1] / item[4])
      const subScatterData2 = streetsData[street].map(item => [
        item[5],                                     // 数组第一个元素：区位比例 (0~1)
        item[4] === 0 ? 0 : item[1] / item[4],       // 数组第二个元素：样本/状态(Y)
        item[2],                                     // 短地址
        item[3],                                     // 完整地址
        item[1],                                     // 行人样本数
        item[4]                                      // 界面整体状态
      ]);

      // 计算线性回归曲线参数 (y = slope * x + intercept)
      let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0, nPts = subScatterData2.length;
      subScatterData2.forEach(pt => {
        sumX += pt[0];
        sumY += pt[1];
        sumXY += pt[0] * pt[1];
        sumXX += pt[0] * pt[0];
      });
      let slope = 0, intercept = sumY / (nPts || 1);
      if (nPts > 1) {
        let num = sumXY - (sumX * sumY) / nPts;
        let den = sumXX - (sumX * sumX) / nPts;
        if (den !== 0) {
          slope = num / den;
          intercept = (sumY - slope * sumX) / nPts;
        }
      }
      let regLineData = [
        [0, slope * 0 + intercept],   // 回归线起点（区位比例 0）
        [1, slope * 1 + intercept]    // 回归线终点（区位比例 1）
      ];

      seriesList.push({
        xAxisIndex: idx * 2 + 1,
        yAxisIndex: idx * 2 + 1,
        type: 'scatter',
        data: subScatterData2,
        symbolSize: 6,
        itemStyle: { color: currentColor, opacity: 0.4 }
      });

      seriesList.push({
        xAxisIndex: idx * 2 + 1,
        yAxisIndex: idx * 2 + 1,
        type: 'line',
        data: regLineData,
        symbol: 'none',
        lineStyle: { color: currentColor, width: 1, type: 'dashed' }
      });

      graphicList.push({
        type: 'rect',
        left: '75.5%',
        right: 120, // 背景方框右边缘同样留空 120px
        top: gridTopPx + 'px',
        shape: { height: 50, r: 0 },
        style: { stroke: '#cbd5e1', fill: '#ffffff', lineWidth: 1 }
      });
    });

    const chartDom = document.getElementById('main'); // 获取 HTML 中用于渲染图表的 DOM 容器
    const myChart = echarts.init(chartDom); // 初始化 ECharts 实例

    const option = {
      title: {
        text: '巨富长街区 - 行人样本数与界面整体状态关联分析', // 图表主标题
        // 副标题使用反引号支持多行文字，并且通过居中对齐排布成 3 排
        subtext: `左侧：点位单轴分布（空心圈：界面整体状态评分 | 实体圈：行人样本数)
中间：状态(X) - 样本(Y) 关联散点图
右侧：区位比例(X) - 样本/状态(Y) 分布及回归趋势线（区位比例=点位序号/点位总数）`,
        left: 'center',
        top: '12px',
        textStyle: { fontSize: 18, fontWeight: 'bold', color: '#1e293b' },
        subtextStyle: { lineHeight: 18, color: '#64748b' }
      },
      tooltip: {
        trigger: 'item',
        formatter: function (params) {
          if (params.seriesType === 'scatter') {
            const val = params.value;
            if (val.length === 5) {
              return `<b>${val[3]}</b><br/>行人样本数: <b style="color:#ee6666">${val[1]}</b> 人<br/>界面整体状态: <b style="color:#2563eb">${val[4]}</b>`;
            } else if (val.length === 6) {
              return `<b>${val[3]}</b><br/>区位比例(X): <b style="color:#2563eb">${val[0].toFixed(2)}</b><br/>样本/状态(Y): <b style="color:#ee6666">${val[1].toFixed(2)}</b><br/>样本数: ${val[4]} | 状态: ${val[5]}`;
            } else if (val.length === 4) {
              return `<b>${val[3]}</b><br/>界面整体状态(X): <b style="color:#2563eb">${val[0]}</b><br/>行人样本数(Y): <b style="color:#ee6666">${val[1]}</b>`;
            }
          } else if (params.seriesType === 'line') {
            return `回归趋势线`;
          }
          return '';
        }
      },
      graphic: graphicList, // 引入图形标签及方框
      singleAxis: singleAxisList, // 引入左侧单轴配置
      grid: gridList,             // 引入右侧小散点图网格
      xAxis: xAxisList,           // 引入右侧横坐标
      yAxis: yAxisList,           // 引入右侧纵坐标
      series: seriesList          // 引入所有散点与折线系列
    };

    myChart.setOption(option); // 将配置项加载并渲染到图表中
    window.addEventListener('resize', () => myChart.resize()); // 监听窗口大小变化自适应缩放
  </script>
</body>
</html>
"""

html_content = html_template.replace(
    '__DATA_JSON__', json_str
)  # 将 HTML 模板中的占位符替换为实际生成的 JSON 数据字符串

output_html_path = 'scatter_single_axis.html'  # 定义最终输出的 HTML 文件名
with open(output_html_path, 'w', encoding='utf-8') as f:
  f.write(html_content)  # 以 UTF-8 编码将完整的 HTML 内容写入到本地文件中

print(
    f'成功生成图表 HTML: {output_html_path}'
)  # 在控制台打印成功提示信息，告知用户 HTML 文件已生成