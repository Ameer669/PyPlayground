import pandas as pd
from temperature_charts import TemperatureCharts

class GlobalWeatherRepository:
    
    def __init__(self, csv_path):
        try:
            self.df = pd.read_csv(csv_path)
            self.required_columns = []
            if not all(col in self.df.columns for col in self.required_columns):
                raise ValueError(f"CSV missing required columns: {self.required_columns}")
            self.countries = self.df['country'].unique()
        except FileNotFoundError:
            print(f"Error: CSV file not found at {csv_path}")
            raise
    
    def display_menu(self):
        print("\n\n\033[1mWelcome to the Global Weather Repository!\033[0m")
        print("=" * 43, "\n")
        print("0. Exit")
        print("1. View all countries")
        print("2. Search for countries with a specific letter")
        print("3. Search for capitals of countries")
        print("4. Check temperature in a specific country")
        print("5. Check humidity in a specific country")
        print("6. Compare countries")   
        print("7. Weather statistics")  
        print("8. Advanced search")     # Feature
        print("9. Weather alerts")      # Feature
        print("10. Export data")        # Feature
        print("11. Generate report")    # Feature
        print("12. Travel recommendations")  # Feature
        print("13. Weather trends")     # Feature
        print("14. Manage favorites")   # Feature

    # Choice 1: View all countries
    def view_all(self):
        print("\n\033[1mList of All Countries\033[0m")
        print("=" * 34)
        print(*self.countries, sep='\n')
    
    # Choice 2: Search for countries with a specific letter
    def search_letter(self):
        print("\n\033[1mSearch for Countries\033[0m")
        print("=" * 34)
        
        letter = input("\nEnter a letter to search for countries: ").lower()
        filtered_countries = [c for c in self.countries if c.lower().startswith(letter)]
        
        if not filtered_countries:
            print("No countries found starting with that letter.")
        else:
            print(f"\nCountries starting with '{letter}':")
            print(*filtered_countries, sep='\n')
    
    # Choice 3: Search for capitals of countries
    def search_capitals(self):
        print("\n\033[1mSearch for Capitals\033[0m")
        print("=" * 34)
        
        choose = input("\nDo you want to search by 1)letters or by 2)country? ").lower().strip()
        
        if choose == "letters" or choose == "1":
            letter = input("\nEnter a letter to search for capitals: ").lower()
            filtered_capitals = self.df['city'][self.df['city'].str.lower().str.startswith(letter)].drop_duplicates()
            if filtered_capitals.empty:
                print("No capitals found starting with that letter.")
            else:
                i = 0
                print(f"\nCapitals starting with '{letter}':\n")
                print(*filtered_capitals, sep='\n')

        elif choose == "country" or choose == "2":
            country = input("\nEnter the country name to search for its capital: ").lower()
            capitals = self.df[self.df['country'].str.lower() == country]['city'].drop_duplicates()
            if capitals.empty:
                print("No capitals found for that country.")
            else:
                print(f"\nCapital of '{country}' is: ", end="")
                print(capitals.iloc[0])
        else:
            print("Invalid choice. Please enter 'letters' or 'country'.")
            return

    # Choice 4: Check temperature in a specific country
    def temperature_report(self, data, country, label):
        print(f"\n\033[1mTemperature Report in: {country}\033[0m")
        print("=" * 34)
                
        # Display each entry
        for date, temp in zip(data['last_updated'], data['temperature_celsius']):
            print(f"\nDate: {date}")
            print(f"The temperature was {temp}°C")
        
        # Calculate and display average
        avg = data['temperature_celsius'].astype(float).mean()
        print(f"\nAverage temperature in {country} in {label}: {avg:.2f}°C")
        
        # Ask user if they want to see charts
        if len(data) >= 2:
            show_chart = input("\n Would you like to see temperature visualizations? (y/n): ").lower().strip()
            if show_chart in ['y', 'yes']:
                TemperatureCharts.display_charts(data, country, label)

    # Choice 5: Check humidity in a specific country
    def humidity_report(self, data, country, label):
        print(f"\n\033[1mHumidity Report in: {country}\033[0m")
        print("=" * 34)
        
        # Display each entry
        for date, humidity in zip(data['last_updated'], data['humidity']):
            print(f"\nDate: {date}")
            print(f"The humidity was {humidity}%")
        
        # Calculate and display average
        avg = data['humidity'].astype(float).mean()
        print(f"\nAverage humidity in {country} in {label}: {avg:.2f}%")
        
        # Ask user if they want to see charts
        if len(data) >= 2:
            show_chart = input("\n Would you like to see humidity visualizations? (y/n): ").lower().strip()
            if show_chart in ['y', 'yes']:
                TemperatureCharts.display_charts(data, country, label)
       
    # Choice 6: Compare weather between two countries 
    def compare_countries(self):
        print("\n\033[1mCompare Weather Between Countries\033[0m")
        print("=" * 34)

        country1 = input("\nEnter first country name: ").strip().title()
        if country1 not in self.countries:
            print(f"Country '{country1}' not found. Please try again.")
            return
        
        country2 = input("Enter second country name: ").strip().title()
        if country2 not in self.countries:
            print(f"Country '{country2}' not found. Please try again.")
            return
        
        if country1 == country2:
            print("Please select two different countries.")
            return
        
        data1 = self.df[self.df['country'] == country1].iloc[0]
        data2 = self.df[self.df['country'] == country2].iloc[0]
        
        print(f"\n\033[1m{country1} vs {country2} - Weather Comparison\033[0m")
        print("=" * 34)
        
        # Temperature comparison
        temp1 = data1['temperature_celsius']
        temp2 = data2['temperature_celsius']
        temp_diff = abs(temp1 - temp2)
        warmer = country1 if temp1 > temp2 else country2

        print(f"\n- Temperature:")
        print(f"   {country1}: {temp1}°C")
        print(f"   {country2}: {temp2}°C")
        print(f"   Difference: {temp_diff:.1f}°C")
        print(f"   Warmer: {warmer}")
        
        # Humidity comparison
        humidity1 = data1['humidity']
        humidity2 = data2['humidity']
        humidity_diff = abs(humidity1 - humidity2)
        more_humid = country1 if humidity1 > humidity2 else country2
        
        print(f"\n- Humidity:")
        print(f"   {country1}: {humidity1}%")
        print(f"   {country2}: {humidity2}%")
        print(f"   Difference: {humidity_diff}%")
        print(f"   More humid: {more_humid}")
        
        # Wind speed comparison
        wind1 = data1['wind_kph']
        wind2 = data2['wind_kph']
        wind_diff = abs(wind1 - wind2)
        windier = country1 if wind1 > wind2 else country2

        print(f"\n- Wind Speed:")
        print(f"   {country1}: {wind1} km/h")
        print(f"   {country2}: {wind2} km/h")
        print(f"   Difference: {wind_diff:.1f} km/h")
        print(f"   Windier: {windier}")
        
        # Weather condition comparison
        condition1 = data1['condition_text']
        condition2 = data2['condition_text']
        
        print(f"\n-  Weather Conditions:")
        print(f"   {country1}: {condition1}")
        print(f"   {country2}: {condition2}")
        
        # Pressure comparison
        pressure1 = data1['pressure_mb']
        pressure2 = data2['pressure_mb']
        pressure_diff = abs(pressure1 - pressure2)
        higher_pressure = country1 if pressure1 > pressure2 else country2
        
        print(f"\n- Atmospheric Pressure:")
        print(f"   {country1}: {pressure1} mb")
        print(f"   {country2}: {pressure2} mb")
        print(f"   Difference: {pressure_diff:.1f} mb")
        print(f"   Higher pressure: {higher_pressure}")
        
        # Overall summary
        print(f"\n\033[1mSummary:\033[0m")
        
        # Determine which country has better weather
        score1 = 0
        score2 = 0
        
        # Temperature score
        if 18 <= temp1 <= 26:
            score1 += 1
        if 18 <= temp2 <= 26:
            score2 += 1

        # Humidity score
        if 40 <= humidity1 <= 60:
            score1 += 1
        if 40 <= humidity2 <= 60:
            score2 += 1
        
        # Wind score
        if 5 <= wind1 <= 20:
            score1 += 1
        if 5 <= wind2 <= 20:
            score2 += 1
        
        # Clear weather gets points
        if any(word in condition1.lower() for word in ['sunny', 'clear', 'partly cloudy']):
            score1 += 1
        if any(word in condition2.lower() for word in ['sunny', 'clear', 'partly cloudy']):
            score2 += 1
        
        if score1 > score2:
            print(f"{country1} has more favorable weather conditions overall.")
        elif score2 > score1:
            print(f"{country2} has more favorable weather conditions overall.")
        else:
            print("Both countries have similar weather conditions.")

        # additional details?
        show_details = input("\nWould you like to see additional weather details? (y/n): ").lower().strip()
        if show_details in ['y', 'yes']:
            self.detailed_comparison(data1, data2, country1, country2)
     
    # Choice 7: Weather statistics
    def weather_statistics(self):
        print("\n\033[1mGlobal Weather Statistics\033[0m")
        print("=" * 50)
        
        # Temperature Statistics
        print("\n  \033[1mTemperature Analytics\033[0m")
        print("-" * 30)
        
        hottest_idx = self.df['temperature_celsius'].idxmax()
        coldest_idx = self.df['temperature_celsius'].idxmin()
        avg_temp = self.df['temperature_celsius'].mean()
        
        hottest_country = self.df.loc[hottest_idx, 'country']
        hottest_temp = self.df.loc[hottest_idx, 'temperature_celsius']
        coldest_country = self.df.loc[coldest_idx, 'country']
        coldest_temp = self.df.loc[coldest_idx, 'temperature_celsius']
        
        print(f"- Hottest: {hottest_country} - {hottest_temp}°C")
        print(f"- Coldest: {coldest_country} - {coldest_temp}°C")
        print(f"- Global Average: {avg_temp:.1f}°C")
        
        # Humidity Statistics
        print("\n \033[1mHumidity Analytics\033[0m")
        print("-" * 30)
        
        most_humid_idx = self.df['humidity'].idxmax()
        least_humid_idx = self.df['humidity'].idxmin()
        avg_humidity = self.df['humidity'].mean()
        
        most_humid_country = self.df.loc[most_humid_idx, 'country']
        most_humid_val = self.df.loc[most_humid_idx, 'humidity']
        least_humid_country = self.df.loc[least_humid_idx, 'country']
        least_humid_val = self.df.loc[least_humid_idx, 'humidity']
        
        print(f"- Most Humid: {most_humid_country} - {most_humid_val}%")
        print(f"-  Least Humid: {least_humid_country} - {least_humid_val}%")
        print(f"- Global Average: {avg_humidity:.1f}%")
        
        # Wind Statistics
        print("\n  \033[1mWind Analytics\033[0m")
        print("-" * 30)
        
        windiest_idx = self.df['wind_kph'].idxmax()
        calmest_idx = self.df['wind_kph'].idxmin()
        avg_wind = self.df['wind_kph'].mean()
        
        windiest_country = self.df.loc[windiest_idx, 'country']
        windiest_speed = self.df.loc[windiest_idx, 'wind_kph']
        calmest_country = self.df.loc[calmest_idx, 'country']
        calmest_speed = self.df.loc[calmest_idx, 'wind_kph']
        
        print(f"-  Windiest: {windiest_country} - {windiest_speed} km/h")
        print(f"- Calmest: {calmest_country} - {calmest_speed} km/h")
        print(f"- Global Average: {avg_wind:.1f} km/h")
        
        # Pressure Statistics
        print("\n  \033[1mPressure Analytics\033[0m")
        print("-" * 30)
        
        highest_pressure_idx = self.df['pressure_mb'].idxmax()
        lowest_pressure_idx = self.df['pressure_mb'].idxmin()
        avg_pressure = self.df['pressure_mb'].mean()
        
        highest_pressure_country = self.df.loc[highest_pressure_idx, 'country']
        highest_pressure_val = self.df.loc[highest_pressure_idx, 'pressure_mb']
        lowest_pressure_country = self.df.loc[lowest_pressure_idx, 'country']
        lowest_pressure_val = self.df.loc[lowest_pressure_idx, 'pressure_mb']
        
        print(f"- Highest Pressure: {highest_pressure_country} - {highest_pressure_val} mb")
        print(f"- Lowest Pressure: {lowest_pressure_country} - {lowest_pressure_val} mb")
        print(f"- Global Average: {avg_pressure:.1f} mb")
        
        # Weather Conditions Analysis
        print("\n  \033[1mWeather Conditions\033[0m")
        print("-" * 30)
        
        condition_counts = self.df['condition_text'].value_counts()
        print("Most Common Weather Conditions:")
        for i, (condition, count) in enumerate(condition_counts.head(5).items(), 1):
            percentage = (count / len(self.df)) * 100
            print(f"{i}. {condition}: {count} times ({percentage:.1f}%)")
        
        # Temperature Categories
        print("\n  \033[1mTemperature Categories\033[0m")
        print("-" * 30)
        
        very_hot = len(self.df[self.df['temperature_celsius'] > 35])
        hot = len(self.df[(self.df['temperature_celsius'] > 25) & (self.df['temperature_celsius'] <= 35)])
        mild = len(self.df[(self.df['temperature_celsius'] > 15) & (self.df['temperature_celsius'] <= 25)])
        cool = len(self.df[(self.df['temperature_celsius'] > 5) & (self.df['temperature_celsius'] <= 15)])
        cold = len(self.df[self.df['temperature_celsius'] <= 5])
        
        total_countries = len(self.df)
        
        print(f"- Very Hot (>35°C): {very_hot} times ({(very_hot/total_countries)*100:.1f}%)")
        print(f"- Hot (25-35°C): {hot} times ({(hot/total_countries)*100:.1f}%)")
        print(f"-  Mild (15-25°C): {mild} times ({(mild/total_countries)*100:.1f}%)")
        print(f"-  Cool (5-15°C): {cool} times ({(cool/total_countries)*100:.1f}%)")
        print(f"-  Cold (≤5°C): {cold} times ({(cold/total_countries)*100:.1f}%)")
        
        # Interactive Options
        print("\n\033[1mDetailed Analytics Options:\033[0m")
        print("1. Top 10 hottest countries")
        print("2. Top 10 coldest countries") 
        print("3. Countries with extreme weather")
        print("4. Return to main menu")
        
        while True:
            try:
                detail_choice = int(input("\nChoose an option (1-4): "))
                
                if detail_choice == 1:
                    self.top_countries('temperature_celsius', 'Hottest', '°C', ascending=False)
                elif detail_choice == 2:
                    self.top_countries('temperature_celsius', 'Coldest', '°C', ascending=True)
                elif detail_choice == 3:
                    self.extreme_weather()
                elif detail_choice == 4:
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    # Choice 8: Advanced search
    def advanced_search(self):
        print("\n\033[1mAdvanced Weather Search\033[0m")
        print("=" * 34)
        
        print("\nSearch Options:")
        print("1. Temperature range search")
        print("2. Humidity range search")
        print("3. Wind speed range search")
        print("4. Weather condition search")
        print("5. Multi-criteria search")
        print("6. Return to main menu")
        
        while True:
            try:
                search_choice = int(input("\nChoose search type (1-6): "))
                
                if search_choice == 1:
                    self.temperature_range_search()
                elif search_choice == 2:
                    self.humidity_range_search()
                elif search_choice == 3:
                    self.wind_range_search()
                elif search_choice == 4:
                    self.condition_search()
                elif search_choice == 5:
                    self.multi_criteria()
                elif search_choice == 6:
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    # Choice 12: Travel recommendations
    def travel_recommendations(self):
        print("\n\033[1mTravel Recommendations\033[0m")
        print("=" * 34)
        
        print("\nRecommendation Options:")
        print("1. Best weather destinations")
        print("2. Seasonal recommendations")
        print("3. Activity-based recommendations")
        print("4. Budget-friendly weather destinations")
        print("5. Return to main menu")
        
        while True:
            try:
                rec_choice = int(input("\nChoose recommendation type (1-5): "))
                
                if rec_choice == 1:
                    self.weather_destinations()
                elif rec_choice == 2:
                    self.seasonal_recommendations()
                elif rec_choice == 3:
                    self.activity_recommendations()
                elif rec_choice == 4:
                    self.budgetWeather_destinations()
                elif rec_choice == 5:
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except ValueError:
                print("Invalid input. Please enter a number.")
  
    def detailed_comparison(self, data1, data2, country1, country2):
        print(f"\n\033[1mDetailed Weather Comparison\033[0m")
        print("=" * 34)
        
        details = [
            ('- Feels Like Temperature', 'feels_like_celsius', '°C'),
            ('- Visibility', 'visibility_km', 'km'),
            ('- UV Index', 'uv_index', ''),
            ('- Precipitation', 'precip_mm', 'mm'),
            ('- Wind Gust', 'gust_kph', 'km/h'),
            ('- Moon Phase', 'moon_phase', ''),
            ('- Moon Illumination', 'moon_illumination', '%')
        ]
        
        for label, column, unit in details:
            if column in data1.index and column in data2.index:
                value1 = data1[column]
                value2 = data2[column]
                
                print(f"\n{label}:")
                print(f"   {country1}: {value1}{unit}")
                print(f"   {country2}: {value2}{unit}")
                
                if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    diff = abs(value1 - value2)
                    print(f"   Difference: {diff:.1f}{unit}")

    def check_country(self, choice):
        
        # Get user inputs
        country, year_input, month_input = self.get_inputs()
        if not country:
            return
        
        # Process data
        filtered_data, label = self.data_handling(country, year_input, month_input)
        if filtered_data is None:
            print(f"\nNo data available for {country} in {label}.")
            return

        # Handle multiple choices
        if choice == 4:
            self.temperature_report(filtered_data, country, label)
        elif choice == 5:
            self.humidity_report(filtered_data, country, label)
    
    def get_inputs(self):
        # Get country input
        co = input("\nEnter the country name: ").strip().title()
        if co not in self.countries:
            print("Country not found. Please try again.")
            return None, None, None
        
        # Get year input
        year_input = input("Enter year (2024, 2025, both): ").strip().lower()
        if year_input not in ['2024', '2025', 'both']:
            print("Invalid year input.")
            return None, None, None
        
        # Get month input
        month_input = input("Enter month (1-12) or 'all' for all months: ").strip().lower()
        if month_input != 'all' and not month_input.isdigit():
            print("Invalid month input.")
            return None, None, None
        
        return co, year_input, month_input
    
    def data_handling(self, country, year_input, month_input):
        
        """Filter data and return processed results."""
        
        # Filter by country
        rows = self.df[self.df['country'] == country]
        
        # Filter by year
        if year_input == 'both':
            filtered = rows[rows['last_updated'].str[:4].isin(['2024', '2025'])]
            label = "2024 and 2025"
        else:
            filtered = rows[rows['last_updated'].str[:4] == year_input]
            label = year_input
        
        # Check if data exists
        if filtered.empty:
            return None, label
        
        # Filter by month if specified
        if month_input != 'all':
            filtered = filtered[filtered['last_updated'].str[5:7] == month_input.zfill(2)]
            label += f" in month {month_input}"
        
        return filtered, label    

    def top_countries(self, column, title, unit, ascending=False):
        print(f"\n \033[1mTop 10 {title} Weathers\033[0m")
        print("-" * 40)
        
        sorted_data = self.df.nlargest(10, column) if not ascending else self.df.nsmallest(10, column)
        
        for i, (_, row) in enumerate(sorted_data.iterrows(), 1):
            print(f"{i:2d}. {row['country']:<20} {row[column]}{unit}")

    def extreme_weather(self):
        print(f"\n  \033[1mExtreme Weather Alerts\033[0m")
        print("-" * 40)
        
        # Extreme temperature alerts
        extreme_hot = self.df[self.df['temperature_celsius'] > 40]
        extreme_cold = self.df[self.df['temperature_celsius'] < -10]
        very_humid = self.df[self.df['humidity'] > 90]
        very_dry = self.df[self.df['humidity'] < 20]
        very_windy = self.df[self.df['wind_kph'] > 50]
        
        # Show summary if no extreme weather found
        if (extreme_hot.empty and extreme_cold.empty and very_humid.empty 
            and very_dry.empty and very_windy.empty):
            print("\n No extreme weather conditions detected globally!")
            return
        
        # Define categories for processing
        categories = [
            ("EXTREME HEAT (>40°C)", extreme_hot, 'temperature_celsius', '°C', False),
            ("EXTREME COLD (<-10°C)", extreme_cold, 'temperature_celsius', '°C', True),
            ("VERY HIGH HUMIDITY (>90%)", very_humid, 'humidity', '%', False),
            ("VERY LOW HUMIDITY (<20%)", very_dry, 'humidity', '%', True),
            ("VERY WINDY (>50 km/h)", very_windy, 'wind_kph', 'km/h', False)
        ]
        
        # Display overview first
        for title, data, column, unit, ascending in categories:
            if not data.empty:
                print(f"\n- {title}: Happened {len(data)} times")
        
        # Show top 15 from each category directly
        max_results = 15
        for title, data, column, unit, ascending in categories:
            if not data.empty:
                print(f"\n- {title}:")
                print("-" * 40)
                
                # Sort and get top results
                top_results = data.nlargest(max_results, column) if not ascending else data.nsmallest(max_results, column)
                
                for i, (_, row) in enumerate(top_results.iterrows(), 1):
                    print(f"{i:2d}. {row['country']:<20} {row[column]}{unit}")
                
                if len(data) > max_results:
                    print(f"    ... and {len(data) - max_results} more times")

    def temperature_range_search(self):
        print("\n\033[1mTemperature Range Search\033[0m")
        print("-" * 30)
        
        try:
            min_temp = float(input("Enter minimum temperature (°C): "))
            max_temp = float(input("Enter maximum temperature (°C): "))
            
            if min_temp > max_temp:
                print("Minimum temperature cannot be greater than maximum temperature.")
                return
            
            results = self.df[(self.df['temperature_celsius'] >= min_temp) & 
                             (self.df['temperature_celsius'] <= max_temp)]
            
            if results.empty:
                print(f"No countries found with temperature between {min_temp}°C and {max_temp}°C")
                return
            
            print(f"\nCountries with temperature between {min_temp}°C and {max_temp}°C:")
            print(f"Showing top 15 results out of {len(results)} total matches:")
            print("-" * 50)
            
            for _, row in results.head(15).iterrows():
                print(f"{row['country']:<20} {row['temperature_celsius']}°C - {row['condition_text']}")
            
            if len(results) > 15:
                print(f"\n... and {len(results) - 15} more results. Use more specific criteria to narrow down.")
                
        except ValueError:
            print("Please enter valid numbers for temperature.")
    
    def humidity_range_search(self):
        print("\n\033[1mHumidity Range Search\033[0m")
        print("-" * 30)
        
        try:
            min_humidity = float(input("Enter minimum humidity (%): "))
            max_humidity = float(input("Enter maximum humidity (%): "))
            
            if min_humidity > max_humidity:
                print("Minimum humidity cannot be greater than maximum humidity.")
                return
            
            results = self.df[(self.df['humidity'] >= min_humidity) & 
                             (self.df['humidity'] <= max_humidity)]
            
            if results.empty:
                print(f"No countries found with humidity between {min_humidity}% and {max_humidity}%")
                return
            
            print(f"\nCountries with humidity between {min_humidity}% and {max_humidity}%:")
            print(f"Showing top 15 results out of {len(results)} total matches:")
            print("-" * 50)
            
            for _, row in results.head(15).iterrows():
                print(f"{row['country']:<20} {row['humidity']}% - {row['condition_text']}")
            
            if len(results) > 15:
                print(f"\n... and {len(results) - 15} more results. Use more specific criteria to narrow down.")
                
        except ValueError:
            print("Please enter valid numbers for humidity.")
    
    def wind_range_search(self):
        print("\n\033[1mWind Speed Range Search\033[0m")
        print("-" * 30)
        
        try:
            min_wind = float(input("Enter minimum wind speed (km/h): "))
            max_wind = float(input("Enter maximum wind speed (km/h): "))
            
            if min_wind > max_wind:
                print("Minimum wind speed cannot be greater than maximum wind speed.")
                return
            
            results = self.df[(self.df['wind_kph'] >= min_wind) & 
                             (self.df['wind_kph'] <= max_wind)]
            
            if results.empty:
                print(f"No countries found with wind speed between {min_wind} km/h and {max_wind} km/h")
                return
            
            print(f"\nCountries with wind speed between {min_wind} km/h and {max_wind} km/h:")
            print(f"Showing top 15 results out of {len(results)} total matches:")
            print("-" * 50)
            
            for _, row in results.head(15).iterrows():
                print(f"{row['country']:<20} {row['wind_kph']} km/h - {row['condition_text']}")
            
            if len(results) > 15:
                print(f"\n... and {len(results) - 15} more results. Use more specific criteria to narrow down.")
                
        except ValueError:
            print("Please enter valid numbers for wind speed.")
    
    def condition_search(self):
        print("\n\033[1mWeather Condition Search\033[0m")
        print("-" * 30)
        
        condition = input("Enter weather condition to search for: ").strip()
        
        if not condition:
            print("Please enter a valid condition.")
            return
        
        results = self.df[self.df['condition_text'].str.contains(condition, case=False, na=False)]
        
        if results.empty:
            print(f"No countries found with weather condition containing '{condition}'")
            return
        
        print(f"\nCountries with weather condition containing '{condition}':")
        print(f"Showing top 15 results out of {len(results)} total matches:")
        print("-" * 50)
        
        for _, row in results.head(15).iterrows():
            print(f"{row['country']:<20} {row['condition_text']} - {row['temperature_celsius']}°C")
        
        if len(results) > 15:
            print(f"\n... and {len(results) - 15} more results. Use more specific criteria to narrow down.")
    
    def multi_criteria(self):
        print("\n\033[1mMulti-Criteria Search\033[0m")
        print("-" * 30)
        
        try:
            # Temperature criteria
            use_temp = input("Filter by temperature? (y/n): ").lower().strip() in ['y', 'yes']
            if use_temp:
                min_temp = float(input("Minimum temperature (°C): "))
                max_temp = float(input("Maximum temperature (°C): "))
            
            # Humidity criteria
            use_humidity = input("Filter by humidity? (y/n): ").lower().strip() in ['y', 'yes']
            if use_humidity:
                min_humidity = float(input("Minimum humidity (%): "))
                max_humidity = float(input("Maximum humidity (%): "))
            
            # Wind criteria
            use_wind = input("Filter by wind speed? (y/n): ").lower().strip() in ['y', 'yes']
            if use_wind:
                min_wind = float(input("Minimum wind speed (km/h): "))
                max_wind = float(input("Maximum wind speed (km/h): "))
            
            # Condition criteria
            use_condition = input("Filter by weather condition? (y/n): ").lower().strip() in ['y', 'yes']
            if use_condition:
                condition = input("Weather condition contains: ").strip()
            
            # Apply filters
            results = self.df.copy()
            
            if use_temp:
                results = results[(results['temperature_celsius'] >= min_temp) & 
                                (results['temperature_celsius'] <= max_temp)]
            
            if use_humidity:
                results = results[(results['humidity'] >= min_humidity) & 
                                (results['humidity'] <= max_humidity)]
            
            if use_wind:
                results = results[(results['wind_kph'] >= min_wind) & 
                                (results['wind_kph'] <= max_wind)]
            
            if use_condition:
                results = results[results['condition_text'].str.contains(condition, case=False, na=False)]
            
            if results.empty:
                print("No countries found matching all criteria.")
                return
            
            print(f"\nCountries matching all criteria ({len(results)} found):")
            print(f"Showing top 15 results:")
            print("-" * 70)
            print(f"{'Country':<20} {'Temp(°C)':<10} {'Humidity(%)':<12} {'Wind(km/h)':<12} {'Condition'}")
            print("-" * 70)
            
            for _, row in results.head(15).iterrows():
                print(f"{row['country']:<20} {row['temperature_celsius']:<10} {row['humidity']:<12} {row['wind_kph']:<12} {row['condition_text']}")
            
            if len(results) > 15:
                print(f"\n... and {len(results) - 15} more results. Use more specific criteria to narrow down.")
                
        except ValueError:
            print("Please enter valid numbers.")
  
    def weather_destinations(self):
        print("\n\033[1mBest Weather Destinations\033[0m")
        print("-" * 40)
        
        # Define ideal weather criteria
        ideal_temp_min, ideal_temp_max = 20, 28
        ideal_humidity_min, ideal_humidity_max = 40, 70
        ideal_wind_max = 25
        
        # Filter for ideal conditions
        ideal_weather = self.df[
            (self.df['temperature_celsius'] >= ideal_temp_min) &
            (self.df['temperature_celsius'] <= ideal_temp_max) &
            (self.df['humidity'] >= ideal_humidity_min) &
            (self.df['humidity'] <= ideal_humidity_max) &
            (self.df['wind_kph'] <= ideal_wind_max)
        ]
        
        # Prefer clear/sunny conditions
        clear_conditions = ['sunny', 'clear', 'partly cloudy', 'fair']
        ideal_weather = ideal_weather[
            ideal_weather['condition_text'].str.lower().str.contains('|'.join(clear_conditions), na=False)
        ]
        
        if ideal_weather.empty:
            print("No destinations found with ideal weather conditions.")
            # Show best available alternatives
            print("\nBest available alternatives:")
            alternatives = self.df[
                (self.df['temperature_celsius'] >= 15) &
                (self.df['temperature_celsius'] <= 32) &
                (self.df['humidity'] <= 80)
            ].head(10)
            
            for _, row in alternatives.iterrows():
                print(f"{row['country']:<20} {row['temperature_celsius']}°C, {row['humidity']}%, {row['condition_text']}")
            return
        
        print(f"Top destinations with ideal weather conditions:")
        print("-" * 50)
        print(f"{'Rank':<5} {'Country':<20} {'Temp(°C)':<10} {'Humidity(%)':<12} {'Condition'}")
        print("-" * 50)
        
        # Sort by temperature preference (closer to 24°C is better)
        ideal_weather['temp_score'] = abs(ideal_weather['temperature_celsius'] - 24)
        best_destinations = ideal_weather.nsmallest(10, 'temp_score')
        
        for i, (_, row) in enumerate(best_destinations.iterrows(), 1):
            print(f"{i:<5} {row['country']:<20} {row['temperature_celsius']:<10} {row['humidity']:<12} {row['condition_text']}")
        
        print(f"\n- Recommendation: These destinations offer perfect weather for sightseeing and outdoor activities!")
    
    def seasonal_recommendations(self):
        print("\n\033[1mSeasonal Travel Recommendations\033[0m")
        print("-" * 40)
        
        print("\nChoose your preferred season:")
        print("1. Spring/Summer (Warm weather)")
        print("2. Fall/Winter (Cool weather)")
        print("3. All-year destinations")
        
        try:
            season_choice = int(input("\nEnter your choice (1-3): "))
            
            if season_choice == 1:
                # Warm weather destinations
                warm_weather = self.df[
                    (self.df['temperature_celsius'] >= 22) &
                    (self.df['temperature_celsius'] <= 35) &
                    (self.df['humidity'] <= 75)
                ]
                
                print(f"\n- Best Warm Weather Destinations:")
                print("-" * 40)
                
                for _, row in warm_weather.head(10).iterrows():
                    print(f"{row['country']:<20} {row['temperature_celsius']}°C - Perfect for beach and outdoor activities")
                    
            elif season_choice == 2:
                # Cool weather destinations
                cool_weather = self.df[
                    (self.df['temperature_celsius'] >= 5) &
                    (self.df['temperature_celsius'] <= 20) &
                    (self.df['wind_kph'] <= 30)
                ]
                
                print(f"\n- Best Cool Weather Destinations:")
                print("-" * 40)
                
                for _, row in cool_weather.head(10).iterrows():
                    print(f"{row['country']:<20} {row['temperature_celsius']}°C - Great for hiking and cultural exploration")
                    
            elif season_choice == 3:
                # All-year destinations (mild temperatures)
                all_year = self.df[
                    (self.df['temperature_celsius'] >= 18) &
                    (self.df['temperature_celsius'] <= 26) &
                    (self.df['humidity'] >= 45) &
                    (self.df['humidity'] <= 65)
                ]
                
                print(f"\n- Best All-Year Destinations:")
                print("-" * 40)
                
                for _, row in all_year.head(10).iterrows():
                    print(f"{row['country']:<20} {row['temperature_celsius']}°C - Comfortable weather year-round")
            else:
                print("Invalid choice.")
                
        except ValueError:
            print("Please enter a valid number.")
    
    def activity_recommendations(self):
        print("\n\033[1mActivity-Based Recommendations\033[0m")
        print("-" * 40)
        
        print("\nChoose your preferred activity:")
        print("1. Beach and water sports")
        print("2. Hiking and trekking")
        print("3. City exploration and museums")
        print("4. Photography and sightseeing")
        print("5. Winter sports")
        
        try:
            activity_choice = int(input("\nEnter your choice (1-5): "))
            
            if activity_choice == 1:
                # Beach weather: warm, not too humid, low wind
                beach_weather = self.df[
                    (self.df['temperature_celsius'] >= 25) &
                    (self.df['temperature_celsius'] <= 35) &
                    (self.df['humidity'] <= 70) &
                    (self.df['wind_kph'] <= 20)
                ]
                
                print(f"\n- Best Beach Destinations:")
                print("-" * 40)
                
                for _, row in beach_weather.head(8).iterrows():
                    print(f"{row['country']:<20} {row['temperature_celsius']}°C, {row['wind_kph']} km/h wind - Perfect for beach activities")
                    
            elif activity_choice == 2:
                # Hiking weather: mild temperature, low humidity, moderate wind
                hiking_weather = self.df[
                    (self.df['temperature_celsius'] >= 15) &
                    (self.df['temperature_celsius'] <= 25) &
                    (self.df['humidity'] <= 60) &
                    (self.df['wind_kph'] <= 25)
                ]
                
                print(f"\n- Best Hiking Destinations:")
                print("-" * 40)
                
                for _, row in hiking_weather.head(8).iterrows():
                    print(f"{row['country']:<20} {row['temperature_celsius']}°C, {row['humidity']}% humidity - Ideal for outdoor adventures")
                    
            elif activity_choice == 3:
                # City exploration: comfortable temperature, any weather mostly
                city_weather = self.df[
                    (self.df['temperature_celsius'] >= 10) &
                    (self.df['temperature_celsius'] <= 30) &
                    (self.df['wind_kph'] <= 35)
                ]
                
                print(f"\n- Best City Exploration Destinations:")
                print("-" * 40)
                
                for _, row in city_weather.head(8).iterrows():
                    print(f"{row['country']:<20} {row['temperature_celsius']}°C - Comfortable for walking and sightseeing")
                    
            elif activity_choice == 4:
                # Photography: clear conditions preferred
                clear_conditions = ['sunny', 'clear', 'partly cloudy']
                photo_weather = self.df[
                    (self.df['temperature_celsius'] >= 12) &
                    (self.df['temperature_celsius'] <= 28) &
                    (self.df['condition_text'].str.lower().str.contains('|'.join(clear_conditions), na=False))
                ]
                
                print(f"\n- Best Photography Destinations:")
                print("-" * 40)
                
                for _, row in photo_weather.head(8).iterrows():
                    print(f"{row['country']:<20} {row['condition_text']} - Great visibility for photography")
                    
            elif activity_choice == 5:
                # Winter sports: cold temperature
                winter_weather = self.df[
                    (self.df['temperature_celsius'] <= 5)
                ]

                print(f"\n- Best Winter Sports Destinations:")
                print("-" * 40)
                
                if winter_weather.empty:
                    print("No destinations found with suitable winter sports weather in current data.")
                else:
                    for _, row in winter_weather.head(8).iterrows():
                        print(f"{row['country']:<20} {row['temperature_celsius']}°C - Perfect for winter activities")
            else:
                print("Invalid choice.")
                
        except ValueError:
            print("Please enter a valid number.")
    
    def budgetWeather_destinations(self):
        print("\n\033[1mBudget-Friendly Weather Destinations\033[0m")
        print("-" * 40)
        
        # Define generally budget-friendly regions (this is a simplified approach)
        # In a real application, you might have cost data
        print("- Destinations with great weather that are typically budget-friendly:")
        print("-" * 60)
        
        # Look for pleasant weather conditions
        budget_weather = self.df[
            (self.df['temperature_celsius'] >= 18) &
            (self.df['temperature_celsius'] <= 32) &
            (self.df['humidity'] <= 75)
        ]
        
        # Common budget-friendly countries (simplified list)
        budget_countries = ['India', 'Thailand', 'Vietnam', 'Indonesia', 'Philippines', 
                           'Mexico', 'Guatemala', 'Nepal', 'Sri Lanka', 'Malaysia']
        
        budget_destinations = budget_weather[budget_weather['country'].isin(budget_countries)]
        
        if budget_destinations.empty:
            print("No budget-friendly destinations found in current weather data.")
            print("\nShowing all destinations with pleasant weather:")
            for _, row in budget_weather.head(10).iterrows():
                print(f"{row['country']:<20} {row['temperature_celsius']}°C, {row['humidity']}% - {row['condition_text']}")
        else:
            print(f"{'Country':<20} {'Temperature':<12} {'Humidity':<12} {'Condition'}")
            print("-" * 60)
            
            for _, row in budget_destinations.iterrows():
                print(f"{row['country']:<20} {row['temperature_celsius']}°C{'':<7} {row['humidity']}%{'':<7} {row['condition_text']}")
        
        print(f"\n- Tip: Consider visiting during shoulder seasons for better prices and pleasant weather!")

    def run(self):
        while True:
            try:
                self.display_menu()
                choice = int(input("\nPlease enter your choice: "))
                
                if choice == 0:
                    ch = input("\nAre you sure you want to exit? (y/n): ").lower().strip()
                    if ch in ['y', 'yes']:
                        ch2 = input("Are you really sure? (y/n): ").lower().strip()
                        if ch2 in ['y', 'yes']:
                            ch3 = input("Last chance! (y/n): ").lower().strip()
                            if ch3 in ['y', 'yes']:
                                ch4 = input("Think about it! (y/n): ").lower().strip()
                                if ch4 in ['y', 'yes']:
                                    input("Just stop the program then! ")
                                    print("\n\n\n\n\n", "\033[1mStupid!\033[0m"*10000, "\n\n\n\n\n")
                                    print("  Happy now? Goodbye!\n\n")
                                    break
                                else:
                                    continue
                        else:
                            continue
                    else:
                        continue
                elif choice == 1:
                    self.view_all()
                elif choice == 2:
                    self.search_letter()
                elif choice == 3:
                    self.search_capitals()
                elif choice == 4:
                    self.check_country(choice) # Temperature
                elif choice == 5:
                    self.check_country(choice) # Humidity
                elif choice == 6:
                    self.compare_countries()
                elif choice == 7:
                    self.weather_statistics()  
                elif choice == 8:
                    self.advanced_search()
                elif choice in [9, 10, 11]:
                    print("Feature coming soon!")
                elif choice == 12:
                    self.travel_recommendations()
                elif choice in [13, 14]:
                    print("Feature coming soon!")
                else:
                    print("Invalid choice, please try again.")
        
            except ValueError:
                print("Invalid input, please enter a number.")


def main():
    csv_path = r'D:\Programming\Codes\datasets\GlobalWeatherRepository.csv'
    weather_repo = GlobalWeatherRepository(csv_path)
    weather_repo.run()


if __name__ == "__main__":
    main()