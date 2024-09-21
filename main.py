from bs4 import BeautifulSoup
import requests
import re

def get_webpage_data(menu_url):
    # Making a GET request
    r = requests.get(menu_url)

    # check status code for response received
    # success code - 200
    print(r)

    # print content of request
    print(r.content)
    return r.content

def extract_menu_items(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Assuming menu items are wrapped in divs or lists with class 'menu-item'
    # Update selectors based on actual website HTML structure
    menu_items = soup.select(".menu-item")
    
    items = []
    
    for item in menu_items:
        name = item.select_one(".item-name")  # Modify based on actual HTML
        description = item.select_one(".item-desc")  # Modify based on actual HTML
        items.append((name, description))

    print("items: ", items)
    
    return items

def check_allergens(menu_items, allergens):
    unsafe_items = []
    
    for name, description in menu_items:
        found_allergens = []
        
        # Check if any of the allergens are in the item description
        for allergy in allergens:
            if re.search(rf'\b{allergy}\b', description, re.IGNORECASE):
                found_allergens.append(allergy)
        
        if found_allergens:
            unsafe_items.append((name, description, found_allergens))
    
    return unsafe_items

def get_menu(web_data, allergens):
    if web_data:
        # Extract the menu items from the HTML content
        menu_items = extract_menu_items(web_data)
        
        if menu_items:
            # Check the menu items for allergens
            unsafe_items = check_allergens(menu_items, allergens)
            
            # Display results
            if unsafe_items:
                print("\nWarning! The following menu items contain allergens:\n")
                for name, description, found_allergens in unsafe_items:
                    print(f"Menu Item: {name}")
                    print(f"Description: {description}")
                    print(f"Contains allergens: {', '.join(found_allergens)}")
                    print("-" * 40)
            else:
                print("Good news! No menu items contain your allergens.")
        else:
            print("No menu items found on the page. Please check the HTML structure or URL.")
    else:
        print("Failed to retrieve the menu.")

def main():
    # Input: User's allergens (comma-separated)
    allergens_input = input("Enter your allergies (comma-separated, e.g., peanuts,gluten): ")
    allergens = [allergy.strip().lower() for allergy in allergens_input.split(",")]

    # Input: Restaurant menu URL
    menu_url = input("Enter the restaurant menu URL: ")
    web_data = get_webpage_data(menu_url)

    print("web_data: ", web_data)

    get_menu(web_data, allergens)

if __name__ == "__main__":
    main()