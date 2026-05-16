package com.hiroki.weatherdashboard.dto;

public record ForecastDay(
        String date,
        Double tempMax,
        Double tempMin,
        Integer precipProbabilityMax,
        Double windSpeedMax,
        Integer weatherCode
) {}
