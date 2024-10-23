# Function to read content from a file in the source code
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return None
