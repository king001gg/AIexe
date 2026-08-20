import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载 .env（若存在）；已存在的环境变量优先，不被 .env 覆盖
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    try:
        return int(_env(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(_env(name, str(default)))
    except ValueError:
        return default


class AppSettings:
    APP_NAME = "AURA"
    APP_VERSION = "3.0"
    APP_SUBTITLE = "AI Intelligent Companion"
    PAGE_TITLE = "AURA · AI 智能伴侣"
    PAGE_ICON = "✨"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"

    DATA_DIR = os.path.join(BASE_DIR, "data")
    CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    DB_DIR = os.path.join(DATA_DIR, "db")
    KNOWLEDGE_DIR = os.path.join(DATA_DIR, "knowledge")

    # 运行时配置（可被 .env / 环境变量覆盖）
    DEEPSEEK_BASE_URL = _env("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_API_KEY = _env("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODELS = ["deepseek-chat", "deepseek-reasoner"]
    DEFAULT_MODEL = _env("DEEPSEEK_MODEL", "deepseek-chat")
    LOG_LEVEL = _env("LOG_LEVEL", "INFO")
    REQUEST_TIMEOUT = _env_float("REQUEST_TIMEOUT", 60.0)
    MAX_RETRIES = _env_int("MAX_RETRIES", 3)
    MAX_AGENT_ITERATIONS = _env_int("MAX_AGENT_ITERATIONS", 5)

    DEFAULT_USER_NAME = "用户"
    DEFAULT_AI_NAME = "AURA"
    DEFAULT_PERSONALITY = "理性冷静"

    USER_AVATAR = "🧑"
    AI_AVATAR = "🤖"

    PARTICLE_COUNT = 50
    PARTICLE_CONNECT_DIST = 150

    AUTO_TITLE_LENGTH = 20

    @classmethod
    def ensure_dirs(cls):
        for d in (cls.CONVERSATIONS_DIR, cls.LOGS_DIR, cls.DB_DIR, cls.KNOWLEDGE_DIR):
            os.makedirs(d, exist_ok=True)


class PersonalityConfig:
    PROMPTS = {
        "温柔体贴": "你是一个温柔体贴的AI伴侣，总是关心用户的感受，用温暖的语气回应，善于倾听和安慰。",
        "幽默风趣": "你是一个幽默风趣的AI伴侣，喜欢用轻松搞笑的方式交流，总能逗用户开心，但也会在需要时给出认真建议。",
        "理性冷静": "你是一个理性冷静的AI伴侣，善于分析问题，给出客观理性的建议，逻辑清晰，不感情用事。",
        "活泼可爱": "你是一个活泼可爱的AI伴侣，充满活力，喜欢用可爱的表情和语气交流，让对话充满乐趣。",
        "知性优雅": "你是一个知性优雅的AI伴侣，谈吐优雅，知识渊博，善于用优美的语言表达观点。",
    }

    TAGS = {
        "温柔体贴": "CARE",
        "幽默风趣": "HUMOR",
        "理性冷静": "LOGIC",
        "活泼可爱": "SPARK",
        "知性优雅": "ELEGANCE",
    }

    OPTIONS = list(PROMPTS.keys())

    @classmethod
    def get_prompt(cls, personality: str) -> str:
        return cls.PROMPTS.get(personality, cls.PROMPTS["理性冷静"])

    @classmethod
    def get_tag(cls, personality: str) -> str:
        return cls.TAGS.get(personality, "LOGIC")

    @classmethod
    def build_system_prompt(cls, ai_name: str, personality: str, user_name: str) -> str:
        desc = cls.get_prompt(personality)
        return (
            f"你是{ai_name}，一个{personality}的AI智能伴侣。"
            f"{desc}"
            f"用户的名字叫{user_name}。"
            f"请用自然、亲切的方式与用户对话。"
            f"当需要精确计算、查询实时日期时间、检索用户私有知识库或读写长期记忆时，"
            f"请使用系统提供的工具，不要凭空猜测。"
        )
