package com.example.eurekaproducer.controller;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import com.example.eurekaproducer.request.Req8001;
import com.example.eurekaproducer.request.Req8002;

@CrossOrigin
@RestController
public class UserController {

    @Autowired
    private RestTemplate restTemplate;

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
        return restTemplate.getForEntity("http://sidecar/8001"
                + "/" + req.getFut()
                + "/" + req.getFutEnd()
                + "/" + req.getStart()
                + "/" + req.getEnd(), String.class).getBody();
    }
    /*
        8002:请求拉取数据from TuShare
    */
    @PostMapping("/Req8002")
    public String pullData(@RequestBody Req8002 req) {
        return restTemplate.getForEntity("http://sidecar/8002"
                + "/" + req.getType()
                + "/" + req.getFut()
                + "/" + req.getStart()
                + "/" + req.getEnd(), String.class).getBody();
    }


}
















//    // 获取K线图
//    @RequestMapping("/getKImage")
//    public String getKImage() {
//        return restTemplate.getForEntity("http://sidecar/KImage", String.class).getBody();
//    }
//    // 获取多子图
//    @RequestMapping("/getMultiImage")
//    public String getMultiImage() { return restTemplate.getForEntity("http://sidecar/MultiImage", String.class).getBody(); }
