# crop_doctor/tools.py

import os
import base64
import requests
from dotenv import load_dotenv
from apify_client import ApifyClient
from urllib.parse import quote_plus

def get_plant_health_assessment(image_path: str):
    """
    Takes a local image path, sends it to the Plant.id Health Assessment API,
    and returns a structured dictionary with diagnosis and treatment suggestions.

    Args:
        image_path (str): The local file path to the plant image.

    Returns:
        dict: A dictionary containing the parsed health assessment results
    """
    # 1. Load API Key from .env file
    load_dotenv()
    api_key = os.getenv("PLANT_API_KEY")
    if not api_key:
        return {
            "error": "PLANT_API_KEY not found in .env file",
            "is_healthy": None,
            "health_probability": 0,
            "disease_suggestions": []
        }

    # 2. Check if image file exists
    if not os.path.exists(image_path):
        return {
            "error": f"Image file not found at {image_path}",
            "is_healthy": None,
            "health_probability": 0,
            "disease_suggestions": []
        }

    # 3. Convert image to Base64 string
    try:
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        return {
            "error": f"Failed to read image: {str(e)}",
            "is_healthy": None,
            "health_probability": 0,
            "disease_suggestions": []
        }
    
    # 4. Define API endpoint and headers
    url = "https://plant.id/api/v3/health_assessment?details=local_name,description,url,treatment,classification,common_names,cause"
    
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    # 5. Prepare the payload for the POST request
    payload = {
        "images": [img_base64]
    }

    # 6. Send the request and handle potential errors
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {
            "error": f"API request failed: {str(e)}",
            "is_healthy": None,
            "health_probability": 0,
            "disease_suggestions": []
        }

    # 7. Parse the JSON response into a structured format
    try:
        data = response.json()
        structured_result = {
            "is_healthy": data.get("result", {}).get("is_healthy", {}).get("binary"),
            "health_probability": data.get("result", {}).get("is_healthy", {}).get("probability", 0),
            "disease_suggestions": []
        }

        if "result" in data and "disease" in data["result"]:
            suggestions = data["result"]["disease"].get("suggestions", [])
            for disease in suggestions:
                details = disease.get("details", {})
                treatment = details.get("treatment", {})
                
                structured_suggestion = {
                    "name": disease.get("name", "Unknown Disease"),
                    "probability": disease.get("probability", 0),
                    "description": details.get("description", "No description available"),
                    "cause": details.get("cause", "Unknown cause"),
                    "treatment": {
                        "prevention": treatment.get("prevention", []),
                        "biological": treatment.get("biological", []),
                        "chemical": treatment.get("chemical", [])
                    }
                }
                structured_result["disease_suggestions"].append(structured_suggestion)
        
        return structured_result
    
    except Exception as e:
        return {
            "error": f"Failed to parse API response: {str(e)}",
            "is_healthy": None,
            "health_probability": 0,
            "disease_suggestions": []
        }


