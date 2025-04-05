import openfoodfacts

# Example usage of the OpenFoodFacts API
def main():
    # Initialize the OpenFoodFacts API
    api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")

    # Search for a product by its barcode
    barcode = "0028400008617"  # Example barcode
    product = api.product.get(barcode)

    if product:
        print("Product found:")
        print(f"Name: {product.get('product_name', 'N/A')}")
        print(f"Brand: {product.get('brands', 'N/A')}")
        print(f"Categories: {product.get('categories', 'N/A')}")
        print(f"Ingredients: {product.get('ingredients_text', 'N/A')}")
        print(f"Packaging: {product.get('ecoscore_data', 'N/A').get('adjustments', 'N/A').get('packaging', 'N/A')}")
    else:
        print("Product not found.")

if __name__ == "__main__":
    main()