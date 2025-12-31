# Implementation Plan - Extend to Support All One Call API 3.0 Data Types

## Issue Understanding

The current implementation only provides 2 endpoints:
- `/weather` - Returns current weather only (excludes hourly/daily)
- `/forecast` - Returns current + hourly (48h) + daily (8d)

However, the One Call API 3.0 provides 5 types of data:
1. **Current weather**
2. **Minutely forecast** (minute-by-minute for 1 hour)
3. **Hourly forecast** (48 hours)
4. **Daily forecast** (8 days)
5. **Alerts** (government weather alerts)

## Proposed Changes

### 1. Add Support for Minutely Forecast
- Add method to `weather_api.py` to format minutely data
- Include minutely data in the `/forecast` endpoint response
- Update client to display minutely forecast when available

### 2. Add Support for Weather Alerts
- Add method to `weather_api.py` to format alerts data
- Add new endpoint `/alerts` to get weather alerts for a location
- Add method to client to display alerts
- Add new CLI command `alerts` to fetch alerts

### 3. Improve Data Formatting
- Ensure all available fields from API response are captured
- Add missing fields like:
  - `wind_gust` (where available)
  - `rain` and `snow` precipitation data
  - `dew_point`
  - `moon_phase` for daily forecast
  - `summary` field for daily forecast

### 4. Update Documentation
- Document all available endpoints
- Add examples for minutely and alerts endpoints
- Update README with comprehensive field descriptions

## Files to Modify

1. **weather_api.py**
   - Add `format_minutely_data()` method
   - Add `format_alerts_data()` method
   - Update `format_forecast_data()` to include minutely when available
   - Add more fields to formatting methods (wind_gust, rain, snow, dew_point, etc.)

2. **mcp_server.py**
   - Add `/alerts` endpoint
   - Update `/forecast` to include minutely data

3. **mcp_client.py**
   - Add `get_alerts()` method
   - Add `display_alerts()` method
   - Update `display_forecast()` to show minutely data when available
   - Add display for additional fields

4. **main.py**
   - Add `alerts` subcommand

5. **README.md**
   - Document new endpoints and capabilities
   - Add examples for alerts
   - Update Quick Start guide

## Summary

This will extend the weather MCP server to fully support all One Call API 3.0 data types, making it a complete weather service that provides:
- Current weather
- Minute-by-minute forecast (1 hour)
- Hourly forecast (48 hours)
- Daily forecast (8 days)
- Weather alerts

Do you want me to proceed with these changes?
