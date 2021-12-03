package com.naah.gateway.filter;

import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
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
        ServerHttpResponse response = exchange.getResponse();
        System.out.println(String.valueOf(exchange.getRequest().getMethod()));
        if (OPTIONS.equalsIgnoreCase(String.valueOf(exchange.getRequest().getMethod()))) {
            System.out.println("OPTIONS鉴定...");
            response.setStatusCode(HttpStatus.OK);
            return response.setComplete();
        }
        // 继续执行filter链
        return chain.filter(exchange);
    }

    // 顺序，数值越小，优先级越高
    @Override
    public int getOrder() {
        return 0;
    }
}


