import json
import random
import re
import time 
import os # Keep os import, although unused in this version, for standard utility

# --- CONFIGURATION ---

# Recommended Daily Intake (RDI) for an average adult
RECOMMENDED_DAILY_INTAKE = {
    "CALORIES": 2000,   # kcal
    "PROTEIN": 50,      # g
    "FAT": 60,          # g
    "CARBS": 275,       # g
    "SODIUM": 2300      # mg
}

# The file where your daily goal progress was previously saved (now unused)
# GOALS_FILE = "daily_goals_state.json" 

# --- MOCK DATA GENERATOR (No API Key or Internet Needed) ---
class MockDataGenerator:
    """
    Generates realistic, randomized nutritional data for any food query 
    using only standard Python libraries. This ensures the application runs 
    without external dependencies or API keys.
    """
    def __init__(self):
        # Define realistic ranges for different food categories (per 100g)
        self.macros_ranges = {
            "meat": {"calories": (150, 300), "protein": (20, 35), "fat": (5, 25), "carbs": (0, 5), "sodium": (50, 600)},
            "grain": {"calories": (100, 150), "protein": (3, 10), "fat": (0, 3), "carbs": (20, 35), "sodium": (10, 200)},
            "vegetable": {"calories": (20, 70), "protein": (1, 5), "fat": (0, 1), "carbs": (5, 15), "sodium": (10, 50)},
            "junk": {"calories": (300, 500), "protein": (5, 15), "fat": (25, 40), "carbs": (30, 60), "sodium": (500, 1500)},
            "default": {"calories": (100, 250), "protein": (10, 20), "fat": (5, 15), "carbs": (10, 25), "sodium": (100, 400)},
        }
        self.common_availability = ["Local Market", "Online Grocer", "Specialty Store"]

    def _determine_category(self, query):
        """Simple keyword matching to categorize food for realistic data."""
        query = query.lower()
        if any(w in query for w in ["chicken", "beef", "pork", "fish", "salmon", "tofu", "egg"]):
            return "meat"
        if any(w in query for w in ["rice", "bread", "pasta", "quinoa", "oat", "potato"]):
            return "grain"
        if any(w in query for w in ["broccoli", "carrot", "salad", "spinach", "asparagus"]):
            return "vegetable"
        if any(w in query for w in ["burger", "pizza", "fries", "soda", "cake", "cookie"]):
            return "junk"
        return "default"

    def generate_data(self, query):
        """Generates mock nutritional data for the given query (per 100g)."""
        category = self._determine_category(query)
        ranges = self.macros_ranges[category]
        
        # Simulate network delay for realism
        time.sleep(random.uniform(0.1, 0.5))

        # Generate Macros
        calories = random.randint(*ranges["calories"])
        protein = round(random.uniform(*ranges["protein"]), 1)
        fat = round(random.uniform(*ranges["fat"]), 1)
        carbs = round(random.uniform(*ranges["carbs"]), 1)
        sodium = random.randint(*ranges["sodium"])
        
        # Generate Micros (Randomly based on category)
        micros = {
            "Sodium": sodium,
            "Iron": round(random.uniform(0.1, 5.0) * (2 if category == 'meat' else 1), 1),
            "Vitamin C": round(random.uniform(0.5, 50.0) * (2 if category == 'vegetable' else 1), 1),
            "Calcium": round(random.uniform(10, 200), 0)
        }

        # Generate Mock Ingredients
        ingredients_map = {
            "meat": ["Lean protein", "Water", "Salt", "Seasoning blend"],
            "grain": ["Whole grain", "Water", "Fiber", "Trace minerals"],
            "vegetable": ["Water", "Fiber", "Vitamins", "Phytonutrients"],
            "junk": ["Refined Flour", "High Fructose Corn Syrup", "Hydrogenated Oils", "Artificial Flavors"],
            "default": ["Primary Food Source", "Water", "Salt"],
        }
        ingredients = random.sample(ingredients_map[category], k=len(ingredients_map[category]))
        
        # Structure the final data
        structured_data = {
            "query": query,
            "per_serving_size": "100g",
            "macros": {"calories": calories, "protein": protein, "carbs": carbs, "fat": fat},
            "micros": micros,
            "ingredients": ingredients,
            "availability": random.sample(self.common_availability, k=2),
            "sources": ["Simulated Data Source (Local)"]
        }
        return structured_data