def scrape_indiamart_for_remedies(remedy_queries: list):
    """
    Takes a list of remedy names, scrapes Indiamart for each using the specified
    Apify actor, and returns structured product information.

    Args:
        remedy_queries (list): A list of remedies to search for.

    Returns:
        dict: A dictionary where keys are the remedy queries and values are lists
              of scraped product data.
    """
    # Initialize result structure
    scraped_data = {}
    for query in remedy_queries:
        scraped_data[query] = []
    
    # 1. Load Apify Token and Actor ID from .env file
    load_dotenv()
    apify_token = os.getenv("APIFY_TOKEN")
    indiamart_actor_id = os.getenv("APIFY_INDIAMART_ACTOR")

    if not apify_token or not indiamart_actor_id:
        return {
            "error": "APIFY_TOKEN or APIFY_INDIAMART_ACTOR not found in .env file",
            **scraped_data
        }

    # 2. Initialize ApifyClient
    try:
        client = ApifyClient(apify_token)
    except Exception as e:
        return {
            "error": f"Failed to initialize Apify client: {str(e)}",
            **scraped_data
        }

    # 3. Construct search URLs
    start_urls = []
    for query in remedy_queries:
        encoded_query = quote_plus(query)
        url = f"https://dir.indiamart.com/search.mp?ss={encoded_query}"
        start_urls.append({"url": url})

    # 4. Prepare actor input
    actor_input = {
        "startUrls": start_urls,
        "maxItems": 10,
        "country": "IN"
    }

    print(f"Starting Apify Indiamart scraper for: {remedy_queries}...")

    # 5. Run the actor and fetch results
    try:
        actor_run = client.actor(indiamart_actor_id).call(run_input=actor_input)
        dataset_items = client.dataset(actor_run["defaultDatasetId"]).list_items().items

        # 6. Process and structure the results
        for item in dataset_items:
            matched_query = None
            
            # Enhanced query matching
            item_url = item.get("url", "").lower()
            item_title = item.get("title", "").lower()
            item_description = item.get("description", "").lower()
            
            for query in remedy_queries:
                query_lower = query.lower()
                encoded_query = quote_plus(query).lower()
                query_words = [word for word in query_lower.split() if len(word) > 2]
                
                if (encoded_query in item_url or 
                    any(word in item_title for word in query_words) or
                    any(word in f"{item_url} {item_description}" for word in query_words)):
                    matched_query = query
                    break

            if matched_query:
                # Extract price information
                price_data = None
                price_fields = ['price', 'Price', 'priceRange', 'pricePerUnit', 'cost', 'amount', 'pricing', 'unitPrice']
                
                for price_field in price_fields:
                    if price_field in item and item[price_field]:
                        price_data = item[price_field]
                        break
                
                if not price_data:
                    price_data = 'Price not available'
                
                # Get seller information
                seller_info = (
                    item.get("sellerName") or 
                    item.get("seller") or 
                    item.get("company") or 
                    item.get("companyName") or
                    "Unknown Seller"
                )
                
                product_info = {
                    "product_name": item.get("title", "Unknown Product"),
                    "price": price_data,
                    "seller": seller_info,
                    "url": item.get("url", ""),
                    "description": item.get("description", "")[:200] if item.get("description") else ""
                }
                
                scraped_data[matched_query].append(product_info)

        # Log results
        total_items = sum(len(items) for items in scraped_data.values())
        items_with_prices = sum(
            1 for items in scraped_data.values() 
            for item in items 
            if item.get('price') and item['price'] not in ['Price not available', None, '', 'NO_PRICE']
        )
        
        print(f"Total items found: {total_items}")
        print(f"Items with price data: {items_with_prices}")
        
        return scraped_data

    except Exception as e:
        return {
            "error": f"Scraping failed: {str(e)}",
            **scraped_data
        }


def search_remedy_prices_google(remedy_name: str):
    """
    Perform web searches for agricultural remedy prices and suppliers in India.
    This function will trigger Gemini to search the web for pricing information.
    
    Args:
        remedy_name (str): The remedy to search for (e.g., "neem oil", "fungicide")
    
    Returns:
        str: Search query for Gemini to execute with web search
    """
    # Create comprehensive search query that Gemini will execute
    search_query = f"""
Search for the following information about '{remedy_name}' in India:

1. Current market prices for {remedy_name} in West Bengal
2. Online suppliers selling {remedy_name} with delivery to Kharagpur
3. Agricultural stores near West Bengal selling {remedy_name}
4. Wholesale/bulk pricing options for {remedy_name}

Focus on finding:
- Exact prices in Indian Rupees (₹)
- Supplier names and contact information
- Location of suppliers (prioritize West Bengal)
- Product specifications (quantity, concentration, etc.)
- Shipping/delivery information

Please search and provide structured results with:
- Product name
- Price (₹ per unit)
- Supplier/store name
- Location
- Contact details or website
- Any bulk discount information

Search terms to use:
- "{remedy_name} price West Bengal India"
- "buy {remedy_name} agricultural supplier India"
- "{remedy_name} wholesale price Kharagpur"
- "cheapest {remedy_name} online India"
"""
    
    print(f"Initiating web search for '{remedy_name}' pricing information...")
    return search_query


# Test function
if __name__ == "__main__":
    print("Testing Plant Health Assessment...")
    image_file = "download (1).jpg"
    if os.path.exists(image_file):
        assessment = get_plant_health_assessment(image_file)
        if "error" in assessment:
            print(f"Error: {assessment['error']}")
        else:
            print(f"Plant is healthy: {assessment.get('is_healthy')}")
            print(f"Found {len(assessment.get('disease_suggestions', []))} disease suggestions")
    else:
        print(f"Test image '{image_file}' not found")
    
    print("\nTesting IndiaMART Scraper...")
    remedies = ["neem oil", "fungicide"]
    results = scrape_indiamart_for_remedies(remedies)
    if "error" in results:
        print(f"Error: {results['error']}")
    else:
        total_items = sum(len(items) for items in results.values() if isinstance(items, list))
        print(f"Found {total_items} total items")
        for query, items in results.items():
            if isinstance(items, list):
                print(f"   {query}: {len(items)} items")
                
    print("\nTesting Google Search...")
    search_result = search_remedy_prices_google("neem oil")
    print("Search query generated successfully")