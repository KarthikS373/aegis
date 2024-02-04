from ctransformers import AutoModelForCausalLM


def create_llm_with_gpu(args):
    gpu_layers = 50 if args.gpu else 0  # Determine gpu_layers based on args.gpu
    llm = AutoModelForCausalLM.from_pretrained(
        'TheBloke/Llama-2-7B-Chat-GGML',
        model_file='llama-2-7b-chat.ggmlv3.q4_K_S.bin',
        context_length=4096,
        max_new_tokens=4096,
        gpu_layers=gpu_layers
    )
    return llm