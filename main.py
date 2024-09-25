from bs4 import BeautifulSoup
import re
import pdfkit
import pdfplumber
import nltk
from nltk.stem import WordNetLemmatizer
import ssl
import requests

ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

def determine_file_type_pdf(url, restaurant_name):
    try:
        # Send a HEAD request to get the headers without downloading the content
        response = requests.get(url)
        if response.status_code == 200:
            # Check if the content type is 'application/pdf'
            content_type = response.headers.get('Content-Type')
            if 'application/pdf' in content_type:
                with open(restaurant_name+'.pdf', 'wb') as file:
                    # Write the PDF content to the file
                    file.write(response.content)
                return True
            else:
                return False
    
    except requests.RequestException as e:
        return f"Error accessing URL: {e}"
      

def extract_allergens_from_pdf(pdf_path, allergens):
    # Lemmatize the allergens and words
    allergens = normalize_allergens(allergens)
    unsafe_items = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Split into lines and parse menu items
                lines = text.split('\n')
                for line in lines:
                    # Clean up line, strip leading/trailing whitespace
                    line = line.strip()
                    if line:  # Only process non-empty lines
                        combined_text = line.lower()
                        found_allergens = []
                        for allergen in allergens:
                            # Check for presence of allergen
                            if re.search(r'\b' + re.escape(allergen) + r'\b', combined_text):
                                found_allergens.append(allergen)
                        
                        if found_allergens:
                            unsafe_items.append((line, found_allergens))

    return unsafe_items

def normalize_allergens(allergens):
    normalized = set()
    for allergen in allergens:
        # Normalize the allergen to lowercase
        allergen_lower = allergen.lower()
        lemmatized = lemmatizer.lemmatize(allergen_lower)
        normalized.add(lemmatized)  # Add the base form

        # Add singular and plural forms explicitly
        if lemmatized.endswith('s'):
            normalized.add(lemmatized[:-1])  # Add singular form (e.g., "almond" from "almonds")
        else:
            normalized.add(lemmatized + 's')  # Add plural form (e.g., "almonds" from "almond")

    return normalized

def get_menu(unsafe_items):
    # Extract the menu items from the pdf content        
    if unsafe_items:
        # Display results
            print("\nWarning! The following menu items contain allergens:\n")
            for name, allergen in unsafe_items:
                print('---')
                print(f"Menu Item: {name}")
                print(f"Allergen: {allergen}")
                print('---')

    else:
        print("Good news! No menu items contain your allergens.")



def main():
    # Input: User's allergens (comma-separated)
    allergens_input = input("Enter your allergies (comma-separated, e.g., peanuts,gluten): ")
    allergens = [allergy.strip().lower() for allergy in allergens_input.split(",")]

    restaurant_name = input("Enter the restaurant name: ").strip().lower()
    menu_url = input("Enter the restaurant menu pdf URL: ").strip()
    if determine_file_type_pdf(menu_url,restaurant_name):
        # web_data = get_webpage_data(menu_url)
        allergic_menu_items = extract_allergens_from_pdf(restaurant_name+'.pdf',allergens)
        get_menu(allergic_menu_items)
    else:
        print("Not valid pdf")

if __name__ == "__main__":
    main()