package com.hiroki.weatherdashboard.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record OpenMeteoGeocodingApiResponse(
        List<Result> results
) {
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Result(
            String name,
            String country,
            Double latitude,
            Double longitude
    ) {}
}
