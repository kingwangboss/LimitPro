// 时间格式化函数
function formatDateTime(utcTimeStr) {
    if (!utcTimeStr) return '-';
    const utcDate = new Date(utcTimeStr);
    const localDate = new Date(utcDate.getTime() - 8 * 60 * 60 * 1000);
    
    const year = localDate.getFullYear();
    const month = String(localDate.getMonth() + 1).padStart(2, '0');
    const day = String(localDate.getDate()).padStart(2, '0');
    const hours = String(localDate.getHours()).padStart(2, '0');
    const minutes = String(localDate.getMinutes()).padStart(2, '0');
    const seconds = String(localDate.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// 创建股票表格行
function createStockRow(stock) {
    return `
        <tr>
            <td><a href="http://quote.eastmoney.com/${stock.代码.startsWith('6') ? 'sh' : 'sz'}${stock.代码}.html" target="_blank" class="stock-code">${stock.代码}</a></td>
            <td>${stock.名称}</td>
            <td class="number">${stock.收盘价.toFixed(2)}</td>
            <td class="number">${stock.涨跌幅.toFixed(2)}%</td>
            <td class="number">${stock.换手率.toFixed(2)}%</td>
            <td class="number">${stock.MA144.toFixed(2)}</td>
            <td class="number">${stock.MA233.toFixed(2)}</td>
            <td class="number">${stock['30日高点'].toFixed(2)}</td>
            <td class="number">${stock['近三日涨幅']}</td>
            <td class="${stock.当前趋势 === '上升' ? 'up' : 'down'}">${stock.当前趋势}</td>
            <td class="number ${stock.出现可能性 >= 80 ? 'high-prob' : ''}">${stock.出现可能性}%</td>
            <td>${stock.最新拐点日期}<br>${stock.最新拐点类型}</td>
        </tr>
    `;
}

// 初始化DataTable
function initDataTable(tableId) {
    return $(tableId).DataTable({
        responsive: true,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.10.21/i18n/Chinese.json'
        },
        order: [[10, "desc"]],
        pageLength: 25,
        dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
             "<'row'<'col-sm-12'tr>>" +
             "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
    });
} 