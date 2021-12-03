package com.naah.gateway.filter;
import org.springframework.stereotype.Component;

import javax.servlet.*;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

//@Component
//@WebFilter(filterName = "CorsFilter", urlPatterns = "/*")
//public class CorsGatewayFilterFactory implements Filter {
//    private static final String OPTIONS = "OPTIONS";
//
//    @Override
//    public void init(FilterConfig filterConfig) throws ServletException {
//
//    }
//
//    @Override
//    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
//        HttpServletRequest request = (HttpServletRequest) servletRequest;
//        HttpServletResponse response = (HttpServletResponse) servletResponse;
//        response.addHeader("Access-Control-Allow-Origin", "*");
//        response.setHeader("Access-Control-Allow-Methods", "POST,GET,PUT,DELETE,OPTIONS");
//        response.addHeader("Access-Control-Allow-Headers", "*");
//        System.out.println("测试是否到达filter");
//        System.out.println(request.getMethod());
//        //response.addHeader("Access-Control-Max-Age", "3628800"); //可选
//
//        if(OPTIONS.equalsIgnoreCase(request.getMethod()))
//
//            return;  // 或者直接输入204、HttpStatus.SC_OK、200，等这些都可以   import org.apache.http.HttpStatus;
//        filterChain.doFilter(servletRequest, response);
//    }
//
//    @Override
//    public void destroy() {
//
//    }
//
////
////    @Override
////    public GatewayFilter apply(Object config) {
////        return (exchange, chain) -> {
////            //1. 获取请求
////            HttpServletRequest request = (HttpServletRequest) exchange.getRequest();
////            //2. 则获取响应
////            HttpServletResponse response = (HttpServletResponse) exchange.getResponse();
////            response.addHeader("Access-Control-Allow-Origin", "*");
////            response.setHeader("Access-Control-Allow-Methods", "POST,GET,PUT,DELETE,OPTIONS");
////            response.addHeader("Access-Control-Allow-Headers", "*");
////            System.out.println("测试是否到达filter");
////            System.out.println(request.getMethod());
////            return chain.filter(exchange);
////        };
////    }
//}
@Component
public class CorsFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) throws IOException, ServletException {
        HttpServletResponse response = (HttpServletResponse) res;
        response.setHeader("Access-Control-Allow-Origin", "*");
        response.setHeader("Access-Control-Allow-Methods", "POST, GET, PUT, OPTIONS, DELETE, PATCH");
        response.setHeader("Access-Control-Max-Age", "3600");
        response.setHeader("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
        response.setHeader("Access-Control-Expose-Headers", "Location");
        chain.doFilter(req, res);
    }

    @Override
    public void init(FilterConfig filterConfig) {}

    @Override
    public void destroy() {}

}
