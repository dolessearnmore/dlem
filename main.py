import mt5_helper


def main():
    """
    Main function that loads environment variables, initializes MT5, retrieves data,
    and saves it to a CSV file.
    """

    # Load mt5
    mt5_helper.init_mt5()

    #Interactive fetch data
    mt5_helper.user_interactive_data_fetch()

if __name__ == "__main__":
    main()