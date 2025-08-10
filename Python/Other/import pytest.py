import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import io
import sys
from Python.Other.GlobalWeather import GlobalWeatherRepository

class TestGlobalWeatherRepository:
    
    @pytest.fixture
    def sample_weather_data(self):
        """Create sample weather data for testing"""
        data = {
            'country': ['Afghanistan', 'Albania', 'Algeria', 'Bangladesh', 'Brazil'],
            'city': ['Kabul', 'Tirana', 'Algiers', 'Dhaka', 'Brasilia'],
            'latitude': [34.52, 41.33, 36.76, 23.72, -15.78],
            'longitude': [69.18, 19.82, 3.05, 90.41, -47.93],
            'timezone': ['Asia/Kabul', 'Europe/Tirane', 'Africa/Algiers', 'Asia/Dhaka', 'America/Sao_Paulo'],
            'last_updated': ['2024-05-16 13:15', '2024-05-16 10:45', '2024-05-16 09:45', '2024-05-16 14:45', '2024-05-16 04:45'],
            'temperature_celsius': [26.6, 19.0, 23.0, 38.4, 23.1],
            'temperature_fahrenheit': [79.8, 66.2, 73.4, 101.2, 73.6],
            'condition_text': ['Partly Cloudy', 'Partly cloudy', 'Sunny', 'Partly Cloudy', 'Fog'],
            'wind_mph': [8.3, 6.9, 9.4, 4.3, 2.5],
            'wind_kph': [13.3, 11.2, 15.1, 6.8, 4.0],
            'wind_degree': [338, 320, 280, 222, 62],
            'wind_direction': ['NNW', 'NW', 'W', 'SW', 'ENE'],
            'pressure_mb': [1012.0, 1012.0, 1011.0, 1006.0, 1009.0],
            'pressure_in': [29.89, 29.88, 29.85, 29.71, 29.81],
            'precip_mm': [0.0, 0.1, 0.0, 0.0, 0.04],
            'precip_in': [0.0, 0.0, 0.0, 0.0, 0.0],
            'humidity': [24, 94, 29, 31, 98],
            'cloud': [30, 75, 0, 30, 100],
            'feels_like_celsius': [25.3, 19.0, 24.6, 41.3, 25.7],
            'feels_like_fahrenheit': [77.5, 66.2, 76.4, 106.4, 78.2],
            'visibility_km': [10.0, 10.0, 10.0, 10.0, 0.0],
            'visibility_miles': [6.0, 6.0, 6.0, 6.0, 0.0],
            'uv_index': [7.0, 5.0, 5.0, 9.0, 1.0],
            'gust_mph': [9.5, 11.4, 13.9, 4.9, 5.0],
            'gust_kph': [15.3, 18.4, 22.3, 7.9, 8.0],
            'moon_phase': ['Waxing Gibbous', 'Waxing Gibbous', 'Waxing Gibbous', 'Waxing Gibbous', 'Waxing Gibbous'],
            'moon_illumination': [55, 55, 55, 55, 55]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def temp_csv_file(self, sample_weather_data, tmp_path):
        """Create a temporary CSV file for testing"""
        csv_file = tmp_path / "test_weather.csv"
        sample_weather_data.to_csv(csv_file, index=False)
        return str(csv_file)
    
    @pytest.fixture
    def weather_repo(self, temp_csv_file):
        """Create a GlobalWeatherRepository instance for testing"""
        return GlobalWeatherRepository(temp_csv_file)

    def test_init_success(self, temp_csv_file, sample_weather_data):
        """Test successful initialization"""
        repo = GlobalWeatherRepository(temp_csv_file)
        assert len(repo.df) == len(sample_weather_data)
        assert len(repo.countries) == 5
        assert 'Afghanistan' in repo.countries
        assert 'Brazil' in repo.countries

    def test_init_file_not_found(self):
        """Test initialization with non-existent file"""
        with pytest.raises(FileNotFoundError):
            GlobalWeatherRepository("non_existent_file.csv")

    def test_init_missing_columns(self, tmp_path):
        """Test initialization with missing required columns"""
        # Create CSV with missing columns
        incomplete_data = pd.DataFrame({'country': ['Test'], 'incomplete': ['data']})
        csv_file = tmp_path / "incomplete.csv"
        incomplete_data.to_csv(csv_file, index=False)
        
        # Should still work since required_columns is empty in the current implementation
        repo = GlobalWeatherRepository(str(csv_file))
        assert len(repo.df) == 1

    def test_display_menu(self, weather_repo, capsys):
        """Test menu display"""
        weather_repo.display_menu()
        captured = capsys.readouterr()
        assert "Welcome to the Global Weather Repository!" in captured.out
        assert "0. Exit" in captured.out
        assert "14. Manage favorites" in captured.out

    def test_view_all(self, weather_repo, capsys):
        """Test view all countries functionality"""
        weather_repo.view_all()
        captured = capsys.readouterr()
        assert "List of All Countries" in captured.out
        assert "Afghanistan" in captured.out
        assert "Brazil" in captured.out

    @patch('builtins.input', return_value='a')
    def test_search_letter_found(self, mock_input, weather_repo, capsys):
        """Test search by letter with results"""
        weather_repo.search_letter()
        captured = capsys.readouterr()
        assert "Countries starting with 'a':" in captured.out
        assert "Afghanistan" in captured.out
        assert "Albania" in captured.out
        assert "Algeria" in captured.out

    @patch('builtins.input', return_value='z')
    def test_search_letter_not_found(self, mock_input, weather_repo, capsys):
        """Test search by letter with no results"""
        weather_repo.search_letter()
        captured = capsys.readouterr()
        assert "No countries found starting with that letter." in captured.out

    @patch('builtins.input', side_effect=['1', 'k'])
    def test_search_capitals_by_letter(self, mock_input, weather_repo, capsys):
        """Test search capitals by letter"""
        weather_repo.search_capitals()
        captured = capsys.readouterr()
        assert "Capitals starting with 'k':" in captured.out
        assert "Kabul" in captured.out

    @patch('builtins.input', side_effect=['2', 'afghanistan'])
    def test_search_capitals_by_country(self, mock_input, weather_repo, capsys):
        """Test search capitals by country"""
        weather_repo.search_capitals()
        captured = capsys.readouterr()
        assert "Capital of 'afghanistan' is: Kabul" in captured.out

    @patch('builtins.input', side_effect=['invalid'])
    def test_search_capitals_invalid_choice(self, mock_input, weather_repo, capsys):
        """Test search capitals with invalid choice"""
        weather_repo.search_capitals()
        captured = capsys.readouterr()
        assert "Invalid choice. Please enter 'letters' or 'country'." in captured.out

    def test_data_handling_single_year(self, weather_repo):
        """Test data handling for single year"""
        filtered_data, label = weather_repo.data_handling('Afghanistan', '2024', 'all')
        assert len(filtered_data) == 1
        assert label == '2024'
        assert filtered_data.iloc[0]['country'] == 'Afghanistan'

    def test_data_handling_both_years(self, weather_repo):
        """Test data handling for both years"""
        filtered_data, label = weather_repo.data_handling('Afghanistan', 'both', 'all')
        assert len(filtered_data) == 1
        assert label == '2024 and 2025'

    def test_data_handling_specific_month(self, weather_repo):
        """Test data handling for specific month"""
        filtered_data, label = weather_repo.data_handling('Afghanistan', '2024', '5')
        assert len(filtered_data) == 1
        assert label == '2024 in month 5'

    def test_data_handling_no_data(self, weather_repo):
        """Test data handling with no matching data"""
        filtered_data, label = weather_repo.data_handling('NonExistent', '2024', 'all')
        assert filtered_data is None

    def test_get_inputs_valid(self, weather_repo):
        """Test get_inputs with valid inputs"""
        with patch('builtins.input', side_effect=['Afghanistan', '2024', 'all']):
            country, year, month = weather_repo.get_inputs()
            assert country == 'Afghanistan'
            assert year == '2024'
            assert month == 'all'

    def test_get_inputs_invalid_country(self, weather_repo, capsys):
        """Test get_inputs with invalid country"""
        with patch('builtins.input', side_effect=['InvalidCountry', '2024', 'all']):
            result = weather_repo.get_inputs()
            assert result == (None, None, None)
            captured = capsys.readouterr()
            assert "Country not found" in captured.out

    def test_get_inputs_invalid_year(self, weather_repo, capsys):
        """Test get_inputs with invalid year"""
        with patch('builtins.input', side_effect=['Afghanistan', '2023', 'all']):
            result = weather_repo.get_inputs()
            assert result == (None, None, None)
            captured = capsys.readouterr()
            assert "Invalid year input" in captured.out

    def test_temperature_report(self, weather_repo, capsys):
        """Test temperature report functionality"""
        data = weather_repo.df[weather_repo.df['country'] == 'Afghanistan']
        with patch('builtins.input', return_value='n'):
            weather_repo.temperature_report(data, 'Afghanistan', '2024')
        
        captured = capsys.readouterr()
        assert "Temperature Report in: Afghanistan" in captured.out
        assert "26.6°C" in captured.out
        assert "Average temperature in Afghanistan" in captured.out

    def test_humidity_report(self, weather_repo, capsys):
        """Test humidity report functionality"""
        data = weather_repo.df[weather_repo.df['country'] == 'Afghanistan']
        with patch('builtins.input', return_value='n'):
            weather_repo.humidity_report(data, 'Afghanistan', '2024')
        
        captured = capsys.readouterr()
        assert "Humidity Report in: Afghanistan" in captured.out
        assert "24%" in captured.out
        assert "Average humidity in Afghanistan" in captured.out

    @patch('builtins.input', side_effect=['Afghanistan', 'Albania', 'n'])
    def test_compare_countries_success(self, mock_input, weather_repo, capsys):
        """Test successful country comparison"""
        weather_repo.compare_countries()
        captured = capsys.readouterr()
        assert "Afghanistan vs Albania - Weather Comparison" in captured.out
        assert "Temperature:" in captured.out
        assert "Humidity:" in captured.out
        assert "Wind Speed:" in captured.out

    @patch('builtins.input', side_effect=['InvalidCountry'])
    def test_compare_countries_invalid_first(self, mock_input, weather_repo, capsys):
        """Test country comparison with invalid first country"""
        weather_repo.compare_countries()
        captured = capsys.readouterr()
        assert "Country 'Invalidcountry' not found" in captured.out

    @patch('builtins.input', side_effect=['Afghanistan', 'InvalidCountry'])
    def test_compare_countries_invalid_second(self, mock_input, weather_repo, capsys):
        """Test country comparison with invalid second country"""
        weather_repo.compare_countries()
        captured = capsys.readouterr()
        assert "Country 'Invalidcountry' not found" in captured.out

    @patch('builtins.input', side_effect=['Afghanistan', 'Afghanistan'])
    def test_compare_countries_same_country(self, mock_input, weather_repo, capsys):
        """Test country comparison with same country"""
        weather_repo.compare_countries()
        captured = capsys.readouterr()
        assert "Please select two different countries" in captured.out

    def test_weather_statistics(self, weather_repo, capsys):
        """Test weather statistics display"""
        with patch('builtins.input', return_value='5'):
            weather_repo.weather_statistics()
        
        captured = capsys.readouterr()
        assert "Global Weather Statistics" in captured.out
        assert "Temperature Analytics" in captured.out
        assert "Hottest:" in captured.out
        assert "Coldest:" in captured.out
        assert "Bangladesh" in captured.out  # Should be hottest at 38.4°C

    def test_top_countries_hottest(self, weather_repo, capsys):
        """Test top countries functionality for hottest"""
        weather_repo.top_countries('temperature_celsius', 'Hottest', '°C', ascending=False)
        captured = capsys.readouterr()
        assert "Top 10 Hottest Weathers" in captured.out
        assert "Bangladesh" in captured.out

    def test_top_countries_coldest(self, weather_repo, capsys):
        """Test top countries functionality for coldest"""
        weather_repo.top_countries('temperature_celsius', 'Coldest', '°C', ascending=True)
        captured = capsys.readouterr()
        assert "Top 10 Coldest Weathers" in captured.out
        assert "Albania" in captured.out  # Should be coldest at 19.0°C

    def test_extreme_weather(self, weather_repo, capsys):
        """Test extreme weather detection"""
        weather_repo.extreme_weather()
        captured = capsys.readouterr()
        assert "Extreme Weather Alerts" in captured.out
        # No extreme weather should be found in our test data
        assert "EXTREME HEAT" not in captured.out or "No" in captured.out

    def test_regional_comparison(self, weather_repo, capsys):
        """Test regional comparison functionality"""
        weather_repo.regional_comparison()
        captured = capsys.readouterr()
        assert "Regional Weather Comparison" in captured.out
        assert "Region" in captured.out
        assert "Avg Temp" in captured.out

    @patch('builtins.input', side_effect=['Afghanistan', '2024', 'all'])
    def test_check_country_temperature(self, mock_input, weather_repo, capsys):
        """Test check_country method for temperature"""
        with patch.object(weather_repo, 'temperature_report') as mock_temp_report:
            weather_repo.check_country(4)
            mock_temp_report.assert_called_once()

    @patch('builtins.input', side_effect=['Afghanistan', '2024', 'all'])
    def test_check_country_humidity(self, mock_input, weather_repo, capsys):
        """Test check_country method for humidity"""
        with patch.object(weather_repo, 'humidity_report') as mock_humidity_report:
            weather_repo.check_country(5)
            mock_humidity_report.assert_called_once()

    @patch('builtins.input', side_effect=['InvalidCountry', '2024', 'all'])
    def test_check_country_invalid_input(self, mock_input, weather_repo):
        """Test check_country with invalid inputs"""
        # Should return early due to invalid country
        weather_repo.check_country(4)
        # No assertion needed - just ensuring no exception is raised

    def test_show_detailed_comparison(self, weather_repo, capsys):
        """Test detailed comparison functionality"""
        data1 = weather_repo.df.iloc[0]  # Afghanistan
        data2 = weather_repo.df.iloc[1]  # Albania
        weather_repo._show_detailed_comparison(data1, data2, 'Afghanistan', 'Albania')
        
        captured = capsys.readouterr()
        assert "Detailed Weather Comparison" in captured.out
        assert "Feels Like Temperature" in captured.out
        assert "UV Index" in captured.out

    def test_empty_dataframe(self, tmp_path):
        """Test behavior with empty dataframe"""
        empty_data = pd.DataFrame()
        csv_file = tmp_path / "empty.csv"
        empty_data.to_csv(csv_file, index=False)
        
        repo = GlobalWeatherRepository(str(csv_file))
        assert len(repo.df) == 0
        assert len(repo.countries) == 0

    def test_extreme_weather_with_extreme_data(self, tmp_path):
        """Test extreme weather detection with actual extreme values"""
        extreme_data = pd.DataFrame({
            'country': ['HotCountry', 'ColdCountry', 'HumidCountry', 'DryCountry', 'WindyCountry'],
            'city': ['Hot', 'Cold', 'Humid', 'Dry', 'Windy'],
            'temperature_celsius': [45.0, -15.0, 25.0, 25.0, 25.0],
            'humidity': [50, 50, 95, 15, 50],
            'wind_kph': [20, 20, 20, 20, 60],
            'last_updated': ['2024-05-16 12:00'] * 5
        })
        
        csv_file = tmp_path / "extreme.csv"
        extreme_data.to_csv(csv_file, index=False)
        repo = GlobalWeatherRepository(str(csv_file))
        
        # Capture output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        repo.extreme_weather()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        assert "EXTREME HEAT" in output
        assert "EXTREME COLD" in output
        assert "VERY HIGH HUMIDITY" in output
        assert "VERY LOW HUMIDITY" in output
        assert "VERY WINDY" in output