import cv2
import numpy as np
from backend.encryption.aes_128 import format_key, encrypt_aes_128, decrypt_aes_128
from io import BytesIO

class ImageSteganographyError(Exception):
    pass

def msgtobinary(message):
    if isinstance(message, str):
        return ''.join([format(ord(char), '08b') for char in message])
    elif isinstance(message, bytes) or isinstance(message, np.ndarray):
        return [format(byte, '08b') for byte in message]
    elif isinstance(message, int) or isinstance(message, np.uint8):
        return format(message, '08b')
    else:
        raise ImageSteganographyError("Input type not supported")

def encode_img_data(input_file, message, user_key):
    try:
        # Load the image from BytesIO
        img_array = np.asarray(bytearray(input_file.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ImageSteganographyError("Image could not be loaded. Please check the file content.")

        aes_key = format_key(user_key)
        encrypted_message = encrypt_aes_128(message, aes_key)
        string_object = encrypted_message.decode('latin-1')

        if len(string_object) == 0:
            raise ImageSteganographyError('Data entered to be encoded is empty')

        # Add a delimiter to mark the end of the message
        string_object += '*^*^*'

        binary_data = msgtobinary(string_object)
        length_data = len(binary_data)

        index_data = 0

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                pixel = img[i, j]
                r, g, b = msgtobinary(pixel)

                if index_data < length_data:
                    pixel[0] = int(r[:-1] + binary_data[index_data], 2)
                    index_data += 1
                if index_data < length_data:
                    pixel[1] = int(g[:-1] + binary_data[index_data], 2)
                    index_data += 1
                if index_data < length_data:
                    pixel[2] = int(b[:-1] + binary_data[index_data], 2)
                    index_data += 1

                img[i, j] = pixel

                if index_data >= length_data:
                    break
            if index_data >= length_data:
                break

        # Write the modified image to a BytesIO object
        is_success, encoded_image = cv2.imencode('.png', img)
        if not is_success:
            raise ImageSteganographyError("Failed to encode the image after embedding the message.")

        output_file = BytesIO(encoded_image.tobytes())
        output_file.seek(0)
        return output_file

    except Exception as e:
        raise ImageSteganographyError(f"An unexpected error occurred: {str(e)}")


def decode_img_data(stego_file, user_key):
    try:
        # Load the stego image from BytesIO
        img_array = np.asarray(bytearray(stego_file.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ImageSteganographyError("Image could not be loaded. Please check the file content.")

        # Collect the LSBs from the image
        bits = []
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                pixel = img[i, j]
                bits.append(msgtobinary(pixel[0])[-1])
                bits.append(msgtobinary(pixel[1])[-1])
                bits.append(msgtobinary(pixel[2])[-1])

        # Join the bits into a single binary string
        data_binary = ''.join(bits)

        # Convert the binary data to bytes in chunks of 8 bits
        total_bytes = [data_binary[i:i + 8] for i in range(0, len(data_binary), 8)]

        # Decode the binary data into characters
        decoded_data = ''.join([chr(int(byte, 2)) for byte in total_bytes])

        # Look for the delimiter "*^*^*" to find the hidden message
        if "*^*^*" in decoded_data:
            aes_key = format_key(user_key)
            string_object = decoded_data.split("*^*^*")[0]
            byte_data = string_object.encode('latin-1')
            decrypted_message = decrypt_aes_128(byte_data, aes_key)
            return decrypted_message

        raise ImageSteganographyError("No hidden message found or incorrect key.")

    except Exception as e:
        raise ImageSteganographyError(f"An unexpected error occurred: {str(e)}")
