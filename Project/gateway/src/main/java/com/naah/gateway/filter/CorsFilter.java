package com.naah.gateway.filter;
import org.springframework.stereotype.Component;

import javax.servlet.*;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Component
@WebFilter(filterName = "CorsFilter", urlPatterns = "/*")
public class CorsFilter implements Filter {
    private static final String OPTIONS = "OPTIONS";

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {

    }

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;
        response.addHeader("Access-Control-Allow-Origin", "*");
        response.setHeader("Access-Control-Allow-Methods", "POST,GET,PUT,DELETE,OPTIONS");
        response.addHeader("Access-Control-Allow-Headers", "*");
        System.out.println("测试是否到达filter");
        System.out.println(request.getMethod());
        //response.addHeader("Access-Control-Max-Age", "3628800"); //可选

        if(OPTIONS.equalsIgnoreCase(request.getMethod()))
            filterChain.doFilter(servletRequest, response);
            return;  // 或者直接输入204、HttpStatus.SC_OK、200，等这些都可以   import org.apache.http.HttpStatus;
    }

    @Override
    public void destroy() {

    }

}