# --- CORE ANALYZER APPLICATION (Analysis Code) ---

class FoodAnalyzer:
    """
    Handles user interaction, RDI calculations, and consumption advice generation.
    """
    def __init__(self):
        self.api = MockDataGenerator()
        self.rdi = RECOMMENDED_DAILY_INTAKE
        self.all_meal_data = {}

    def _generate_advice(self, total_macros: dict) -> tuple[str, bool]:
        """Provides consumption advice based on RDI and nutrient profile."""
        advice_parts = []
        is_healthy = True
        
        # 1. Calories Check (Assuming this is one significant meal, ~35% of RDI)
        if total_macros['Calories'] > (self.rdi['CALORIES'] * 0.35):
            advice_parts.append("This is a high-calorie meal; consider reducing portion size.")
            is_healthy = False
        
        # 2. Fat Check (High Fat)
        if total_macros['Fat'] > 30:
            advice_parts.append("High in total fat. Try to balance this with low-fat meals later today.")
            is_healthy = False
        
        # 3. Sodium Check (Above 25% of RDI for the day)
        if self.rdi.get('SODIUM') and total_macros.get('Sodium', 0) > (self.rdi['SODIUM'] * 0.25):
            advice_parts.append(f"Warning: High Sodium content ({total_macros['Sodium']:.0f}mg). Look for low-sodium alternatives next time.")
            is_healthy = False
            
        if total_macros['Protein'] > 30:
            advice_parts.insert(0, "Excellent source of protein, essential for muscle repair.")

        if not advice_parts:
            advice_parts.append("A nutritionally balanced choice. Fits well into a healthy diet.")
            
        final_advice = f"CONSIDER CONSUMING: {'Yes' if is_healthy else 'No - Caution'}\n"
        final_advice += "--- Reasons & Suggestions ---\n"
        final_advice += "\n".join([f"- {a}" for a in advice_parts])
        
        return final_advice, is_healthy

    def _print_report(self, meal_query: str, total_macros: dict, advice: str, is_healthy: bool):
        """Prints the final, comprehensive report."""
        
        header_style = "\n" + "="*80
        footer_style = "="*80 + "\n"
        health_rating = "🟢 HEALTHY CHOICE" if is_healthy else "🔴 CAUTION REQUIRED"
        
        print(header_style)
        print(f"| NUTRITION AND CHEMICAL COMPOSITION REPORT | Meal: {meal_query}")
        print(f"| Health Rating: {health_rating}")
        print(footer_style)
        
        # A. Total Meal Composition vs. RDI
        print("\n--- A. TOTAL MEAL COMPOSITION & DAILY GOAL COMPARISON ---")
        print(f"Note: Based on a general {self.rdi['CALORIES']} kcal RDI for an average adult.")
        print("-" * 50)
        
        print(f"{'Nutrient':<15} | {'Amount in Meal':<15} | {'RDI Goal':<10} | {'% of RDI':<10}")
        print("-" * 50)
        
        for name, goal in [("Calories", self.rdi["CALORIES"]), ("Protein", self.rdi["PROTEIN"]), 
                           ("Carbs", self.rdi["CARBS"]), ("Fat", self.rdi["FAT"])]:
            amount = total_macros.get(name, 0)
            unit = "kcal" if name == "Calories" else "g"
            
            percent = (amount / goal) * 100 if goal > 0 else 0
            
            print(f"{name:<15} | {amount:<15.1f} {unit:<3} | {goal:<10} {unit:<3} | {percent:<10.1f}%")

        # B. Consumption Advice
        print("\n--- B. CONSUMPTION ADVICE ---")
        print(advice)
        print("\n" + "*"*80)
        
        # C. Detailed Breakdown and Availability 
        print("\n--- C. DETAILED PRODUCT BREAKDOWN ---")
        
        for name, data in self.all_meal_data.items():
            print(f"\n>>>> Product: {name} (Per 100g) <<<<")
            
            # Macronutrient Display
            print(f"  > **MACRONUTRIENTS (Energy) **:")
            print(f"    - Calories: {data['macros']['calories']} kcal")
            print(f"    - Protein: {data['macros']['protein']:.1f} g")
            print(f"    - Carbohydrates: {data['macros']['carbs']:.1f} g")
            print(f"    - Total Fat: {data['macros']['fat']:.1f} g")
            print("    *These large molecules are broken down during digestion to provide energy.* [Image of the human digestive system] ")

            # Chemical Composition (Micronutrients)
            print(f"  > **CHEMICAL COMPOSITION (Micronutrients)**:")
            # Use LaTeX for scientific notation/formulas
            # Example of a key vitamin: Vitamin C ($C_6H_8O_6$)
            print(f"    - Vitamin C ($C_6H_8O_6$): {data['micros'].get('Vitamin C', 0):.1f} mg")
            
            # Example of a key mineral: Iron (Fe)
            print(f"    - Iron (Fe): {data['micros'].get('Iron', 0):.1f} mg")
            
            # Example of an electrolyte: Sodium (Na)
            print(f"    - Sodium (Na): {data['micros'].get('Sodium', 0):.1f} mg")
            print("    *Micronutrients are essential chemical components needed in small amounts.* [Image of chemical structure of Vitamin C] ")
                
            # Ingredient Analysis
            ingredients_str = ', '.join(data['ingredients'])
            if len(ingredients_str) > 100:
                ingredients_str = ingredients_str[:100] + "..."
            print(f"  > **INGREDIENTS**: {ingredients_str}")

            # Availability Check
            availability_str = ', '.join(data['availability']) if data['availability'] else 'Not found in mock data.'
            print(f"  > **AVAILABILITY**: {availability_str}")

            # Data Sources
            if data.get('sources'):
                 print(f"  > **DATA SOURCES**: {', '.join(data['sources'])}")

        print(footer_style)


    def analyze_and_report(self, meal_query: str):
        """
        Main driver function to process the meal, fetch data, and generate the report.
        """
        self.all_meal_data = {}
        
        # Split meal into components
        food_items = [item.strip() for item in re.split(r',\s*| and \s*', meal_query) if item.strip()]
        
        if not food_items:
            print("Please enter a valid meal containing at least one food item.")
            return

        print(f"\nAnalyzing meal components: {food_items}")
        
        # Initialize total accumulation
        total_macros = {"Calories": 0, "Protein": 0, "Carbs": 0, "Fat": 0, "Sodium": 0}
        
        for item in food_items:
            # Generate mock data instead of calling external API
            data = self.api.generate_data(item)
            
            if data:
                self.all_meal_data[item.title()] = data
                
                # Accumulate total macros (assuming 100g of each for the analysis)
                total_macros["Calories"] += data["macros"]["calories"]
                total_macros["Protein"] += data["macros"]["protein"]
                total_macros["Carbs"] += data["macros"]["carbs"]
                total_macros["Fat"] += data["macros"]["fat"]
                total_macros["Sodium"] += data["micros"].get("Sodium", 0)
                
            else:
                print(f"Data generation failed for item: {item}")

        if not self.all_meal_data:
            print("Could not analyze any food item.")
            return

        # Generate Consumption Advice and Report
        advice, is_healthy = self._generate_advice(total_macros)
        self._print_report(meal_query.title(), total_macros, advice, is_healthy)


# --- EXECUTION BLOCK ---

def main():
    """Application entry point."""
    print("Welcome to the Nutritional & Chemical Composition Analyzer (Self-Contained).")
    print("This version uses internal mock data and requires NO API Key or Internet connection.")

    analyzer = FoodAnalyzer()

    # Example of a nutrient-poor meal to demonstrate the "Caution" advice
    default_meal = "cheeseburger, french fries, and soda"
    
    meal_query = input(f"\nEnter your meal components separated by commas (e.g., '{default_meal}'):\n> ")
    
    if not meal_query:
        meal_query = default_meal
        print(f"Using default meal: {default_meal}")

    # Start analysis
    analyzer.analyze_and_report(meal_query)


if __name__ == "__main__":
    print("\nStarting the Food Analyzer...")
    # NOTE: To run this file correctly, save it and execute it from your 
    # operating system's terminal (Command Prompt/Terminal) using:
    # python food_analyzer_standalone_v2.py
    try:
        main()
    except Exception as e:
        print(f"\nFATAL ERROR: The application failed to run: {e}")
