package com.hiroki.weatherdashboard.controller;

import com.hiroki.weatherdashboard.dto.ForecastResponse;
import com.hiroki.weatherdashboard.service.OpenMeteoForecastService;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Validated
public class ForecastController {

    private final OpenMeteoForecastService forecastService;

    public ForecastController(OpenMeteoForecastService forecastService) {
        this.forecastService = forecastService;
    }

    @GetMapping("/api/forecast")
    public ForecastResponse forecast(
            @RequestParam @DecimalMin("-90.0") @DecimalMax("90.0") double lat,
            @RequestParam @DecimalMin("-180.0") @DecimalMax("180.0") double lon,
            @RequestParam(defaultValue = "Asia/Tokyo") @NotBlank String timezone
    ) {
        return forecastService.getDailyForecast(lat, lon, timezone);
    }
}
