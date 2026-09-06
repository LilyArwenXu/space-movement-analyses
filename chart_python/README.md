# 可修改的 Python 图表备份

01–14 各对应一个风琴栏目。使用 Python 3 运行，无需安装额外绘图库。

例如修改 `04_comfort.py` 后，在本文件夹运行：

```powershell
python 04_comfort.py
```

每份文件的 `HTML` 是页面结构，`JAVASCRIPT` 是完整的 ECharts 绘图代码（保存在 Python 多行字符串内）。可直接搜索副标题文字、`symbolSize`、`grid`、`series`、`fontFamily` 修改；图形依然由浏览器中的 ECharts 渲染，并非 Matplotlib。02 的绘图代码在 `HTML` 内。

对应绘图函数：01 `heat`；02 `option`；03 `scatter`；04 `scatter` 及 `if(page===6)`；05 `single`；06 `scatter`；07 `confidence`；08 `radar`；09 `lorenz`；10 `relations`；11 `stacked/ageHeat`；12 `economy`；13 `memory`；14 `report/correlationMatrix`。共享函数的备份彼此独立，修改一个文件只改变对应栏目。

运行后更新 `spacemovement`、`aerial/spacemovement`、`dist/spacemovement`、`docs/spacemovement` 的对应 HTML，并重新打包 `.site-build/github-pages.zip`。浏览器刷新后查看；GitHub Pages 需提交更新的 `docs` 文件夹。

源工作簿更新后，在项目根目录运行 `python scripts/build_site.py`，会重算源数据、更新记录数，并应用这里的全部自定义绘图代码，不覆盖手动修改的 Python 文件。数据重算需要项目原有的 NumPy/SciPy 环境。单独修改样式后运行栏目文件，不需要重新计算数据。

请保留 `_export.py` 和项目目录结构。`scripts/create_chart_editors.py` 仅创建缺失的备份，不会覆盖已有文件。
