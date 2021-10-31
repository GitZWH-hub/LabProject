
package com.example.EurekaSidecarApplication;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.sidecar.EnableSidecar;


@EnableSidecar
@SpringBootApplication
public class EurekaSidecarApplication {
    public static void main(String[] args) {

        SpringApplication.run(EurekaSidecarApplication.class, args);
    }
}
