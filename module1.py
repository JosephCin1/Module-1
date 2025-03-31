import requests
import pandas as pd
import time

class PennyStocker:
    def __init__(self):
        self.bank_account = 0
        self.calc_stock = {}
        self.stock_file = {}  # This is a dictionary to store date-ticker pairs
        self.api_key = 'dce4ee48b4c54257891f479601d2b63d'
        self.interval = '1day'
        self.end_date = '2025-01-01'
        self.stock_df = pd.DataFrame()  # Initialize an empty DataFrame to hold stock data

    def export_stocks(self, filename):
        with open(filename, "r") as file:
            for line in file:
                stocks = line.strip().split(", ")
                date = stocks[0]
                for i, ticker in enumerate(stocks[1:], start=1):
                    # Add ticker to the dictionary with the date as the key
                    self.stock_file.setdefault(date, []).append(ticker)

    def process_stocks(self):
        api_request_limit = 0  # Keep track of the API request limit
        spy_stocks = []  # List to store multiple instances of SPY stock information

        for i, (start_date, tickers) in enumerate(self.stock_file.items()):
            print(f"Date {i}: {start_date}")
            for j, ticker in enumerate(tickers):
                print(f"Stock {j} from {start_date}: {ticker}")
                api_url = f"https://api.twelvedata.com/time_series?symbol={ticker}&interval={self.interval}&start_date={start_date}&end_date={self.end_date}&apikey={self.api_key}"
                response = requests.get(api_url).json()

                if api_request_limit <= 7:
                    if 'values' in response:
                        data = pd.DataFrame(response['values'])  # Convert to DataFrame
                        data['datetime'] = pd.to_datetime(data['datetime'])  # Convert to datetime
                        data.set_index('datetime', inplace=True)  # Set datetime as the index

                        data['high'] = pd.to_numeric(data['high'])  # Convert 'high' to numeric
                        max_high_date = data['high'].idxmax()  # Date of max high
                        max_high_value = data.loc[max_high_date, 'high']  # Max high value

                        data['low'] = pd.to_numeric(data['low'])  # Convert 'low' to numeric
                        
                        # Filter for rows before the max high date
                        filtered_data = data.loc[data.index < max_high_date]
                        
                        non_nan_low_values = filtered_data['low'].dropna()

                        if not non_nan_low_values.empty:
                            min_low_date_before_max_high = non_nan_low_values.idxmin()  # Get the date of the min low value
                            min_low_value_before_max_high = filtered_data.loc[min_low_date_before_max_high, 'low']
                            
                            print(f"The stock {ticker} had the lowest low value of {min_low_value_before_max_high} on {min_low_date_before_max_high}, before the greatest high value on {max_high_date}")
                        else:
                            print(f"No valid low values found before the date {max_high_date} for stock {ticker}.")

                        print(f"The stock {ticker} had the greatest high value of {max_high_value} on {max_high_date}")
                        api_request_limit += 1


                        # Update calc_stock dictionary with stock information
                        self.calc_stock[ticker] = {
                            'stock':ticker,
                            'start_date': start_date,
                            'min_low_value': min_low_value_before_max_high,
                            'min_low_date': min_low_date_before_max_high,
                            'max_high_value': max_high_value,
                            'max_high_date': max_high_date
                        }
                        if ticker == "SPY":
                            start_value = data.loc[start_date, 'open'] if start_date in data.index else None
    
                            # End value on specific end date (from the 'close' column)
                            end_date = "2024-12-31"
                            end_value = data.loc[end_date, 'close'] if end_date in data.index else None
                            spy_stocks.append({
                            'stock':ticker,
                            'start_date': start_date,
                            'min_low_value': start_value,
                            'min_low_date': start_date,
                            'max_high_value': end_value,
                            'max_high_date': end_date
                        })
                            
                            
                    else:
                        # Print error message if the request failed
                        print(f"Error: {response.get('message', 'Failed to fetch data')}")
                        api_request_limit += 1

                        
                else:
                    print("Waiting for API token request limit ~60 seconds cooldown")
                    time.sleep(61)
                    print("Wait is over, rebooting")
                    api_request_limit = 0
    

        # Convert calc_stock to a DataFrame and store it as an CSV
        column_names = ["Ticker", "Researched_Date", "Lowest_Price", "Lowest_Date", "Highest Price", "Highest_Date"]

        self.stock_df = pd.DataFrame.from_dict(self.calc_stock, orient='index')
        # Append to the existing CSV
        self.stock_df.to_csv('stock.csv', mode='a', header=False, index=False)
        self.stock_df.columns = column_names

        if spy_stocks:
            spy_df = pd.DataFrame(spy_stocks)  # Convert SPY stock list to DataFrame
            spy_df.to_csv('stock.csv', mode='a', header=False, index=False)  # Append SPY stock instances to CSV
            spy_df.columns = column_names
        time.sleep(61)
        print(f"Resetting API for Next API Request function")

    def calculated_bank(self,stock_csv):
        #calculate the stocks and take pyplots
        df = pd.read_csv('stock.csv')

if __name__ == "__main__":
    penny_stocker = PennyStocker()  # Create an instance of PennyStocker
    filename = "rani.txt"  # Replace with the name of your file
    penny_stocker.export_stocks(filename)  # Call export_stocks method to load stock data
    penny_stocker.process_stocks()  # Call process_stocks method to process the stocks
    stock_csv="stock.csv"
