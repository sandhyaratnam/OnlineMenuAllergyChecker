from bs4 import BeautifulSoup
import nltk
from nltk.stem import WordNetLemmatizer
import ssl
import requests
import pymupdf
import tempfile
import pdfkit


ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

#TODO use s3
def determine_file_type_pdf(url, restaurant_name):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type')
            if 'application/pdf' in content_type:
                with open('input_menus/'+restaurant_name+'.pdf', 'wb') as file:
                    file.write(response.content)
                return True
            else:
            #     temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=restaurant_name+'.pdf').name
            #     pdfkit.from_url(url, temp_pdf_path)
                return False
    
    except Exception as e:
        return f"Error : {e}"
      

def normalize_allergens(allergens):
    normalized = set()
    for allergen in allergens:
        allergen_lower = allergen.lower()
        lemmatized = lemmatizer.lemmatize(allergen_lower)
        normalized.add(lemmatized)

        # Add singular and plural forms
        if lemmatized.endswith('s'):
            normalized.add(lemmatized[:-1]) 
        else:
            normalized.add(lemmatized + 's') 

    return normalized

"""Highlight allergens in the PDF and save it as a new file."""
def highlight_menu_items_with_allergens(input_pdf_path, allergens, output_pdf_path):
    allergens = normalize_allergens(allergens)
    doc = pymupdf.open("input_menus/"+input_pdf_path)

    for page in doc:
        for allergen in allergens:
            # Search for the allergen in the page text
            text_instances = page.search_for(allergen)
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=(1, 1, 0))  # highlight color (yellow)
                highlight.update()

    doc.save("output_menus/"+output_pdf_path)
    doc.close()


def main():
    #TODO multiple word allergen
    allergens_input = input("Enter your allergies (comma-separated, e.g., peanuts,gluten): ")
    allergens = [allergy.strip().lower() for allergy in allergens_input.split(",")]

    restaurant_name = input("Enter the restaurant name: ").strip().lower()
    menu_url = input("Enter the restaurant menu pdf URL: ").strip()
    
    if determine_file_type_pdf(menu_url, restaurant_name):
        highlight_menu_items_with_allergens(restaurant_name+'.pdf', allergens, restaurant_name+'_output.pdf')
        print("Successfully created pdf!")
        

if __name__ == "__main__":
    main()