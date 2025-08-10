"""
AI-generated code to demonstrate charts
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import numpy as np

# Set the style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class TemperatureCharts:
    
    @staticmethod
    def setup_plot_style():
        """Configure matplotlib and seaborn styling."""
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
    
    @staticmethod
    def line_chart(data, country, label):
        """Create a line chart showing temperature trends over time."""
        if len(data) < 2:
            print("⚠️  Need at least 2 data points for line chart")
            return
        
        TemperatureCharts.setup_plot_style()
        
        # Prepare data
        df = data.copy()
        df['date'] = pd.to_datetime(df['last_updated'])
        df['temp'] = df['temperature_celsius'].astype(float)
        df = df.sort_values('date')
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        
        # Line plot with markers
        plt.plot(df['date'], df['temp'], 
                marker='o', linewidth=2, markersize=6, 
                color='#2E86AB', markerfacecolor='#A23B72')
        
        # Customize the plot
        plt.title(f'🌡️ Temperature Trend for {country} ({label})', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Temperature (°C)', fontsize=12, fontweight='bold')
        
        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Add temperature values on points
        for i, (date, temp) in enumerate(zip(df['date'], df['temp'])):
            if i % max(1, len(df) // 10) == 0:  # Show every nth label to avoid crowding
                plt.annotate(f'{temp:.1f}°C', 
                           (date, temp), 
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center',
                           fontsize=9,
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
        
        plt.show()
    
    @staticmethod
    def bar_chart(data, country, label):
        """Create a bar chart showing temperatures."""
        if len(data) < 2:
            print("⚠️  Need at least 2 data points for bar chart")
            return
        
        TemperatureCharts.setup_plot_style()
        
        # Prepare data
        df = data.copy()
        df['date'] = pd.to_datetime(df['last_updated'])
        df['temp'] = df['temperature_celsius'].astype(float)
        df = df.sort_values('date')
        
        # Create date labels (show month-day or just day)
        if len(df) <= 20:
            df['date_label'] = df['date'].dt.strftime('%m-%d')
        else:
            df['date_label'] = df['date'].dt.strftime('%d')
        
        # Create the plot
        plt.figure(figsize=(14, 7))
        
        # Create color map based on temperature
        colors = plt.cm.RdYlBu_r((df['temp'] - df['temp'].min()) / (df['temp'].max() - df['temp'].min()))
        
        bars = plt.bar(df['date_label'], df['temp'], color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Customize the plot
        plt.title(f'🌡️ Temperature Distribution for {country} ({label})', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12, fontweight='bold')
        plt.ylabel('Temperature (°C)', fontsize=12, fontweight='bold')
        
        # Add value labels on bars
        for bar, temp in zip(bars, df['temp']):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{temp:.1f}°C', ha='center', va='bottom', fontsize=9)
        
        # Rotate x-axis labels if too many dates
        if len(df) > 10:
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def histogram(data, country, label):
        """Create a histogram showing temperature distribution."""
        if len(data) < 5:
            print("⚠️  Need at least 5 data points for histogram")
            return
        
        TemperatureCharts.setup_plot_style()
        
        # Prepare data
        temps = data['temperature_celsius'].astype(float)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        # Create histogram with seaborn for better styling
        sns.histplot(temps, bins=min(15, len(temps)//2), 
                    kde=True, color='#2E86AB', alpha=0.7, edgecolor='black')
        
        # Add mean line
        mean_temp = temps.mean()
        plt.axvline(mean_temp, color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_temp:.1f}°C')
        
        # Customize the plot
        plt.title(f'📊 Temperature Distribution for {country} ({label})', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Temperature (°C)', fontsize=12, fontweight='bold')
        plt.ylabel('Frequency', fontsize=12, fontweight='bold')
        plt.legend()
        
        # Add statistics text
        stats_text = f'Count: {len(temps)}\nMean: {mean_temp:.1f}°C\nStd: {temps.std():.1f}°C\nMin: {temps.min():.1f}°C\nMax: {temps.max():.1f}°C'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def box_plot(data, country, label):
        """Create a box plot showing temperature distribution."""
        if len(data) < 5:
            print("⚠️  Need at least 5 data points for box plot")
            return
        
        TemperatureCharts.setup_plot_style()
        
        # Prepare data
        df = data.copy()
        df['temp'] = df['temperature_celsius'].astype(float)
        
        # Create the plot
        plt.figure(figsize=(8, 6))
        
        # Create box plot
        box = plt.boxplot(df['temp'], patch_artist=True, labels=[country])
        box['boxes'][0].set_facecolor('#2E86AB')
        box['boxes'][0].set_alpha(0.7)
        
        # Add individual points
        y = df['temp']
        x = np.random.normal(1, 0.04, size=len(y))  # Add some jitter
        plt.scatter(x, y, alpha=0.6, color='red', s=20)
        
        # Customize the plot
        plt.title(f'📦 Temperature Distribution (Box Plot) for {country} ({label})', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.ylabel('Temperature (°C)', fontsize=12, fontweight='bold')
        
        # Add statistics
        stats = df['temp'].describe()
        stats_text = f'Q1: {stats["25%"]:.1f}°C\nMedian: {stats["50%"]:.1f}°C\nQ3: {stats["75%"]:.1f}°C'
        plt.text(1.1, stats["75%"], stats_text, fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def heatmap_calendar(data, country, label):
        """Create a calendar heatmap showing temperatures."""
        if len(data) < 10:
            print("⚠️  Need at least 10 data points for calendar heatmap")
            return
        
        TemperatureCharts.setup_plot_style()
        
        # Prepare data
        df = data.copy()
        df['date'] = pd.to_datetime(df['last_updated'])
        df['temp'] = df['temperature_celsius'].astype(float)
        
        # Create month-day combinations
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        
        # Create pivot table for heatmap
        if len(df['month'].unique()) > 1:
            heatmap_data = df.pivot_table(values='temp', index='day', columns='month', aggfunc='mean')
        else:
            # If only one month, create a different view
            df['week'] = df['date'].dt.isocalendar().week
            heatmap_data = df.pivot_table(values='temp', index='day', columns='week', aggfunc='mean')
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Create heatmap
        sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlBu_r', 
                   cbar_kws={'label': 'Temperature (°C)'}, 
                   linewidths=0.5, linecolor='white')
        
        # Customize the plot
        plt.title(f'🗓️ Temperature Calendar Heatmap for {country} ({label})', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Month' if len(df['month'].unique()) > 1 else 'Week', fontsize=12, fontweight='bold')
        plt.ylabel('Day', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def display_charts(data, country, label):
        """Display multiple chart options and let user choose."""
        data_size = len(data)
        
        if data_size < 2:
            print(f"\n⚠️  Need at least 2 data points to create charts (have {data_size})")
            return
        
        print(f"\n🎨 Available Charts for {country} ({label}):")
        print("=" * 50)
        print("1. 📈 Line Chart (Temperature Trend)")
        print("2. 📊 Bar Chart (Temperature by Date)")
        
        if data_size >= 5:
            print("3. 📊 Histogram (Temperature Distribution)")
            print("4. 📦 Box Plot (Statistical Summary)")
        
        if data_size >= 10:
            print("5. 🗓️ Calendar Heatmap")
        
        print("6. 🎯 Show All Available Charts")
        print("0. ⬅️ Skip Charts")
        
        try:
            choice = input("\nSelect chart type (0-6): ").strip()
            
            if choice == '1':
                TemperatureCharts.line_chart(data, country, label)
            elif choice == '2':
                TemperatureCharts.bar_chart(data, country, label)
            elif choice == '3' and data_size >= 5:
                TemperatureCharts.histogram(data, country, label)
            elif choice == '4' and data_size >= 5:
                TemperatureCharts.box_plot(data, country, label)
            elif choice == '5' and data_size >= 10:
                TemperatureCharts.heatmap_calendar(data, country, label)
            elif choice == '6':
                print("\n🎯 Generating all available charts...")
                TemperatureCharts.line_chart(data, country, label)
                TemperatureCharts.bar_chart(data, country, label)
                if data_size >= 5:
                    TemperatureCharts.histogram(data, country, label)
                    TemperatureCharts.box_plot(data, country, label)
                if data_size >= 10:
                    TemperatureCharts.heatmap_calendar(data, country, label)
            elif choice == '0':
                print("Skipping charts...")
            else:
                print("Invalid choice or insufficient data for selected chart type.")
                
        except Exception as e:
            print(f"Error creating chart: {e}")
            print("Make sure you have matplotlib and seaborn installed:")
            print("pip install matplotlib seaborn")


# Standalone demo function
def demo_charts():
    """Demo function to test the charts with sample data."""
    # Sample data
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    temps = [15 + 10 * np.sin(i/3) + np.random.normal(0, 2) for i in range(20)]
    
    sample_data = pd.DataFrame({
        'last_updated': dates.strftime('%Y-%m-%d'),
        'temperature_celsius': temps
    })
    
    print("🌡️  Temperature Charts Demo")
    TemperatureCharts.display_charts(sample_data, "Sample Country", "January 2024")


if __name__ == "__main__":
    demo_charts()
