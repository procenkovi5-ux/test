from flask import Flask, request, jsonify

app = Flask(__name__)

# Existing code

@app.route('/api/product/add', methods=['POST'])
def add_product():
    data = request.get_json()
    # Logic to add product to catalog
    return jsonify({'message': 'Product added successfully!'}), 201

if __name__ == '__main__':
    app.run(debug=True)