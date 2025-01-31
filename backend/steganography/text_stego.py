from backend.encryption.aes_128 import format_key, encrypt_aes_128, decrypt_aes_128
from io import BytesIO

class TextSteganographyError(Exception):
    pass

class MessageTooLargeError(TextSteganographyError):
    pass

class InvalidStegoFileError(TextSteganographyError):
    pass

def txt_encode(ip_file, text, op_file):
    l = len(text)
    i = 0
    add = ''
    
    while i < l:
        t = ord(text[i])
        if 0 <= t <= 64:
            t1 = t + 48
            t2 = t1 ^ 170  # 170: 10101010
            res = bin(t2)[2:].zfill(8)
            add += "0011" + res
        else:
            t1 = t - 48
            t2 = t1 ^ 170
            res = bin(t2)[2:].zfill(8)
            add += "0110" + res
        i += 1

    res1 = add + "111111111111"
    ZWC = {"00": u'\u200C', "01": u'\u202C', "11": u'\u202D', "10": u'\u200E'}

    # Reading words from the ip_file BytesIO object
    ip_file.seek(0)  # Make sure we're reading from the start
    words = [word for line in ip_file for word in line.decode('utf-8').split()]
    
    i = 0
    while i < len(res1):
        s = words[int(i / 12)]
        HM_SK = ''.join(ZWC[res1[j + i] + res1[i + j + 1]] for j in range(0, 12, 2))
        op_file.write((s + HM_SK + " ").encode('utf-8'))  # Write to op_file BytesIO
        i += 12

    t = int(len(res1) / 12)
    while t < len(words):
        op_file.write((words[t] + " ").encode('utf-8'))
        t += 1





def encode_txt_data(ip, msg, user_key):
    aes_key = format_key(user_key)
    encrypted_message = encrypt_aes_128(msg, aes_key)
    string_object = encrypted_message.decode('latin-1')

    input_content = ip.read().decode('utf-8')
    word_count = len(input_content.split())
    
    max_capacity = int(word_count / 6)
    if len(string_object) > word_count:
        raise MessageTooLargeError(f"Message too large! Maximum allowed words: {max_capacity}")
    
    output = BytesIO()
    txt_encode(BytesIO(input_content.encode('utf-8')), string_object, output)
    output.seek(0)
    return output

def BinaryToDecimal(binary):
    return int(binary, 2)

def decode_txt_data(stego, user_key):
    ZWC_reverse = {u'\u200C': "00", u'\u202C': "01", u'\u202D': "11", u'\u200E': "10"}
    temp = ''
    
    # Read the stego content directly as bytes
    stego_content = stego.read()  # Reading stego content as bytes
    stego_content_str = stego_content.decode('utf-8')  
    
    for line in stego_content_str.split('\n'):
        for words in line.split():
            binary_extract = ''.join(ZWC_reverse.get(letter, '') for letter in words)
            if binary_extract == "111111111111":
                break
            temp += binary_extract

    if not temp:
        raise InvalidStegoFileError("Invalid or non-encoded file provided.")

    i = 0
    a, b, c, d = 0, 4, 4, 12
    final = ''
    while i < len(temp):
        t3 = temp[a:b]
        t4 = temp[c:d]
        if t3 == '0110':
            final += chr((BinaryToDecimal(t4) ^ 170) + 48)
        elif t3 == '0011':
            final += chr((BinaryToDecimal(t4) ^ 170) - 48)
        a += 12
        b += 12
        c += 12
        d += 12
        i += 12
    aes_key = format_key(user_key)
    
    # Convert the decoded string to bytes using latin-1 encoding
    byte_data = final.encode('latin-1')  # Ensure it's in bytes format for AES decryption

    # Decrypt the message (decrypt_aes_128 expects bytes, so this is now correct)
    decrypted_message = decrypt_aes_128(byte_data, aes_key)
    
    # If the decrypted_message is bytes, decode it to string for returning
    if isinstance(decrypted_message, bytes):
        return decrypted_message.decode('utf-8')  # Decode to string if needed
    return decrypted_message  # If it's already a string

