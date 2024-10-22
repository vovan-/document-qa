import os
import codecs

def get_assets(directory="demo_project"):
    info = "additional information about files:\n----------------------------------------------------------------------------"
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                try:
                    with codecs.open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read(5000)
                    info += "file path: " + filepath + "\n"
                    info += "file content:\n" + content
                    info += "\n----------------------------------------------------------------------------\n\n"
                except Exception as e:
                    print(f"error in reading file {filepath}: {e}")
    return info[:100000]
