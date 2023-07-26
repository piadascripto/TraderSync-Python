import csv
import requests
from bs4 import BeautifulSoup

IBKR_user_token = "135962967293328323184330"
IBKR_user_query = "830297"

def fetch_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any HTTP errors
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def remove_duplicate_headers(input_file, output_file):
    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)

            # Flag to check if the header is already written to the output file
            header_written = False

            for row in reader:
                # Check if the row contains the header and it's not written already
                if "ClientAccountID" in row and not header_written:
                    writer.writerow(row)
                    header_written = True
                # Check if the row doesn't contain the header and write the data
                elif "ClientAccountID" not in row:
                    writer.writerow(row)

def fetch_IBKR_orders(IBKR_user_token, IBKR_user_query):
    url = f"https://www.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest?t={IBKR_user_token}&q={IBKR_user_query}&v=2"
    
    page_content = fetch_page_content(url)
    if page_content:
        soup = BeautifulSoup(page_content, "html.parser")
        IBKR_code = soup.find("code").text.strip() if soup.find("code") else None

        if IBKR_code:
            user_query_url = f"https://www.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement?q={IBKR_code}&t={IBKR_user_token}&v=2"
            
            IBKR_user_orders = fetch_page_content(user_query_url)
            if IBKR_user_orders:
                # Write the data to the CSV file
                raw_orders_file = "raw_orders.csv"
                with open(raw_orders_file, 'wb') as file:
                    file.write(IBKR_user_orders)
                
                # Clean the CSV file to remove duplicate headers
                orders_file = "orders.csv"
                remove_duplicate_headers(raw_orders_file, orders_file)
            else:
                print("Error fetching user orders.")
        else:
            print("Error fetching IBKR code.")
    else:
        print("Error fetching IBKR data.")
    
    return None


fetch_IBKR_orders(IBKR_user_token, IBKR_user_query)