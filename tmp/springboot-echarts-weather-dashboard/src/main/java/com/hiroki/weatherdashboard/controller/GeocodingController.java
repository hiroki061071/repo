package com.hiroki.weatherdashboard.controller;

import com.hiroki.weatherdashboard.dto.GeocodeResult;
import com.hiroki.weatherdashboard.service.OpenMeteoGeocodingService;
import jakarta.validation.constraints.NotBlank;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@Validated
public class GeocodingController {

    private final OpenMeteoGeocodingService geocodingService;

    public GeocodingController(OpenMeteoGeocodingService geocodingService) {
        this.geocodingService = geocodingService;
    }

    @GetMapping("/api/geocode")
    public List<GeocodeResult> geocode(@RequestParam @NotBlank String name) {
        return geocodingService.search(name);
    }
}
