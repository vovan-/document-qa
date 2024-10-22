def fix_json(json):
    start_index = json.find('{')
    end_index = json.rfind('}')
    return json[start_index:end_index+1]