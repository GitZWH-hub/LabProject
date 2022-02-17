package com.example.eurekaproducer.controller;
import com.example.eurekaproducer.request.Req8008;
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

    /*
    * 8001：查询交易所下所有期货代码
    * */
    @PostMapping("/Req8001")
    public String getKData(@RequestBody Req8001 req){
        System.out.println(req);
        return restTemplate.getForEntity("http://sidecar/8001"
                + "/" + req.getExchange(), String.class).getBody();
    }
    /*
    * 8002: 拉取数据
    * */
    @PostMapping("/Req8002")
    public String pullData(@RequestBody Req8002 req) {
        return restTemplate.getForEntity("http://sidecar/8002"
                + "/" + req.getType()
                + "/" + req.getExchange()
                + "/" + req.getStart()
                + "/" + req.getEnd(), String.class).getBody();
    }
    @PostMapping("/Req8008")
    public String BackTestPull(@RequestBody Req8008 req) {
        return restTemplate.getForEntity("http://sidecar/8008"
                + "/" + req.getFut()
                + "/" + req.getStart()
                + "/" + req.getEnd(), String.class).getBody();
    }
}