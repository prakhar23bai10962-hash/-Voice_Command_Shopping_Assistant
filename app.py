from flask import Flask, render_template, request, jsonify
from nlp_parser import parse_command, get_suggestions
import uuid

app = Flask(__name__)

# In-memory storage for simplicity (avoids setting up external DB, strictly per requirements)
shopping_list = []
shopping_history = [] 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process-command', methods=['POST'])
def process_command():
    data = request.json
    text = data.get('text', '')
    
    parsed = parse_command(text)
    action = parsed.get("action")
    
    response_msg = f"I didn't quite catch that. Try saying 'Add milk'. (Heard: '{text}')"
    items_updated = False
    
    if action == "add" and parsed["item"]:
        # Add to list
        new_item = {
            "id": str(uuid.uuid4()),
            "name": parsed["item"].capitalize(),
            "quantity": parsed["quantity"],
            "category": parsed["category"]
        }
        shopping_list.append(new_item)
        shopping_history.append(new_item)
        response_msg = f"Added {parsed['quantity']} {parsed['item']} to your list."
        items_updated = True
        
    elif action == "remove" and parsed["item"]:
        # Remove from list
        term = parsed["item"].lower()
        items_before = len(shopping_list)
        # using a simple exclusion on name match
        shopping_list[:] = [item for item in shopping_list if term not in item['name'].lower()]
        
        if len(shopping_list) < items_before:
            response_msg = f"Removed {parsed['item']} from your list."
            items_updated = True
        else:
            response_msg = f"I couldn't find {parsed['item']} on your list."
            
    elif action == "search" and parsed["item"]:
        # Mock the search behavior as per requirements
        if "price_limit" in parsed:
            response_msg = f"Searching for '{parsed['item']}' under ${parsed['price_limit']}..."
        else:
            response_msg = f"Searching for '{parsed['item']}'..."

    return jsonify({
        "status": "success",
        "action": action,
        "message": response_msg,
        "parsed": parsed,
        "list_updated": items_updated,
        "current_list": shopping_list
    })

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    recs = get_suggestions(shopping_history)
    return jsonify({
        "status": "success",
        "suggestions": recs
    })

@app.route('/api/list', methods=['GET'])
def get_list():
    return jsonify({
        "status": "success",
        "current_list": shopping_list
    })

@app.route('/api/add-item', methods=['POST'])
def add_item_direct():
    data = request.json
    item_name = data.get('item', '')
    if item_name:
        new_item = {
            "id": str(uuid.uuid4()),
            "name": item_name.capitalize(),
            "quantity": 1,
            "category": "General" # Simplification for direct add
        }
        shopping_list.append(new_item)
        shopping_history.append(new_item)
        return jsonify({"status": "success", "current_list": shopping_list, "message": f"Added {item_name}"})
    return jsonify({"status": "error", "message": "No item provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)
