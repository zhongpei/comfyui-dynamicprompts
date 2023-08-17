import subprocess
import os
from chatglm_cpp import Pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GLM_EXE_PATH = os.path.join(BASE_DIR, "chatglm.exe")
GLM_MODEL_PATH = "chatglm2-ggml.bin"


class LoadChatGLMModel:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("STRING", {"default": GLM_MODEL_PATH}),
            }
        }

    RETURN_TYPES = ("CHATGLM_MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_model"
    CATEGORY = "fofo/prompt"

    def load_model(self, model: str = GLM_MODEL_PATH):
        pipe = Pipeline(model_path=os.path.join(BASE_DIR, model))
        pipe.generate(prompt="test")
        return (pipe,)


class ChatGLMPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING",
                           {
                               "multiline": True,
                               "default": "用英语描述一副画面“宋朝 送别 桥头”，详细描述细节。"
                           }),
                "model": ("CHATGLM_MODEL",),
                "top_k": ("INT", {"default": 0}),
                "top_p": ("FLOAT", {"default": 0.8}),
                "temperature": ("FLOAT", {"default": 0.95}),

                "max_length": ("INT", {"default": 2048}),
                "max_context_length": ("INT", {"default": 256}),

                "repeat_penalty": ("FLOAT", {"default": 1.0}),
                "threads": ("INT", {"default": 8, "min": 1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt"
    OUTPUT_NODE = True
    CATEGORY = "fofo/prompt"

    def get_prompt(self,
                   prompt: str,
                   model: Pipeline = None,
                   top_k: int = 0,
                   top_p: float = 0.8,
                   temperature: float = 0.95,
                   max_length: int = 2048,
                   max_context_length: int = 256,

                   repeat_penalty: float = 1.0,
                   threads: int = 8
                   ) -> tuple[str]:
        prompt = prompt.replace("\"", '”')

        result = model.generate(
            prompt=prompt,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            max_length=max_length,
            max_context_length=max_context_length,
            repetition_penalty=repeat_penalty,
            num_threads=threads,
            stream=False
        )
        return (result,)
