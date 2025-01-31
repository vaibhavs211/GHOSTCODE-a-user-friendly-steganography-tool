from backend.encryption.aes_128 import format_key, encrypt_aes_128, decrypt_aes_128
import wave
import io

class AudioSteganographyError(Exception):
    pass

class EncodingError(AudioSteganographyError):
    pass

class DecodingError(AudioSteganographyError):
    pass

def encode_aud_data(input_file, message, user_key):
    try:
        aes_key = format_key(user_key)
        encrypted_message = encrypt_aes_128(message, aes_key)
        string_object = encrypted_message.decode('latin-1')
        string_object = '^*^*^' + string_object + '*^*^*'  # Add delimiter to the encrypted message
        
        with wave.open(input_file, mode='rb') as song:
            params = song.getparams()
            nframes = song.getnframes()
            frames = song.readframes(nframes)
            frame_bytes = bytearray(frames)

        # Convert encrypted message to binary
        result = []
        for c in string_object:
            bits = bin(ord(c))[2:].zfill(8)
            result.extend([int(b) for b in bits])

        if len(result) > len(frame_bytes) * 2:
            raise EncodingError("Message too large to encode in the given audio file.")

        # Embedding message into LSB
        j = 0
        for i in range(len(result)):
            res = bin(frame_bytes[j])[2:].zfill(8)
            if res[-4] == str(result[i]):
                frame_bytes[j] = (frame_bytes[j] & 253)  # 253: 11111101
            else:
                frame_bytes[j] = (frame_bytes[j] & 253) | 2  # 2: 00000010
                frame_bytes[j] = (frame_bytes[j] & 254) | result[i]  # 254: 11111110
            j += 1

        frame_modified = bytes(frame_bytes)

        # Create output file in memory
        output_file = io.BytesIO()
        with wave.open(output_file, 'wb') as fd:
            fd.setparams(params)
            fd.writeframes(frame_modified)
        
        output_file.seek(0)
        return output_file

    except Exception as e:
        raise AudioSteganographyError(f"An unexpected error occurred: {str(e)}")

def decode_aud_data(stego_file, user_key):
    try:
        with wave.open(stego_file, mode='rb') as song:
            nframes = song.getnframes()
            frames = song.readframes(nframes)
            frame_bytes = bytearray(frames)

        extracted = ""
        start_delimiter_found = False
        decoded_data = ""

        # Extract bits from the LSB
        for i in range(len(frame_bytes)):
            res = bin(frame_bytes[i])[2:].zfill(8)
            if res[-2] == '0':
                extracted += res[-4]
            else:
                extracted += res[-1]

            # Check every 8 bits (1 byte)
            if len(extracted) % 8 == 0:
                byte = chr(int(extracted[-8:], 2))
                decoded_data += byte

                # Check for start delimiter first
                if not start_delimiter_found:
                    if decoded_data == "^*^*^":
                        start_delimiter_found = True
                        extracted = ""  # Clear the extracted data and continue from here
                        decoded_data = ""  # Clear the decoded data for the actual message
                else:
                    # If delimiter is found, start extracting the message
                    if decoded_data.endswith("*^*^*"):
                        aes_key = format_key(user_key)
                        string_object = decoded_data[:-5]  # Remove end delimiter
                        byte_data = string_object.encode('latin-1')
                        decrypted_message = decrypt_aes_128(byte_data, aes_key)
                        return decrypted_message

        raise DecodingError("No hidden message found or incomplete extraction.")

    except Exception as e:
        raise AudioSteganographyError(f"An unexpected error occurred: {str(e)}")
    
    