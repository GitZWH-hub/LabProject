package com.naah.gateway.filter;
import org.springframework.stereotype.Component;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
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

import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

/**
 * 自定义全局过滤器，需要实现GlobalFilter和Ordered接口
 */
@Component
public class AuthGlobalFilter implements GlobalFilter, Ordered {
    private static final String OPTIONS = "OPTIONS";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        if (OPTIONS.equalsIgnoreCase(String.valueOf(exchange.getRequest().getMethod()))) {
            System.out.println("OPTIONS鉴定...");
            exchange.getResponse().setStatusCode(HttpStatus.OK);
            return exchange.getResponse().setComplete();
        }
        System.out.println(String.valueOf(exchange.getRequest().getMethod()));
        // 继续执行filter链
        return chain.filter(exchange);
    }

    // 顺序，数值越小，优先级越高
    @Override
    public int getOrder() {
        return 0;
    }
}


