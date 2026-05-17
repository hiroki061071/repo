package com.hiroki.weatherdashboard.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hiroki.weatherdashboard.dto.GeocodeResult;
import com.hiroki.weatherdashboard.dto.OpenMeteoGeocodingApiResponse;
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
public class OpenMeteoGeocodingService {

    private static final String BASE_URL = "https://geocoding-api.open-meteo.com/v1/search";

    private final ObjectMapper objectMapper;
    private final HttpClient httpClient;

    public OpenMeteoGeocodingService() {
        this.objectMapper = new ObjectMapper();
        this.httpClient = HttpClient.newHttpClient();
    }

    public List<GeocodeResult> search(String name) {
        String encoded = URLEncoder.encode(name, StandardCharsets.UTF_8);
        String url = BASE_URL + "?name=" + encoded + "&count=5&language=ja&format=json";

        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .header("Accept", "application/json")
                .GET()
                .build();

        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                throw new IllegalStateException("Geocoding API error: " + response.statusCode() + " body=" + response.body());
            }

            OpenMeteoGeocodingApiResponse apiResponse =
                    objectMapper.readValue(response.body(), OpenMeteoGeocodingApiResponse.class);

            List<GeocodeResult> list = new ArrayList<>();
            if (apiResponse.results() != null) {
                for (OpenMeteoGeocodingApiResponse.Result r : apiResponse.results()) {
                    list.add(new GeocodeResult(
                            r.name(),
                            r.country(),
                            r.latitude(),
                            r.longitude()
                    ));
                }
            }

            return list;

        } catch (IOException e) {
            throw new IllegalStateException("Failed to parse geocoding response", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Interrupted while geocoding", e);
        }
    }
}
