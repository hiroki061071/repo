package com.hiroki.weatherdashboard.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hiroki.weatherdashboard.dto.ForecastDay;
import com.hiroki.weatherdashboard.dto.ForecastResponse;
import com.hiroki.weatherdashboard.dto.OpenMeteoApiResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

@Service
public class OpenMeteoForecastService {

    private final String baseUrl;
    private final ObjectMapper objectMapper;
    private final HttpClient httpClient;

    public OpenMeteoForecastService(@Value("${app.weather.base-url}") String baseUrl) {
        this.baseUrl = baseUrl;
        this.objectMapper = new ObjectMapper();
        this.httpClient = HttpClient.newHttpClient();
    }

    public ForecastResponse getDailyForecast(double latitude, double longitude, String timezone) {
        String url = buildUrl(latitude, longitude, timezone);

        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .header("Accept", "application/json")
                .GET()
                .build();

        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                throw new IllegalStateException(
                        "Open-Meteo API error: " + response.statusCode() + " body=" + response.body()
                );
            }

            OpenMeteoApiResponse apiResponse =
                    objectMapper.readValue(response.body(), OpenMeteoApiResponse.class);

            return mapToForecastResponse(apiResponse);

        } catch (IOException e) {
            throw new IllegalStateException("Failed to parse weather response", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Interrupted while fetching weather forecast", e);
        }
    }

    private String buildUrl(double latitude, double longitude, String timezone) {
        String encodedTimezone = URLEncoder.encode(timezone, StandardCharsets.UTF_8);
        return baseUrl
                + "?latitude=" + latitude
                + "&longitude=" + longitude
                + "&timezone=" + encodedTimezone
                + "&forecast_days=7"
                + "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max";
    }

    private ForecastResponse mapToForecastResponse(OpenMeteoApiResponse apiResponse) {
        List<ForecastDay> days = new ArrayList<>();

        if (apiResponse.daily() != null && apiResponse.daily().time() != null) {
            int size = apiResponse.daily().time().size();

            for (int i = 0; i < size; i++) {
                days.add(new ForecastDay(
                        get(apiResponse.daily().time(), i),
                        get(apiResponse.daily().temperature2mMax(), i),
                        get(apiResponse.daily().temperature2mMin(), i),
                        get(apiResponse.daily().precipitationProbabilityMax(), i),
                        get(apiResponse.daily().windSpeed10mMax(), i),
                        get(apiResponse.daily().weatherCode(), i)
                ));
            }
        }

        return new ForecastResponse(
                apiResponse.latitude(),
                apiResponse.longitude(),
                apiResponse.timezone(),
                days
        );
    }

    private <T> T get(List<T> list, int index) {
        if (list == null || index >= list.size()) {
            return null;
        }
        return list.get(index);
    }
}