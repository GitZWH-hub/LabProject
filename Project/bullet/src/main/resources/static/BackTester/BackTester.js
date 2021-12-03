$(document).ready(function() {   //在HTML文档加载完成后执行
    const host = "http://10.177.31.53:8888";
    let socket = null;
    let stompClient = null;
    // 【下载数据】
    $("#DownloadData").click(function(){
        //获取控件的的合约代码
        let fut = document.getElementById("fut")
        let start = document.getElementById("start")
        let end = document.getElementById("end")
        let post_data = {'fut': fut.value, 'start': start.value, 'end': end.value};
        document.getElementById("chart").innerHTML="";
        $.ajax({
            type: "POST",
            url: host + "/Req8008",
            headers: {'Content-Type': 'application/json'},
            timeout: 5000,
            cache: false,
            data: JSON.stringify(post_data),
            dataType : "text",
            success: function (data, status) {
                if (status == 'success') {
                    let json = JSON.parse(JSON.parse(data))
                    // 声明三维数组
                    var dataArr = []
                    //      时间          开盘      收盘    最低    最高       期货代码       五日均值 十日均值
                    // dataArr = [
                    //     ["2021/10/1", [2320.26,2302.6,2287.3,2362.94], "cu2110.SHF", [2450, 2350]],
                    // ];
                    for (let i = 0; i < json.length; i++) {
                        //处理数据放到数组里
                        var arr = new Array(json[i].trade_date,
                                            [json[i].open, json[i].close, json[i].low, json[i].high],
                                            json[i].ts_code,
                                            [json[i].MAS, json[i].MAL])
                        dataArr.push(arr)
                    }
                    console.log(dataArr)
                    document.getElementById("ShowInfo").innerHTML = "下载数据完成</br>";
                    goChart(document.getElementById("chart"), dataArr);
                } else {
                    alert('failed');
                }
            }
        })
        // // 长连接回测
        // // 如果连接存在，则关闭连接
        // if (stompClient != null) {
        //     stompClient.disconnect();
        //     setConnected(true);
        // }
        // // 如果下载数据成功
        // // 长连接bullet
        // socket = new SockJS(host + '/bullet');
        // stompClient = Stomp.over(socket);
        // stompClient.connect({}, function (fra) {
        //     setConnected(false)
        //     stompClient.subscribe('/toAll/DoubleMABackTester', function (response) {
        //         showResponse(response.body);
        //     });
        // });
    })
    $("#BackTest").click(function(){
        // 发送数据
        let fut = document.getElementById("fut")        // 合约代码
        let start = document.getElementById("start")    // 起始日期
        let end = document.getElementById("end")        // 结束日期
        let short = document.getElementById("short")    // 短线周期
        let long = document.getElementById("long")      // 长线周期
        let cash = document.getElementById("cash")      // 回测资金
        let post_data = {   'fut': fut.value,
            'start': start.value,
            'end': end.value,
            'longT': parseInt(long.value),
            'shortT': parseInt(short.value),
            'cash': parseInt(cash.value)};
        console.log("Req8105")
        stompClient.send("/Req8105", {}, JSON.stringify(post_data));
    })
    function setConnected(connected){
        document.getElementById('BackTest').disabled = connected;
    }
    function showResponse(message){
        console.log("收到信息")
        let msg = JSON.parse(message).info
        document.getElementById("ShowInfo").innerHTML += msg + "</br>";
    }
    // 这边想先实现一个隐藏div，鼠标点击显示div。如果要实现放在矩形上显示数据可能要自己根据rect实现，不然就固定放在表格的右边部分，放到框里时显示当日的数据，ts_code/trade_date/high/low/open/close
    function goChart(cBox, dataArr){
        // 申明需要的变量，并且初始化图表（js写在 goChart方法中）
        // 所有变量的一样我已经在注释中注明，大家先不用特别理解，到后面用到的时候就知道了
        // 声明所需变量
        var canvas, ctx;
        // 图表属性
        // 宽度     高度      空白     空间、距离
        var cWidth, cHeight, cMargin, cSpace;
        // x起始
        var originX, originY;
        // 图属性
        var bMargin, tobalBars, bWidth, maxValue, minValue;
        var totalYNomber;
        // var gradient;
        var showArr;
        // 范围选择属性
        var dragBarX, dragBarWidth;
        // 运动相关变量
        var ctr, numctr, speed;
        // 鼠标移动
        var mousePosition = {};
        // 创建canvas并获得canvas上下文
        canvas = document.createElement("canvas");
        if(canvas && canvas.getContext){
            ctx = canvas.getContext("2d");
        }
        canvas.innerHTML = "你的浏览器不支持HTML5 canvas";
        cBox.appendChild(canvas);

        initChart();            // 图表初始化
        drawLineLabelMarkers(); // 绘制图表轴、标签和标记
        drawBarAnimate();       // 绘制柱状图的动画
        // drawLineAnimate();   // 绘制折线图，用于展示5日均价
        // 检测鼠标移动
        var mouseTimer = null;
        addMouseMove();
        function addMouseMove(){
            canvas.addEventListener("mousemove",function(e){
                e = e || window.event;
                if( e.offsetX || e.offsetX==0 ){
                    mousePosition.x = e.offsetX;
                    mousePosition.y = e.offsetY;
                }else if( e.layerX || e.layerX==0 ){
                    mousePosition.x = e.layerX;
                    mousePosition.y = e.layerY;
                }
                clearTimeout(mouseTimer);
                mouseTimer = setTimeout(function(){
                    ctx.clearRect(0,0,canvas.width, canvas.height);
                    drawLineLabelMarkers();
                    drawBarAnimate(true);
                    drawDragBar();
                },10);
            });
        }
        // 图表初始化
        function initChart(){
            // 图表信息
            cMargin = 60;
            cSpace = 80;
            // 将canvas扩大2倍，然后缩小，以适应高清屏幕
            canvas.width = cBox.getAttribute("width")* 2 ;
            canvas.height = cBox.getAttribute("height")* 2;
            canvas.style.height = canvas.height/2 + "px";
            canvas.style.width = canvas.width/2 + "px";
            cHeight = canvas.height - cMargin * 2 - cSpace * 2;
            cWidth = canvas.width - cMargin * 2 - cSpace * 2;
            originX = cMargin + cSpace;
            originY = cMargin + cHeight;

            // 显示多少条记录（矩形）
            showArr = dataArr.slice(0, parseInt(dataArr.length/2) );

            // 柱状图信息
            tobalBars = showArr.length;
            // 矩形宽度
            bWidth = parseInt(cWidth / tobalBars / 3);
            // 矩形间隔
            bMargin = parseInt((cWidth - bWidth * tobalBars) / (tobalBars + 1));
            // 每天的最高价和最低价
            maxValue = 0;
            minValue = 9999999;
            // 循环获取每天的最高价和最低价
            for(var i = 0; i < dataArr.length; i++){
                var barVal =  dataArr[i][1][3] ;
                if( barVal > maxValue ){
                    maxValue = barVal;
                }
                var barVal2 =  dataArr[i][1][2] ;
                if( barVal2 < minValue ){
                    minValue = barVal2;
                }
            }
            // y轴最大值
            maxValue += 20;
            // y轴最小值
            minValue -= 20;
            // y轴最大值和最小值之间分割十份
            totalYNomber = 10;
            // 运动相关
            ctr = 1;
            numctr = 50;
            speed = 2;
            dragBarWidth = 30;
            dragBarX = cWidth / 2 + cSpace + cMargin - dragBarWidth / 2;
        }
        // 接着上一步的代码 绘制坐标轴和标记
        // 绘制图表轴、标签和标记
        function drawLineLabelMarkers(){
            // 字体和大小
            ctx.font = "24px Arial";
            // 坐标轴线的宽度
            ctx.lineWidth = 2;
            // 坐标轴字体颜色
            ctx.fillStyle = "#FFFFFF";
            // 坐标轴线的颜色
            ctx.strokeStyle = "#FFFFFF";
            // 画y轴
            drawLine(originX, originY, originX, cMargin);
            // 画x轴
            drawLine(originX, originY, originX + cWidth, originY);
            // 绘制标记
            drawMarkers();
        }
        // 画线的方法
        function drawLine(x, y, X, Y){
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(X, Y);
            ctx.stroke();
            ctx.closePath();
        }
        // 绘制标记
        function drawMarkers(){
            ctx.strokeStyle = "#E0E0E0";    // 线条颜色浅灰色
            // 绘制 y
            var oneVal = (maxValue - minValue) / totalYNomber;
            ctx.textAlign = "right";
            // 一共画totalNomber：10条
            for(var i = 0; i <= totalYNomber; i++){
                // y轴显示的数字，第一次就是minvalue
                var markerVal =  parseInt(i * oneVal + minValue);
                // y轴显示的数字的x坐标位置
                var xMarker = originX - 10;
                // y轴显示的数字的y坐标位置
                var yMarker = parseInt(originY - cHeight * (markerVal - minValue)/ (maxValue - minValue));
                // 填充y轴文字
                ctx.fillText(markerVal, xMarker, yMarker + 3, cSpace); // 文字
                // 画浅灰色线条
                if(i > 0){
                    drawLine(originX + 2, yMarker, originX + cWidth, yMarker);
                }
            }
            // 绘制 x
            var textNb = 6;
            ctx.textAlign = "center";
            for(var i = 0; i < tobalBars; i++){
                if(tobalBars > textNb && i % parseInt(tobalBars / 6) != 0 ){
                    continue;
                }
                var markerVal = dataArr[i][0];
                var xMarker = parseInt(originX + cWidth * (i / tobalBars) + bMargin + bWidth / 2);
                var yMarker = originY + 40;
                ctx.fillText(markerVal, xMarker, yMarker, cSpace); // 文字
            }
            // 绘制标题 y
            ctx.save();
            ctx.rotate(-Math.PI / 2);
            ctx.fillText("价 格", -canvas.height / 2, cSpace - 40);
            ctx.restore();
            // 绘制标题 x
            ctx.fillText("日 期", originX + cWidth / 2, originY + cSpace - 10);
            num = dataArr.length
            ctx.fillText(dataArr[0][2] + " " + dataArr[0][0] + " - "  + dataArr[num-1][0]+ " K线图", originX + cWidth / 2, originY + cSpace + 100);
        };
        // 接着绘制 中间的K图柱子
        // 这里的代码中包含了后面鼠标移动和调节范围的判断代码，现在还看不到其作用
        // 绘制柱形图动画
        function drawBarAnimate(mouseMove){
            var parsent = ctr / numctr;
            for(var i = 0; i < tobalBars; i++){
                var oneVal = parseInt(maxValue/totalYNomber);
                var data = dataArr[i][1];
                var color = "#0af10a"
                var barVal = data[0];
                var disY = 0;
                // 开盘0 收盘1 最低2 最高3   跌30C7C9  涨D7797F
                if(data[1] > data[0]){  // 涨是红色
                    color = "#ef0202";
                    barVal = data[1];
                    disY = data[1] - data[0];
                }else{
                    disY = data[0] - data[1];
                }
                var showH = disY/ (maxValue - minValue) * cHeight * parsent;
                showH = showH > 2 ? showH: 2;

                var barH = parseInt(cHeight * (barVal-minValue)/(maxValue-minValue));
                var y = originY - barH;
                var x = originX + ((bWidth + bMargin) * i + bMargin)*parsent;

                drawRect( x, y, bWidth, showH, mouseMove, color,true);  //开盘收盘  高度减一避免盖住x轴

                //最高最低的线
                showH = (data[3]-data[2])/(maxValue-minValue)*cHeight*parsent;
                showH = showH>2 ? showH : 2 ;

                y = originY - parseInt(cHeight* (data[3] - minValue)/(maxValue-minValue));
                drawRect(parseInt(x + bWidth/ 2 - 1), y, 2, showH, mouseMove, color);  //最高最低  高度减一避免盖住x轴
            }
            // 绘制折线图
            //（1）五日均线
            ctx.strokeStyle = "rgb(255,251,182)";  //"#49FE79";
            // 连线
            ctx.beginPath();
            for(var i = 0; i < tobalBars; i++){
                var dotVal = dataArr[i][3][0];
                var barH = parseInt(cHeight * (dotVal - minValue)/ (maxValue - minValue) * ctr / numctr);
                var y = originY - barH;
                // var x = originX + bWidth * 3 * i;
                var x = originX + bWidth * (i + 0.5) + bMargin * (i + 1);
                if(i == 0){
                    ctx.moveTo( x, y );
                }else{
                    ctx.lineTo( x, y );
                }
            }
            ctx.stroke();
            // (2) 十日均线
            ctx.strokeStyle = "#ef0606";  //"#49FE79";
            //连线
            ctx.beginPath();
            for(var i = 0; i < tobalBars; i++){
                var dotVal = dataArr[i][3][1];
                var barH = parseInt(cHeight * (dotVal - minValue)/ (maxValue - minValue) * ctr / numctr);
                var y = originY - barH;
                // var x = originX + bWidth * 3 * i;
                var x = originX + bWidth * (i + 0.5) + bMargin * (i + 1);
                if(i == 0){
                    ctx.moveTo( x, y );
                }else{
                    ctx.lineTo( x, y );
                }
            }
            ctx.font="20px";
            // ctx.fillText(" ———— 十日均线", originX + cWidth / 2 + 650, originY + cSpace + 100);
            ctx.stroke();

            if(ctr<numctr){
                ctr++;
                setTimeout(function(){
                    ctx.clearRect(0,0,canvas.width, canvas.height);
                    drawLineLabelMarkers();
                    drawBarAnimate();
                    drawDragBar();
                }, speed*=0.03);
            }
        }
        // 绘制方块
        function drawRect( x, y, X, Y, mouseMove , color, ifBigBar,ifDrag){
            ctx.beginPath();
            if( parseInt(x)%2 !== 0){
                x += 1;
            }
            if( parseInt(y)%2 !== 0){
                y += 1;
            }if( parseInt(X)%2 !== 0){
                X += 1;
            }
            if( parseInt(Y)%2 !== 0){
                Y += 1;
            }
            ctx.rect( parseInt(x), parseInt(y), parseInt(X), parseInt(Y) );
            // 还需要添加一个功能：当鼠标放在这个方框上时，方框变大
            if(ifBigBar && mouseMove && ctx.isPointInPath(mousePosition.x*2, mousePosition.y*2)){ //如果是鼠标移动的到柱状图上，重新绘制图表
                ctx.strokeStyle = color;
                ctx.strokeWidth = 20;
                ctx.stroke();

                // 我要知道鼠标放在的方块是第几个方块，才能找到这个方块的数据，
                // 已知：该方块的起始x值；方块宽度bWidth；坐标轴原点的x位置originX，方块之间间隔bMargin
                // 整个图表的宽度是固定值：cWidth
                let i = 0;
                for(; i < dataArr.length; i++)
                    if(i * bWidth + (i + 1) * bMargin + originX <= x && (i + 1) * (bWidth + bMargin) + originX > x)
                        break

                // 在鼠标旁边绘制一个方块显示当日的信息
                // drawRect(x - 50, y - 100,160, 80)

                const table = document.getElementsByTagName("table")[0];
                // 追加一行
                table.innerHTML = "<tr>\n" +
                    "        <th align='center'>" + "交易日期" + "</th>\n" +
                    "        <th align='center'>" + "合约代码" + "</th>\n" +
                    "        <th align='center'>" + "开盘价" + "</th>\n" +
                    "        <th align='center'>" + "收盘价" + "</th>\n" +
                    "        <th align='center'>" + "最高价" + "</th>\n" +
                    "        <th align='center'>" + "最低价" + "</th>\n" +
                    "        <th align='center'>" + "五日均价" + "</th>\n" +
                    "        <th align='center'>" + "十日均价" + "</th>\n" +
                    "    </tr>";
                table.innerHTML += "<tr>\n" +
                    "        <td align='center'>" + dataArr[i][0] + "</td>\n" +
                    "        <td align='center'>" + dataArr[i][2] + "</td>\n" +
                    "        <td align='center' class='td3'>" + dataArr[i][1][0]  + "</td>\n" +     // 开盘价
                    "        <td align='center' class='td3'>" + dataArr[i][1][1]  + "</td>\n" +     // 收盘价
                    "        <td align='center' class='td3'>" + dataArr[i][1][3]  + "</td>\n" +     // 最低价
                    "        <td align='center' class='td3'>" + dataArr[i][1][2]  + "</td>\n" +     // 最高价
                    "        <td align='center'>" + dataArr[i][3][0]  + "</td>\n" +     // 五日均价
                    "        <td align='center'>" + dataArr[i][3][1]  + "</td>\n" +     // 十日均价
                    "    </tr>";
            }
            // 如果移动到拖动选择范围按钮
            canvas.style.cursor = "default";
            if(ifDrag && ctx.isPointInPath(mousePosition.x*2, mousePosition.y*2)){ //如果是鼠标移动的到柱状图上，重新绘制图表
                canvas.style.cursor = "all-scroll";
            }
            ctx.fillStyle = color;
            ctx.fill();
            ctx.closePath();
        }
        // 绘制圆点
        function drawArc( x, y, X, Y ){
            ctx.beginPath();
            ctx.arc( x, y, 3, 0, Math.PI*2 );
            ctx.fill();
            ctx.closePath();
        }
        // 接着绘制选择范围的矩形
        // 绘制拖动轴
        drawDragBar();
        function drawDragBar(){
            drawRect(originX, originY+cSpace+5, cWidth, cMargin-20, false, "#0a0711");
            drawRect(originX, originY+cSpace+5, dragBarX-originX, cMargin-20, false, "#898c92");
            drawRect(dragBarX, originY+cSpace+5, dragBarWidth, cMargin-20, false, "#ffffff",false,true);
        }
        // 监听拖拽
        canvas.onmousedown = function(e){
            if(canvas.style.cursor != "all-scroll"){
                return false;
            }
            document.onmousemove = function(e){
                e = e || window.event;
                if( e.offsetX || e.offsetX==0 ){
                    dragBarX = e.offsetX*2-dragBarWidth/2;
                }else if( e.layerX || e.layerX==0 ){
                    dragBarX = e.layerX*2-dragBarWidth/2;
                }
                if(dragBarX<=originX){
                    dragBarX=originX
                }
                if(dragBarX>originX+cWidth-dragBarWidth){
                    dragBarX=originX+cWidth-dragBarWidth
                }
                var nb = Math.ceil( dataArr.length*( (dragBarX-cMargin-cSpace)/cWidth ) );
                showArr = dataArr.slice( 0, nb || 1 );

                // 柱状图信息
                tobalBars = showArr.length;
                bWidth = parseInt( cWidth/ tobalBars / 3);
                bMargin = parseInt( (cWidth - bWidth * tobalBars)/(tobalBars + 1) );
            }
            document.onmouseup = function(){
                document.onmousemove = null;
                document.onmouseup = null;
            }
        }
    }
})
