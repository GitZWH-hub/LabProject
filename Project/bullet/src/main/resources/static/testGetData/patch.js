$(document).ready(function() {   //在HTML文档加载完成后执行
    $("#getFuture").click(function() {
        $.ajax({
            type: "GET",
            // url: "http://localhost:8765/future",
            url: "http://10.177.31.53:8888/future",
            timeout: 5000,
            dataType: 'text',  // 请求方式为jsonp
            success: function (data, status) {
                if (status == 'success') {
                    console.log(data)
                    let json = JSON.parse(JSON.parse(data))
                    // 获取table
                    const future = document.getElementsByTagName("table")[0];
                    // 追加一行

                    future.innerHTML = "<tr>\n" +
                        "        <th align='center'>" + "INDEX" + "</th>\n" +
                        "        <th align='center'>" + "合约代码" + "</th>\n" +
                        "        <th align='center'>" + "交易标识" + "</th>\n" +
                        "        <th align='center'>" + "交易市场" + "</th>\n" +
                        "        <th align='center'>" + "中文简称" + "</th>\n" +
                        "        <th align='center'>" + "合约产品代码" + "</th>\n" +
                        "        <th align='center'>" + "交易单位每手" + "</th>\n" +
                        "        <th align='center'>" + "报价" + "</th>\n" +
                        "    </tr>";
                    for (let i = 0; i < json.length; i++) {
                        // 追加一行
                        future.innerHTML += "<tr>\n" +
                            "        <td>" + (i + 1) + "</td>\n" +
                            "        <td>" + json[i].ts_code + "</td>\n" +
                            "        <td>" + json[i].symbol + "</td>\n" +
                            "        <td>" + json[i].exchange + "</td>\n" +
                            "        <td>" + json[i].name + "</td>\n" +
                            "        <td>" + json[i].fut_code + "</td>\n" +
                            "        <td>" + json[i].per_unit + "</td>\n" +
                            "        <td>" + json[i].quote_unit + "</td>\n" +
                            "    </tr>";
                    }
                } else {
                    alert('failed');
                }
            }
        })
    })
    $("#pullData").click(function() {
        //拉取数据暂时先必选，暂时不晓得空的时候如何传值
        const type = document.getElementById("type");
        const fut = document.getElementById("fut")
        const start = document.getElementById("start");
        const end = document.getElementById("end");
        let post_data = {'type': type.value, 'fut': fut.value, 'start': start.value, 'end': end.value,};
        $.ajax({
            type: "post",
            url: "http://10.177.31.53:8888/Req8002",
            data: JSON.stringify(post_data),
            contentType : "application/json;charsetset=UTF-8",  //发送参数时必须添加此句
            timeout: 10000,
            dataType: 'text',
            success: function (data, status) {
                if (status == 'success') {
                    json = JSON.parse(data)
                    alert('Pull Succeed! Congratulations!')
                } else {
                    alert('Failed');
                }
            }
        })
    })
})
