package com.hiroki.weatherdashboard.dto;

import java.util.List;

public record ForecastResponse(
        Double latitude,
        Double longitude,
        String timezone,
        String fetchedAt,
        List<ForecastDay> days
) {}
