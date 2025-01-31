from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
from backend.steganography.audio_stego import encode_aud_data, decode_aud_data, AudioSteganographyError
from backend.steganography.text_stego import encode_txt_data, decode_txt_data, TextSteganographyError
from backend.steganography.image_stego import encode_img_data,decode_img_data,ImageSteganographyError

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audio-steganography')
def audio_steganography():
    return render_template('audio-steganography.html')

@app.route('/text-steganography')
def text_steganography():
    return render_template('text-steganography.html')

@app.route('/image-steganography')
def image_steganography():
    return render_template('image-steganography.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def  help():
    return render_template('help.html')

@app.route('/encode_audio', methods=['POST'])
def encode_audio():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            message = request.form['message']
            private_key = request.form['privateKey']
            
            # Read the file into memory
            input_file = BytesIO(file.read())
            
            # Encode the data
            output_file = encode_aud_data(input_file, message, private_key)
            
            # Prepare the response
            output_filename = f"encoded_{file.filename}"
            return send_file(
                output_file,
                as_attachment=True,
                download_name=output_filename,
                mimetype='audio/wav'
            )
    
    except AudioSteganographyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/decode_audio', methods=['POST'])
def decode_audio():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            private_key = request.form['privateKey']
            
            # Read the file into memory
            file_data = BytesIO(file.read())
            
            decoded_message = decode_aud_data(file_data, private_key)
            
            return jsonify({
                'success': True,
                'message': decoded_message
            })
    
    except AudioSteganographyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    
@app.route('/encode_text', methods=['POST'])
def encode_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            message = request.form.get('message')
            private_key = request.form.get('privateKey')

            if not message or not private_key:
                return jsonify({'error': 'Message or private key is missing'}), 400
            
            
            # Read the file into memory
            input_file = BytesIO(file.read())
            input_file.seek(0)  
            
            # Encode the data
            output_file = encode_txt_data(input_file, message, private_key)
            
            # Ensure the output is a file-like object
            if not isinstance(output_file, BytesIO):
                raise ValueError("Encoding failed, output file is not valid")

            # Prepare the response
            output_filename = f"encoded_{file.filename}"
            return send_file(
                output_file,
                as_attachment=True,
                download_name=output_filename,
                mimetype='text/plain'
            )
    
    except TextSteganographyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {str(e)} eorrorrrrrrrrr")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/decode_text', methods=['POST'])
def decode_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            private_key = request.form['privateKey']
            
            # Read the file into memory
            input_file = BytesIO(file.read())
            
            # Decode the data
            decoded_message = decode_txt_data(input_file, private_key)
            
            return jsonify({'message': decoded_message})
    
    except TextSteganographyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/encode_image', methods=['POST'])
def encode_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            message = request.form['message']
            private_key = request.form['privateKey']
            
            # Read the file into memory
            input_file = BytesIO(file.read())
            
            # Encode the data
            output_file = encode_img_data(input_file, message, private_key)
            
            # Prepare the response
            output_filename = f"encoded_{file.filename}"
            return send_file(
                output_file,
                as_attachment=True,
                download_name=output_filename,
                mimetype='image/png'
            )
    
    except ImageSteganographyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/decode_image', methods=['POST'])
def decode_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            private_key = request.form['privateKey']
            
            # Read the file into memory
            file_data = BytesIO(file.read())
            
            decoded_message = decode_img_data(file_data, private_key)
            
            return jsonify({
                'success': True,
                'message': decoded_message
            })
    
    except ImageSteganographyError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)