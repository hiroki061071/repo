package com.hiroki.weatherdashboard.dto;

public record GeocodeResult(
        String name,
        String country,
        Double latitude,
        Double longitude
) {}
