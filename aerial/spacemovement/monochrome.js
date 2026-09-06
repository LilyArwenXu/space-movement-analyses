(function () {
  function install() {
    if (!window.echarts || window.echarts.__monoInstalled) return;
    window.echarts.__monoInstalled = true;
    const originalInit = window.echarts.init;
    const palette = ['#f5f5f2','#d8d8d5','#b8b8b5','#969693','#747472','#525250','#303030'];
    window.echarts.init = function () {
      const chart = originalInit.apply(this, arguments);
      const originalSetOption = chart.setOption;
      chart.setOption = function (option) {
        option.textStyle = {fontFamily:'Times New Roman, SimSun, Songti SC, serif',color:'#ddd'};
        option.backgroundColor = '#101010';
        option.color = palette;
        if (option.title) {
          const titles = Array.isArray(option.title) ? option.title : [option.title];
          titles.forEach(t => { t.textStyle = Object.assign({}, t.textStyle, {color:'#f5f5f2'}); t.subtextStyle = Object.assign({}, t.subtextStyle, {color:'#a8a8a5'}); });
        }
        const axes = [].concat(option.xAxis || [], option.yAxis || [], option.singleAxis || []);
        axes.forEach(a => {
          a.axisLabel = Object.assign({}, a.axisLabel, {color:'#bdbdb9'});
          a.axisLine = {lineStyle:Object.assign({}, a.axisLine && a.axisLine.lineStyle, {color:'#666'})};
          if (a.splitLine) a.splitLine.lineStyle = Object.assign({}, a.splitLine.lineStyle, {color:'#333'});
          if (a.nameTextStyle) a.nameTextStyle.color = '#bdbdb9';
        });
        const legends = Array.isArray(option.legend) ? option.legend : [option.legend];
        legends.filter(Boolean).forEach(l => { l.textStyle = Object.assign({}, l.textStyle, {color:'#ddd'}); });
        if (option.series) option.series.forEach((s,i) => {
          s.itemStyle = Object.assign({}, s.itemStyle, {color:palette[i % palette.length], borderColor:'#f5f5f2'});
          if (s.lineStyle) s.lineStyle.color = palette[i % palette.length];
          if (s.label) s.label.color = i < 2 ? '#090909' : '#f5f5f2';
        });
        return originalSetOption.apply(chart, arguments);
      };
      return chart;
    };
  }
  install();
})();
