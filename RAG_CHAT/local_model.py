from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
from dotenv import load_dotenv



load_dotenv()
# 指定本地模型路径
if os.getenv("thinking_model"):
    model_path = os.getenv("llm_model_thinking")
else:
    model_path = os.getenv("llm_model")

if model_path:
    # 加载模型和分词器
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    # 将模型移动到 GPU（如果可用）
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)


def local_model_chat(history, history_round, prompt_template, temperature, max_tokens, thinking):


    # 系统消息
    system_message = {'role': 'system', 'content': 'You are a helpful assistant.'}
    
    # 准备对话历史和系统消息
    messages = []
    history_round = min(len(history), history_round) 
    for i in range(history_round):
        messages.append({'role': 'user', 'content': history[-history_round + i][0]})
        messages.append({'role': 'assistant', 'content': history[-history_round + i][1]})
    messages.append({'role': 'user', 'content': prompt_template})
    messages = [system_message] + messages


    if os.getenv("thinking_model"):

        # 使用分词器处理对话模板
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking= thinking,
        )

        # 对输入文本进行编码
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # 生成响应
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_tokens,
            temperature = temperature,
        )

        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

        # parsing thinking content
        try:
            # rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

        print("thinking content:", thinking_content)
        print("content:", content)

        return content
    
    else:

        # 使用分词器处理对话模板
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        # 对输入文本进行编码
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # 生成响应
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_tokens,
            temperature = temperature,
        )

        # 提取生成的响应
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        # 解码生成的响应
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # 打印生成的对话响应
        print(response)

        return response
















