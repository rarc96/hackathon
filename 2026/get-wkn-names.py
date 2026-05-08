import csv

def get_marketing_name(wkn):

    filename="Datenbank.csv"
    
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["WKN"] == wkn:
                return row["MarketingName"]
    return None  # If the WKN was not found

def main():
    wkn = input("Enter WKN: ").strip()
    result = get_marketing_name(wkn)
    if result:
        print(f"MarketingName for WKN {wkn}: {result}")
    else:
        print(f"WKN {wkn} not found in products.csv")

if __name__ == "__main__":
    main()
# Example Usage:
# print(get_marketing_name("BASF11"))  # Output: BASF AG
