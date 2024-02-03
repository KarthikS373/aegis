from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
import torch
import accelerate

use_4bit = True
bnb_4bit_compute_dtype = "float16"
bnb_4bit_quant_type = "nf4"
use_double_nested_quant = True
compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

# BitsAndBytesConfig 4-bit config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=use_4bit,
    bnb_4bit_use_double_quant=use_double_nested_quant,
    bnb_4bit_quant_type=bnb_4bit_quant_type,
    bnb_4bit_compute_dtype=compute_dtype,
    load_in_8bit_fp32_cpu_offload=True
)



# Load model in 4-bit
tokenizer = AutoTokenizer.from_pretrained("AlfredPros/CodeLlama-7b-Instruct-Solidity")
modelGen = AutoModelForCausalLM.from_pretrained("AlfredPros/CodeLlama-7b-Instruct-Solidity", quantization_config=bnb_config, device_map="balanced_low_0")