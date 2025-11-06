from flask import Flask, render_template, request
import numpy as np

app = Flask (__name__)

# -------------------------------
# Encryption Algorithms
# -------------------------------

def caesar_encrypt(text, shift):
    text = text.upper()
    return ''.join(chr((ord(ch) - 65 + shift) % 26 + 65) if ch.isalpha() else ch for ch in text)

def monoalphabetic_encrypt(text, key_map):
    text = text.upper()
    return ''.join(key_map.get(ch, ch) for ch in text)

def generate_playfair_matrix(key):
    key = key.upper().replace("J", "I")
    result = ""
    for ch in key:
        if ch not in result:
            result += ch
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    for ch in alphabet:
        if ch not in result:
            result += ch
    return [list(result[i:i+5]) for i in range(0, 25, 5)]

def playfair_encrypt(text, key):
    text = text.upper().replace("J", "I")
    if len(text) % 2 != 0:
        text += "X"
    matrix = generate_playfair_matrix(key)
    pos = {matrix[i][j]: (i, j) for i in range(5) for j in range(5)}
    result = ""
    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        r1, c1 = pos[a]
        r2, c2 = pos[b]
        if r1 == r2:
            result += matrix[r1][(c1+1)%5] + matrix[r2][(c2+1)%5]
        elif c1 == c2:
            result += matrix[(r1+1)%5][c1] + matrix[(r2+1)%5][c2]
        else:
            result += matrix[r1][c2] + matrix[r2][c1]
    return result

def hill_encrypt(plain, key_matrix):
    plain = plain.upper().replace(" ", "")
    if len(plain) % 2 != 0:
        plain += "X"
    result = ""
    for i in range(0, len(plain), 2):
        pair = np.array([[ord(plain[i])-65], [ord(plain[i+1])-65]])
        cipher_pair = np.dot(key_matrix, pair) % 26
        result += chr(int(cipher_pair[0][0]) + 65)
        result += chr(int(cipher_pair[1][0]) + 65)
    return result

def vigenere_encrypt(text, key):
    text, key = text.upper(), key.upper()
    result = ""
    for i in range(len(text)):
        if text[i].isalpha():
            shift = ord(key[i % len(key)]) - 65
            result += chr((ord(text[i]) - 65 + shift) % 26 + 65)
        else:
            result += text[i]
    return result

def rail_fence_encrypt(text, key):
    rail = ['' for _ in range(key)]
    direction_down = False
    row = 0
    for ch in text:
        rail[row] += ch
        if row == 0 or row == key-1:
            direction_down = not direction_down
        row += 1 if direction_down else -1
    return ''.join(rail)

def row_column_encrypt(text, key):
    text = text.replace(" ", "").upper()
    col = len(key)
    row = len(text) // col
    if len(text) % col != 0:
        row += 1
        text += "X" * (col*row - len(text))
    matrix = [list(text[i*col:(i+1)*col]) for i in range(row)]
    order = sorted(range(len(key)), key=lambda k: key[k])
    cipher = ""
    for idx in order:
        for r in range(row):
            cipher += matrix[r][idx]
    return cipher


# -------------------------------
# Flask Routes
# -------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        algo = request.form["algorithm"]
        text = request.form["plaintext"]
        key = request.form.get("key", "")
        
        if algo == "caesar":
            output = caesar_encrypt(text, int(key))
        elif algo == "mono":
            key_map = {chr(65+i): chr(90-i) for i in range(26)}  # simple reverse key
            output = monoalphabetic_encrypt(text, key_map)
        elif algo == "playfair":
            output = playfair_encrypt(text, key)
        elif algo == "hill":
            key_matrix = np.array([[3, 3], [2, 5]])
            output = hill_encrypt(text, key_matrix)
        elif algo == "vigenere":
            output = vigenere_encrypt(text, key)
        elif algo == "rail":
            output = rail_fence_encrypt(text, int(key))
        elif algo == "row":
            output = row_column_encrypt(text, key)
    
    return render_template("index.html", result=output)


if __name__ == "__main__":
    app.run(debug=True) 