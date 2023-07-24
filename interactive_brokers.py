import requests
from bs4 import BeautifulSoup

def fetch_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any HTTP errors
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def fetch_IBKR_data_and_write_to_csv(IBKR_user_token, IBKR_user_query):
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
                file_path = "orders.csv"
                with open(file_path, 'wb') as file:
                    file.write(IBKR_user_orders)
            else:
                print("Error fetching user orders.")
        else:
            print("Error fetching IBKR code.")
    else:
        print("Error fetching IBKR data.")
    
    return None
