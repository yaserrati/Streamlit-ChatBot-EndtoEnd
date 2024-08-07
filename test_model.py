from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
import pandasql as ps

# Load the tokenizer and model from the local directory
model_path = r"C:\Users\Desktop\YOURMODELPATH"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

players= pd.read_csv("football_players_n.csv")


# Question du client
question = "What is the old playerS?"

# Requête SQL générée par le modèle (exemple simple)
sql_query = "SELECT name, age FROM players WHERE age > 30;"

# Exécution de la requête SQL sur la DataFrame
result = ps.sqldf(sql_query, locals())

# Formatage du résultat en une chaîne de caractères
result_str = result.to_string(index=False)

paraphrase_prompt = f"""
You are a skilled paraphrasing expert. Given the following question and result, provide a detailed and comprehensive response. Include as much relevant information as possible and make the response informative and engaging.

Question: {question}
Result:
{result_str}

Detailed and Comprehensive Response:
"""

# Tokeniser l'entrée
inputs = tokenizer(paraphrase_prompt, return_tensors="pt", max_length=1024, truncation=True)

# Générer la paraphrase
outputs = model.generate(
    inputs.input_ids,
    max_length=512,
    num_beams=5,
    early_stopping=True,
    no_repeat_ngram_size=2,
    length_penalty=1.5
)

# Décoder la sortie
detailed_paraphrased_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(detailed_paraphrased_response)



