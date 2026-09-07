# Inclusive Vitality

当前封面有调研网页、数据采集、类型划分（暂空）、宏观行为分析、微观行为分析五个入口。宏观目录为八个白底图表，数据采集内含目录PDF及两张源表。运行 `python scripts/build_site.py` 更新全站，同时重建根目录的 `data_extract.csv`；统计公式见 [METHODS.md](METHODS.md)，当前可编辑Python文件在 `chart_python/current`。

## GitHub Pages 发布

网站已经生成，不需要在 GitHub 上安装 Python 或运行分析脚本。

1. 将 **完整的 `docs` 文件夹** 上传到仓库 `LilyArwenXu/space-movement-analyses` 的 `main` 分支，并提交。不要只上传 `index.html`。
2. 进入仓库 **Settings → Pages → Build and deployment**。
3. Source 选择 **Deploy from a branch**。
4. Branch 选择 **main**，目录选择 **/docs**，点击 **Save**。
5. 等待 GitHub 的 Pages 部署完成，以 Settings → Pages 显示的网站链接为准。

未设置自定义域名时，本仓库的默认网站地址为：

https://lilyarwenxu.github.io/space-movement-analyses/

不要省略网址中的 `/space-movement-analyses/`。发布来源选为 `/docs` 后，访问网址不需要再加 `/docs/`。

官方说明：https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## 文件归类

| 目录或文件 | 用途 |
| --- | --- |
| `docs/index.html` | 正式发布首页 |
| `docs/visualizations.html` | 八个入口的风琴目录 |
| `docs/behavior-analysis.html` | 行为分析页面 |
| `docs/assets/` | 样式、背景图片与字体 |
| `docs/spacemovement/` | 八个当前图表页面、保留的历史图表与图表库 |
| `docs/.nojekyll` | 直接按静态文件发布 |
| `index.html` | 根目录兼容入口，跳转到 `docs/index.html` |
| `aerial/` | 网站页面源文件，后续样式修改在这里进行 |
| `spacemovement/` | 图表源文件、原始工作簿与参考材料 |
| `scripts/` | 数据处理、构建与检查脚本 |
| `dist/` | 原有 Sites 发布输出，继续保留 |
| `.openai/` | 原有 Sites 配置，与 GitHub Pages 发布无关 |
| `.build-deps/`、`.site-build/` | 本地依赖、临时文件与发布压缩包，已忽略提交 |

`docs/` 自带所有运行必需的文件；工作簿、Word 文档和 Python 脚本不需要放进发布目录。

## 后续更新

只改静态页面且 `dist/` 已同步时，运行 `python scripts/prepare_pages.py` 更新 `docs/`。

更新源页面或原始表格后，先安装 `scripts/requirements.txt` 中的依赖，再运行 `python scripts/build_site.py`，会依次更新 `aerial/`、`dist/`、`docs/` 和 `.site-build/github-pages.zip`。

生成的压缩包里 `index.html` 位于顶层，适合解压后单独作为静态站点上传。使用本仓库时优先采用上面的 `main /docs` 发布方式。

如果误将 Pages 配置成 `main /(root)`，根目录入口也会跳转到网站，但推荐改回 `/docs`，让发布范围只包含网站文件。

07–11 栏的人群图表来自工作簿的“行人信息总表（0905）”；10 栏的空间指标按点位 ID 关联“全量总表(0906)”。居民指数、游客指数取点位内行人原始指数的均值；身份倾向按两项指数高低分类，不代表真实居住身份。点位置信区间的最低样本量为5，相关矩阵不做FDR校正。

12 栏按全量总表中的全部135条有效点位记录，按完整功能类型分组，分别计算消费水平、消费空间占比和承载人数的有效值均值；复合功能作为独立类型，避免重复统计。

13 栏为“代际偏好推演，非历史实测”：当前年长群体行为按明确列出的优先规则映射为原初功能假设，再连接至该点位的当前功能类型。它不能验证20年前的实际用途，历史实测版本需要点位与历史功能的对照资料。详细规则保存在图表副标题和生成数据的 memoryMethod 中。

栏目顺序由 `scripts/catalog.py` 统一维护；旧点位年龄构成地址会跳转到人群构成的第二个选项卡。
