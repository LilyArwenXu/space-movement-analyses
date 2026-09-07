# 衡复历史街区地图与点位位置数据包

本数据包用于后续网页可视化制作。数据读取自当前网站 [衡复历史街区人因数据调研分析](https://hfinvestigation.site/)，导出日期为 2026-09-07，共 135 个点位。

## 文件说明

| 文件 | 用途 |
|---|---|
| `hengfu-base-map.jpg` | 网站当前使用的高清位图底图，尺寸 6144 × 4340 px |
| `hengfu-base-map.svg` | 可缩放矢量底图，适合网页和设计软件 |
| `hengfu-base-map-vector.pdf` | 矢量 PDF 底图，适合 Illustrator 等软件 |
| `points.json` | 推荐的网页数据源，包含元数据和全部点位 |
| `points.js` | 与 JSON 内容一致，可直接用 `<script>` 引入，便于本地双击示例 |
| `points.xlsx` | 便于人工核对、筛选和转交的点位表 |
| `example.html` | 不依赖框架的网页叠加示例，可直接双击打开 |

## 坐标系统

`x_percent` 和 `y_percent` 是相对于配套底图的百分比坐标，原点在底图左上角：

- `x_percent = 0`：底图最左侧；`100`：最右侧。
- `y_percent = 0`：底图最上方；`100`：最下方。
- 这些值不是经纬度，也不是 Web Mercator 坐标。
- 必须保持地图原始宽高比，点位才能与底图正确重合。

网页中的推荐定位方式：

```css
.map {
  position: relative;
  aspect-ratio: 6144 / 4340;
}
.map > img {
  display: block;
  width: 100%;
  height: 100%;
}
.marker {
  position: absolute;
  transform: translate(-50%, -50%);
}
```

```js
marker.style.left = point.x_percent + "%";
marker.style.top = point.y_percent + "%";
```

Canvas 或像素坐标换算：

```js
const xPx = imageWidth  * point.x_percent / 100;
const yPx = imageHeight * point.y_percent / 100;
```

## 点位字段

| 字段 | 类型 | 含义 |
|---|---|---|
| `sequence` | integer | 按“街道 → 道路 → 完整地址”整理的交付序号 |
| `point_id` | string | 网站中的稳定点位 ID；后续关联其他研究数据时建议作为主键 |
| `name` | string | 点位名称 |
| `full_address` | string | 完整地址 |
| `district` | string | 行政区 |
| `subdistrict` | string | 街道 |
| `road` | string | 道路 |
| `x_percent` | number | 相对底图左侧的百分比 |
| `y_percent` | number | 相对底图顶部的百分比 |

## 网页接入方式

生产项目中推荐读取 `points.json`：

```js
const { points } = await fetch("/data/points.json").then(r => r.json());

for (const point of points) {
  const marker = document.createElement("button");
  marker.className = "marker";
  marker.style.left = `${point.x_percent}%`;
  marker.style.top = `${point.y_percent}%`;
  marker.title = `${point.name}｜${point.full_address}`;
  map.append(marker);
}
```

如果直接在电脑上双击 HTML，浏览器通常会限制本地 `fetch`。本包的 `example.html` 改用 `points.js`，因此可直接打开。正式网站仍建议使用 JSON。

## 重要说明

1. 该套坐标只对应本包所附底图；裁切底图、改变可视区域或不保持宽高比都会造成错位。
2. 如需把点位放到高德、百度、Mapbox、Leaflet 的真实地理底图上，还需另做地理配准或地址地理编码，不能把百分比坐标直接当作经纬度。
3. 本包只包含地图和点位定位所需字段，不包含照片、空间指标、行人记录、问卷或分类研究数据。
4. 网站新增、删除或移动点位后，应重新导出位置数据，继续以 `point_id` 作为跨版本关联键。

