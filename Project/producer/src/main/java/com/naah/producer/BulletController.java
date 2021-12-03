package com.naah.producer;

import com.naah.producer.request.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import javax.annotation.Resource;

@CrossOrigin
@RestController
public class BulletController {
    private static final Logger logger = LoggerFactory.getLogger(BulletController.class);

    @Autowired
    private RestTemplate restTemplate;


    @Resource
    private SimpMessagingTemplate template;

    // 查询期货合约信息
    @GetMapping("/future")
    public String getFuture() {
        return restTemplate.getForEntity("http://sidecar/future", String.class).getBody();
    }
    /*
        8001：查询：请求获取K线图数据
    */
    @PostMapping("/Req8001")
    public String getKData(@RequestBody Req8001 req){
        System.out.println(req);
        return restTemplate.getForEntity("http://sidecar/8001"
                + "/" + req.getFut()
                + "/" + req.getFutEnd()
                + "/" + req.getStart()
                + "/" + req.getEnd(), String.class).getBody();
    }
    /*
        8002
    */
    @PostMapping("/Req8002")
    public String pullData(@RequestBody Req8002 req) {
        return restTemplate.getForEntity("http://sidecar/8002"
                + "/" + req.getType()
                + "/" + req.getFut()
                + "/" + req.getStart()
                + "/" + req.getEnd(), String.class).getBody();
    }

    /*
    8008:请求拉取数据from TuShare
    */
    @PostMapping("/Req8008")
    public String getData(@RequestBody Req8008 req) {
        System.out.println(req);
        return restTemplate.getForEntity("http://sidecar/8008"
                + "/" + req.getFut()
                + "/" + req.getStart()
                + "/" + req.getEnd(), String.class).getBody();
    }
}