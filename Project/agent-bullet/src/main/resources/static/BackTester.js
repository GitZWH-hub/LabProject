$(document).ready(function() {   //在HTML文档加载完成后执行

    const host = "http://10.177.31.240:8888";


    // 先连接上
    var socket = new SockJS(host + '/agent-bullet');
    let i = 0;
    let cache_base64 = ""
    stompClient = Stomp.over(socket);
    stompClient.connect({}, function (frame) {
        console.log('Connected:' + frame);
        stompClient.subscribe('/toAll/buildfit', function (response) {
            showResponse(response.body);
        });
    });
    function showResponse(message){
        console.log("收到信息")
        let msg = JSON.parse(message).info
        if(msg.length < 2000)
            document.getElementById("ShowInfo").innerHTML += msg + "</br>";
        else{
            cache_base64 += msg
            i = i + 1
            if(i == 2){
                i = 0
                //转码显示
                document.getElementById('show_img').src = cache_base64;
                document.getElementById('mse').innerHTML = 'MSE = ' + JSON.parse(message).mse + '\n'
                cache_base64 = ""
            }
        }
    }
    $("#build").click(function() {
        let flag = document.getElementById("flag")
        let scale = document.getElementById("scale")
        let post_data = {'flag': flag.value, 'scale': scale.value};
        stompClient.send("/Req9999", {}, JSON.stringify(post_data));
    })
})
