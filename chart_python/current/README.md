# 当前八个白底图表的 Python 编辑文件

修改编号 01–08 文件内的 `JAVASCRIPT` 绘图代码后，运行对应 Python 文件即可更新网页、`docs` 和发布包。每份代码独立；日后刷新数据不会覆盖这里的修改。图表用 ECharts/HTML/SVG 渲染，Python 负责生成页面。

```powershell
python 01_address_people_heatmaps.py
```

数据处理、类别展开、评分权重、筛选阈值和 `data_extract.csv` 的生成统一位于 `scripts/build_inclusive_data.py`。修改工作簿后，在项目根目录运行 `python scripts/build_site.py`，重算整个网站。可优先使用工作表精确名称“全量总表”和“行人信息总表”；若不存在，则继续使用“全量总表(0906)”和“行人信息总表（0905）”。

源工作簿不被修改；地图以 `point_id` 关联135个点位，不按相同地址合并。目录 PDF 从 `spacemovement/目录索引*.pdf` 读取并生成网页页图。原目录中的14份 Python 是历史备份，当前网页请用此目录。

评分是本次新增的等权方案，可在数据处理文件中调整；不是既有研究的既定权重。详情参见项目 `METHODS.md`。
