# Phase B: LLM-based Automation Agent for DataWorks Solutions
import os
import subprocess
import openai
from flask import Flask, request, jsonify
import pandas as pd

# B1 & B2: Security Checks

def B12(filepath):
    """Checks if the given file path is within the allowed directory and raises an error if not."""
    if not filepath.startswith('/data'):
        raise PermissionError("Access outside /data is not allowed.")
    
    return True  # Access is allowed


# B3: Fetch Data from an API
def B3(url, save_path):
    if not B12(save_path):
        return None
    import requests
    response = requests.get(url)
    with open(save_path, 'w') as file:
        file.write(response.text)

# B4: Clone a Git Repo and Make a Commit 
def clone_git_repo(repo_url, commit_message):
    """Clones a Git repository and makes an empty commit with a message."""
    repo_path = "/data/repo"

    try:
        # Clone the repository
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)

        # Change directory to the cloned repository
        os.chdir(repo_path)

        # Ensure the repository is initialized
        subprocess.run(["git", "add", "."], check=True)

        # Make a commit with the provided message
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        print("Repository cloned and commit made successfully.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False


# B5: Run SQL Query
def B5(db_path, query, output_filename):
    if not B12(db_path):
        return None
    import sqlite3, duckdb
    conn = sqlite3.connect(db_path) if db_path.endswith('.db') else duckdb.connect(db_path)
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    with open(output_filename, 'w') as file:
        file.write(str(result))
    return result

# B6: Web Scraping
def B6(url, output_filename):
    import requests
    result = requests.get(url).text
    with open(output_filename, 'w') as file:
        file.write(str(result))

# B7: Image Processing
def B7(image_path, output_path, resize=None):
    from PIL import Image
    if not B12(image_path):
        return None
    if not B12(output_path):
        return None
    img = Image.open(image_path)
    if resize:
        img = img.resize(resize)
    img.save(output_path)

# B8: Audio Transcription

def is_valid_path(filepath):
    """Checks if the given file path is within the allowed directory."""
    return filepath.startswith('/data')

def transcribe_audio(audio_path):
    """
    Transcribes an audio file using OpenAI's Whisper model.
    
    Args:
        audio_path (str): Path to the audio file.
        
    Returns:
        str: Transcribed text or None if access is denied or an error occurs.
    """
    if not is_valid_path(audio_path):
        print("Access denied: File must be inside /data directory.")
        return None
    
    try:
        with open(audio_path, 'rb') as audio_file:
            return openai.Audio.transcribe("whisper-1", audio_file)
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

# B9: Markdown to HTML Conversion
def B9(md_path, output_path):
    import markdown
    if not B12(md_path):
        return None
    if not B12(output_path):
        return None
    with open(md_path, 'r') as file:
        html = markdown.markdown(file.read())
    with open(output_path, 'w') as file:
        file.write(html)

# B10: API Endpoint for CSV Filtering

app = Flask(__name__)

def is_valid_path(filepath):
    """Checks if the given file path is within the allowed directory."""
    return filepath.startswith('/data')

@app.route('/filter_csv', methods=['POST'])
def filter_csv():
    """
    API endpoint to filter a CSV file based on a column value.
    
    Expected JSON payload:
    {
        "csv_path": "/data/sample.csv",
        "filter_column": "column_name",
        "filter_value": "desired_value"
    }
    
    Returns:
        JSON: Filtered records or an error message.
    """
    try:
        # Parse JSON request data
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['csv_path', 'filter_column', 'filter_value']):
            return jsonify({"error": "Missing required fields"}), 400
        
        csv_path = data['csv_path']
        filter_column = data['filter_column']
        filter_value = data['filter_value']

        # Security check for file path
        if not is_valid_path(csv_path):
            return jsonify({"error": "Access denied. File must be inside /data directory."}), 403

        # Check if file exists
        if not os.path.exists(csv_path):
            return jsonify({"error": f"File not found: {csv_path}"}), 404

        # Load and filter CSV
        df = pd.read_csv(csv_path)

        # Validate if column exists
        if filter_column not in df.columns:
            return jsonify({"error": f"Column '{filter_column}' not found in CSV"}), 400

        filtered = df[df[filter_column] == filter_value]

        # Return filtered data
        return jsonify(filtered.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
