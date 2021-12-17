package com.naah.bullet;

import com.naah.bullet.request.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import com.alibaba.fastjson.JSON;
import javax.annotation.Resource;

//@Controller
@CrossOrigin
@RestController
public class BulletController {
    private static final Logger logger = LoggerFactory.getLogger(BulletController.class);

    @Autowired
    private RestTemplate restTemplate;

    @MessageMapping("/Req8101")
    //SendTo 发送至 Broker 下的指定订阅路径
    @SendTo("/toAll/bulletScreen")
    public String sendQuotes(Req8101 req) {
        System.out.println("Req8181 订阅行情");
       //这里调用行情ctp api获取行情
        return restTemplate.getForEntity("http://sidecar/8101/" + req.getFut() + "/" + req.getFutEnd(), String.class).getBody();
    }

    @Resource
    private SimpMessagingTemplate template;

    //这里是API收到行情主动调用的函数，与前台链接测试成功
    @PostMapping("/sendQuotes")
    public String sendMessage(@RequestBody Req8102 req) throws Exception{
        System.out.println("bullet 收到行情");
        String json=JSON.toJSONString(req);//关键
        System.out.println(json);
        template.convertAndSend("/toAll/bulletScreen", json);
        return "yes";
    }

    @MessageMapping("/Req8102")
    public String stopQuotes() {
        System.out.println("8102取消订阅");
        //这里调用行情ctp api获取行情
        return restTemplate.getForEntity("http://sidecar/8102", String.class).getBody();
    }

    @MessageMapping("/Req8103")
    public String exchangeEv(@RequestBody Req8103 req) {
        System.out.println("8103更改环境");
        //这里调用行情ctp api获取行情
        return restTemplate.getForEntity("http://sidecar/8103" + "/" + req.getFlag(), String.class).getBody();
    }

    //SendTo 发送至 Broker 下的指定订阅路径
    @MessageMapping("/Req8105")
    @SendTo("/toAll/DoubleMABackTester")
    public void doubleMABackTest(@RequestBody Req8105 req) {
        System.out.println("8105双均线回测");
        System.out.println(req);
        //这里调用行情ctp api获取行情
        restTemplate.getForEntity("http://sidecar/8105"
                + "/" + req.getFut()+ "/" + req.getStart()+ "/" + req.getEnd()
                + "/" + req.getShortT()+ "/" + req.getLongT()+ "/" + req.getCash(), String.class).getBody();
    }
    //这里是API收到行情主动调用的函数，与前台链接测试成功
    @PostMapping("/sendDoubleMABackTestInfo")
    public String sendMessage(@RequestBody Req8100 req) throws Exception{
        System.out.println("bullet 收到信息");
        String json=JSON.toJSONString(req);//关键
        System.out.println(json);
        template.convertAndSend("/toAll/DoubleMABackTester", json);
        return "yes";
    }

    //数据挖掘课程demo
    //SendTo 发送至 Broker 下的指定订阅路径
    @MessageMapping("/Req9999")
    @SendTo("/toAll/buildfit")
    public void build(@RequestBody req9998 req) {
        System.out.println("9999");
        System.out.println(req);
        //这里调用行情ctp api获取行情
        restTemplate.getForEntity("http://sidecar/9999"
                + "/" + req.getFlag(), String.class).getBody();
    }
    @PostMapping("/buildandfit")
    public String buildandfit(@RequestBody req9999 req) throws Exception{
        System.out.println("bullet 收到信息");
        String json=JSON.toJSONString(req);//关键
        System.out.println(json);
        template.convertAndSend("/toAll/buildfit", json);
        return "yes";
    }
}