prompt_template = "Classifique: {initiative_text}"
initiative_text = "Iniciativa com chaves {exemplo}"
try:
    prompt = prompt_template.format(initiative_text=initiative_text)
    print(f"Success: {prompt}")
except Exception as e:
    print(f"Error: {e}")
