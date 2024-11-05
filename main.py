import mt5_helper
import economics_index_craw as ec
import time
def main():
    """
    Main function that loads environment variables, initializes MT5, retrieves data,
    and saves it to a CSV file.
    """

    # Load mt5
    mt5_helper.init_mt5()

    #Interactive fetch stock data
    mt5_helper.user_interactive_data_fetch()

    #Fetch Economics data
    print("* Prepare the economics data *")
    time.sleep(1)
    ec.fetch_multiple_indicators()
if __name__ == "__main__":
    main()