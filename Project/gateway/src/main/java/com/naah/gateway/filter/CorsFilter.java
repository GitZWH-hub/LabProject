package com.naah.gateway.filter;

import org.springframework.stereotype.Component;

import javax.servlet.*;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

//import org.springframework.stereotype.Component;
//import org.springframework.cloud.gateway.filter.GatewayFilterChain;
//import org.springframework.cloud.gateway.filter.GlobalFilter;
//import org.springframework.core.Ordered;
//import org.springframework.http.HttpStatus;
//import org.springframework.web.server.ServerWebExchange;
//import reactor.core.publisher.Mono;
//
///**
// * 自定义全局过滤器，需要实现GlobalFilter和Ordered接口
// */
//@Component
//public class AuthGlobalFilter implements GlobalFilter, Ordered {
//    private static final String OPTIONS = "OPTIONS";
//
//    @Override
//    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
//        if (OPTIONS.equalsIgnoreCase(String.valueOf(exchange.getRequest().getMethod()))) {
//            System.out.println("OPTIONS鉴定...");
//            exchange.getResponse().setStatusCode(HttpStatus.OK);
//            return exchange.getResponse().setComplete();
//        }
//        System.out.println(String.valueOf(exchange.getRequest().getMethod()));
//        // 继续执行filter链
//        return chain.filter(exchange);
//    }
//
//    // 顺序，数值越小，优先级越高
//    @Override
//    public int getOrder() {
//        return 0;
//    }
//}
@Component
public class CorsFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) throws IOException, ServletException {
        HttpServletResponse response = (HttpServletResponse) res;
        System.out.println("come here");
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

