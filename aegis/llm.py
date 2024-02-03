from ctransformers import AutoModelForCausalLM

llm = AutoModelForCausalLM.from_pretrained(
    'TheBloke/Llama-2-7B-Chat-GGML',
    model_file='llama-2-7b-chat.ggmlv3.q4_K_S.bin',
    context_length=4096,
    max_new_tokens=4096,
)
