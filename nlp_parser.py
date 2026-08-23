import re

def parse_command(text):
    text = text.lower().strip()
    
    # Remove common punctuation at the end
    text = text.rstrip('.!?,')
    
    # Defaults
    result = {
        "action": "unknown",
        "item": "",
        "quantity": 1,
        "category": "General",
        "original_text": text
    }
    
    # 1. Check for Add
    add_prefixes = [
        "add ", "buy ", "i need ", "i want to buy ", "i want ",
        "can i get ", "get me ", "at ", "and ", "give me ",
        "can you get me ", "can you get ", "could you get me ", "could you get ",
        "could you buy ", "could you add ", "please get me ", "please get ",
        "please add ", "please buy ", "we need ", "we should get ",
        "we should buy ", "we should add ", "let's get ", "let's buy ",
        "let's add ", "can we get ", "can we buy ", "can we add ",
        "grab ", "pick up ", "put down ", "put ", "throw in ", "toss in ", "get "
    ]
    
    # If the text starts with a known prefix OR doesn't start with removing/finding keywords (catch-all for direct items)
    if any(text.startswith(p) for p in add_prefixes) or (not text.startswith("remove") and not text.startswith("delete") and not text.startswith("search") and not text.startswith("find")):
        result["action"] = "add"
        
        # Remove prefix
        for prefix in sorted(add_prefixes, key=len, reverse=True):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
                
        # Remove common articles
        for article in ["a ", "an ", "some ", "the "]:
            if text.startswith(article):
                text = text[len(article):].strip()
                break
                
        # Map written numbers to digits
        word_to_num = {
            "one": "1", "a couple ": "2 ", "two": "2", "three": "3", "four": "4", 
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
            "eleven": "11", "twelve": "12", "a dozen ": "12 ", "half a dozen ": "6 "
        }
        for word, num in word_to_num.items():
            if text.startswith(word + " "):
                text = num + " " + text[len(word)+1:]
                break
                
        # Try to extract quantity
        quantity_match = re.match(r"^(\d+)\s*(.*)", text)
        if quantity_match:
            try:
                result["quantity"] = int(quantity_match.group(1))
            except ValueError:
                pass
            item_text = quantity_match.group(2).strip()
            
            # Remove filler units for item name clean up
            item_text = re.sub(r"^(bottles of|packs of|boxes of|liters of|kgs of|kg of|grams of)\s+", "", item_text)
            result["item"] = item_text
        else:
            result["item"] = text.strip()
            
        # Strip conversational suffixes dynamically
        conversational_suffixes = [
            " to my list", " on my list", " to the list", " on the list", " in the list", " in my list", 
            " please", " urgently", " preferably", " right now", " today", " tomorrow", " asap", 
            " immediately", " as soon as possible", " for now", " eventually", " next time", " quickly"
        ]
        
        # Sort by length descending to match longest suffixes first (" as soon as possible" before " possible")
        for suffix in sorted(conversational_suffixes, key=len, reverse=True):
            if result["item"].endswith(suffix):
                result["item"] = result["item"][:-len(suffix)].strip()
                
        result["category"] = categorize_item(result["item"])
        return result
        
    # 2. Check for Remove
    if text.startswith("remove") or text.startswith("delete"):
        result["action"] = "remove"
        for prefix in ["remove ", "delete "]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        
        result["item"] = text.replace(" from my list", "").strip()
        return result
        
    # 3. Check for Search
    if text.startswith("find") or text.startswith("search"):
        result["action"] = "search"
        text = text.replace("find me ", "").replace("find ", "").replace("search for ", "").strip()
        
        # Check for price range
        price_match = re.search(r"under\s*\$?(\d+)(?:\s*dollars?)?", text)
        if price_match:
            result["price_limit"] = float(price_match.group(1))
            text = text[:price_match.start()].strip()
            
        result["item"] = text
        return result

    return result

def categorize_item(item):
    item = item.lower()
    if any(x in item for x in ["milk", "cheese", "butter", "yogurt"]):
        return "Dairy"
    if any(x in item for x in ["apple", "banana", "orange", "grape", "tomato", "potato", "onion", "carrot", "watermelon"]):
        return "Produce"
    if any(x in item for x in ["bread", "cake", "cookie", "chips", "biscuit"]):
        return "Bakery/Snacks"
    if any(x in item for x in ["beef", "chicken", "pork", "fish"]):
        return "Meat"
    if any(x in item for x in ["toothpaste", "soap", "shampoo"]):
        return "Personal Care"
    return "General"

def get_suggestions(history):
    suggestions = []
    historical_items = [h['name'].lower() for h in history]
    
    if "milk" in historical_items:
        suggestions.append({"type": "substitute", "text": "Want to try Almond Milk next time?", "item": "Almond milk"})
    
    if "bread" in historical_items and "butter" not in historical_items:
        suggestions.append({"type": "complement", "text": "You bought bread, do you need butter?", "item": "Butter"})
        
    # Always offer a seasonal mock for demonstration
    if "watermelon" not in historical_items:
        suggestions.append({"type": "seasonal", "text": "Watermelons are in season!", "item": "Watermelon"})
    
    return suggestions
