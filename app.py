from flask import Flask, jsonify, request
import sqlite3
import loot as lt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:4000", 'http://127.0.0.1:5008', 'https://simonhansedasi.github.io']}})


def index():
    return render_template('index.html')

@app.route('/get_loot', methods=['POST'])
def get_loot_endpoint():
    data = request.json
    cr_value = data.get('cr_value')
    print(cr_value)
    loot_type = data.get('loot_type')
    print(loot_type)
    # Validate CR value
    if not cr_value.isdigit() or int(cr_value) < 0:
        return jsonify({'error': 'Invalid CR value'}), 400

    cr_value = int(cr_value)

    try:
        # Call the appropriate function based on loot type
        if loot_type == 'hoard':
            coins, selected_art, selected_gems, magic_items = lt.roll_hoard(cr_value)
            coin = []
            if magic_items:
                print(magic_items)
            else:
                print('poops')
            for item in coins:
                coin.append(f'{int(item[1]):,} {item[0]}')
            result = {
                'coins': coin,
                'selected_art': selected_art,
                'selected_gems': selected_gems,
                'magic_items': magic_items
            }
            print(coin)
        elif loot_type == 'individual':
            cash = lt.roll_individual(cr_value)
            coin = []
            for item in cash:
                coin.append(f'{int(item[1]):,} {item[0]}')
            print(coin)
            result = {'cash': coin}
        else:
            return jsonify({'error': 'Invalid loot type'}), 400

        return jsonify(result)

    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port = 5008)