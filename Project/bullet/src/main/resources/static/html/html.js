$(document).ready(function() {   //在HTML文档加载完成后执行
    $("#register").click(function() {
        // 获取控件的值
        var flag = document.getElementById("type")
        var name = document.getElementById("name")
        var pwd = document.getElementById("pwd")
        var post_data = {"flag": flag.value, "name": name.value, "pwd": pwd.value}
        console.log(post_data)
        $.ajax({
            type: "POST",
            url: "http://localhost:8000/register",
            contentType : "application/json;charsetset=UTF-8",  //发送参数时必须添加此句
            headers:{'token':'123', 'name':'', 'pwd':'', 'flag':''},
            timeout: 5000,
            data: JSON.stringify(post_data),
            dataType: 'text',
            success: function (data, status) {
                if (status == 'success') {
                    //解析json数据
                    var info = JSON.parse(data)
                    //提示一个alert窗口
                    alert(info.rspMsg)
                } else {
                    alert('failed');
                }
            }
        })
    })
    $("#login").click(function() {
        // 获取控件的值
        var flag = document.getElementById("type")
        var name = document.getElementById("name")
        var pwd = document.getElementById("pwd")
        var post_data = {"flag": flag.value, "name": name.value, "pwd": pwd.value}
        console.log(post_data)
        $.ajax({
            type: "POST",
            url: "http://localhost:8000/login",
            contentType : "application/json;charsetset=UTF-8",  //发送参数时必须添加此句
            timeout: 5000,
            data: JSON.stringify(post_data),
            dataType: 'text',
            // 登录以后的所有请求都要添加header，包含信息：token, 用于网关权限认证
            beforeSend: function (xhr){
                xhr.setRequestHeader("token", encodeURIComponent("eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxIiwic3ViIjoiYWRtaW4iLCJpc3MiOiJhZG1pbiIsImlhdCI6MTYzNTQwNTUwMSwiZXhwIjoxNjM1NDA5MTAxfQ.lZk4ahWJosntSxzEFBDZt8asJOhI_bOoVLKvPYM2hho"))
            },
            success: function (data, status) {
                if (status == 'success') {
                    console.log(data)
                    //解析json数据
                    var info = JSON.parse(data)
                    if(info.allow == 0)
                        alert(info.rspMsg)
                    else{
                        // window.location.href = "manager.html"
                    }
                } else {
                    alert('failed');
                }
            }
        })
    })
})
