from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0" # A small, fast model for testing
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=100)
llm = HuggingFacePipeline(pipeline=pipe)

chat_model = ChatHuggingFace(llm=llm)

# Now you can use it
result = chat_model.invoke("What is the capital of India?")
print(result)