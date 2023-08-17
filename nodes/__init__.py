from .combinatorial import DPCombinatorialGenerator
from .feeling_lucky import DPFeelingLucky
from .jinja import DPJinja
from .magicprompt import DPMagicPrompt
from .random_prompt import DPRandomGenerator
from .format_prompt import FormatPrompt
from .translate_prompt import TranslatePrompt
from .sdxl_image_size import SDXLImageSize
from .chatglm_prompt import ChatGLMPrompt,LoadChatGLMModel
NODE_CLASS_MAPPINGS = {
    "DPRandomGenerator": DPRandomGenerator,
    "DPCombinatorialGenerator": DPCombinatorialGenerator,
    "DPFeelingLucky": DPFeelingLucky,
    "DPJinja": DPJinja,
    "DPMagicPrompt": DPMagicPrompt,
    "FormatPrompt": FormatPrompt,
    "TranslatePrompt": TranslatePrompt,
    "SDXLImageSize": SDXLImageSize,
    "ChatGLMPrompt": ChatGLMPrompt,
    "LoadChatGLMModel": LoadChatGLMModel,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "DPRandomGenerator": "Random Prompts",
    "DPCombinatorialGenerator": "Combinatorial Prompts",
    "DPFeelingLucky": "I'm Feeling Lucky",
    "DPJinja": "Jinja2 Templates",
    "DPMagicPrompt": "Magic Prompt",
    "FormatPrompt": "Format Prompt",
    "TranslatePrompt": "Translate Prompt",
    "SDXLImageSize": "SDXL Image Size",
    "ChatGLMPrompt": "ChatGLM Prompt",
    "LoadChatGLMModel": "Load ChatGLM Model",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
