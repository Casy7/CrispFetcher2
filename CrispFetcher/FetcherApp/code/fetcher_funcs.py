
def rec_replace(text:str, replace_from:str, replace_to:str):
    while replace_from in text:
        text = text.replace(replace_from, replace_to)
    return text

def get_text_between(text, start_text, end_text):
	start_index = text.find(start_text)
	if start_index == -1:
		return ""
	end_index = text.find(end_text, start_index+len(start_text))
	res_text = text[start_index+len(start_text):end_index]
	return res_text