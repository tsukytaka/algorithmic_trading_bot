import json
import os

import pandas

import time

# import backtest_lib
import display_lib
import indicator_lib
import mt5_lib
# from strategies import macd_crossover_strategy
import ema_cross_strategy

# Location of settings.json
settings_filepath = "settings.json" # <- This can be modified to be your own settings filepath


# Function to import settings from settings.json
def get_project_settings(import_filepath):
    """
    Function to import settings from settings.json
    :param import_filepath: path to settings.json
    :return: settings as a dictionary object
    """
    # Test the filepath to make sure it exists
    if os.path.exists(import_filepath):
        # If yes, import the file
        f = open(import_filepath, "r")
        # Read the information
        project_settings = json.load(f)
        # Close the file
        f.close()
        # Return the project settings
        return project_settings
    # Notify user if settings.json doesn't exist
    else:
        raise ImportError("settings.json does not exist at provided location")


# Function to start up MT5
def mt5_startup(project_settings):
    """
    Function to run through the process of starting up MT5 and initializing symbols
    :param project_settings: json object of project settings
    :return: Boolean. True. Startup successful. False. Error in starting up.
    """
    # Attempt to start MT5
    start_up = mt5_lib.start_mt5(project_settings=project_settings)
    # If starting up successful, proceed to confirm that the symbols are initialized
    if start_up:
        init_symbols = mt5_lib.enable_all_symbols(symbol_array=project_settings["mt5"]["symbols"])
        if init_symbols:
            return True
        else:
            print(f"Error intializing symbols")
            return False
    else:
        print(f"Error starting MT5")
        return False


# Main function
if __name__ == '__main__':
    print("Let's build an awesome trading bot!!!")
    # Import settings.json
    project_settings = get_project_settings(import_filepath=settings_filepath)
    # Start MT5
    mt5_start = mt5_startup(project_settings=project_settings)
    # pandas.set_option('display.max_columns', None)
    comment = "ema_cross_strategy"
    # Start a Performance timer
    perf_start = time.perf_counter()
    # Try making a trade
    symbol_for_strategy = project_settings['mt5']['symbols'][0]
    print("symbol_for_strategy: ", symbol_for_strategy)
    # Set up a previous time variable
    previous_time = 0
    # Set up a current time variable
    current_time = 0
    # Start a while loop to poll MT5
    while True:
        # Retrieve the current candle data
        candle_data = mt5_lib.query_historic_data(symbol=symbol_for_strategy,timeframe=project_settings['mt5']['timeframe'], number_of_candles=1)
        # Extract the timedata
        current_time = candle_data.iloc[0]['time']
        # Compare against previous time
        if current_time != previous_time:
            # Notify user
            print("New Candle")
            # Update previous time
            previous_time = current_time
            # Retrieve previous orders
            orders = mt5_lib.get_all_open_orders()
            # Start strategy one on selected symbol
            trade_outcome = ema_cross_strategy.ema_cross_strategy(symbol=symbol_for_strategy, timeframe=project_settings['mt5']['timeframe'],
                                  ema_one=50, ema_two=200)
            
            # Cancel orders
            if trade_outcome:
                for order in orders:
                    mt5_lib.cancel_order(order)
        # else:
        #     # Get positions
        #     positions = mt5_interface.get_open_positions()
        #     # Pass positions to update_trailing_stop
        #     for position in positions:
        #         ema_cross_strategy.update_trailing_stop(order=position, trailing_stop_pips=10,
        #                                       pip_size=project_settings['pip_size'])
        time.sleep(0.1)





