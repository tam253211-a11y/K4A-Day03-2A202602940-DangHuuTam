"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import re
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Xin chào! Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu dữ liệu thời gian thực)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()

        # 1. Có mã ticket dạng TCK-xxxx/TCK_xxxx -> ưu tiên tra cứu trước
        match = re.search(r"tck[-_]?(\d+)", prompt_lower)
        if match:
            ticket_id = f"TCK-{match.group(1)}"
            return {
                "type": "tool_call",
                "tool_name": "it_ticket_query",
                "arguments": {"ticket_id": ticket_id},
                "thought": f"Người dùng muốn biết tình trạng ticket {ticket_id}. Tôi sẽ gọi tool it_ticket_query."
            }

        # 2. Không có mã ticket nhưng yêu cầu tạo hỗ trợ mới
        if "tạo" in prompt_lower and ("hỗ trợ" in prompt_lower or "ticket" in prompt_lower or "yêu cầu" in prompt_lower):
            issue_type = "software"
            if "mạng" in prompt_lower or "vpn" in prompt_lower:
                issue_type = "network"
            elif "mật khẩu" in prompt_lower or "tài khoản" in prompt_lower or "đăng nhập" in prompt_lower:
                issue_type = "account"
            elif "laptop" in prompt_lower or "máy tính" in prompt_lower or "phần cứng" in prompt_lower:
                issue_type = "hardware"

            priority = "high" if ("gấp" in prompt_lower or "khẩn" in prompt_lower or "ưu tiên cao" in prompt_lower) else "medium"

            return {
                "type": "tool_call",
                "tool_name": "create_support_ticket",
                "arguments": {
                    "employee_id": "NV2026003",
                    "issue_type": issue_type,
                    "description": prompt,
                    "priority": priority
                },
                "thought": f"Người dùng yêu cầu tạo ticket hỗ trợ mới loại '{issue_type}'. Tôi sẽ gọi tool create_support_ticket."
            }

        # 3. Câu hỏi chung, không cần Tool
        return {
            "type": "text",
            "content": "[Mock Agent Response]: Để được hỗ trợ IT, bạn hãy mô tả sự cố (mạng, tài khoản, phần cứng, phần mềm) kèm mức độ ưu tiên, Agent sẽ tạo ticket giúp bạn.",
            "thought": "Câu hỏi chung về quy trình hỗ trợ IT, trả lời trực tiếp không cần gọi Tool."
        }



def _parse_gemini_quota_error(api_error) -> tuple:
    """Đọc quotaId (Per-Day hay Per-Minute) và retryDelay gợi ý (giây) từ lỗi 429 của Gemini."""
    quota_id = ""
    retry_seconds = None
    details = getattr(api_error, "details", None)
    if isinstance(details, dict):
        for d in details.get("error", {}).get("details", []):
            type_name = d.get("@type", "")
            if type_name.endswith("QuotaFailure"):
                violations = d.get("violations", [])
                if violations:
                    quota_id = violations[0].get("quotaId", "")
            elif type_name.endswith("RetryInfo"):
                match = re.match(r"([\d.]+)s", d.get("retryDelay", ""))
                if match:
                    retry_seconds = float(match.group(1))
    return quota_id, retry_seconds


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = None
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=config
                    )
                    break
                except Exception as api_error:
                    is_rate_limited = "RESOURCE_EXHAUSTED" in str(api_error) or "429" in str(api_error)
                    if not is_rate_limited:
                        raise

                    quota_id, retry_seconds = _parse_gemini_quota_error(api_error)

                    # Quota theo NGÀY (PerDay) sẽ không hồi phục dù đợi bao lâu trong hôm nay -> fallback ngay, không retry
                    if "PerDay" in quota_id:
                        print(f"🛑 [Gemini Quota]: Đã dùng hết hạn mức NGÀY của model '{self.model_name}' (quotaId: {quota_id}). Không thể retry hôm nay, chuyển sang Mock.")
                        raise

                    if attempt < max_retries:
                        wait_time = min(retry_seconds or (20 * (attempt + 1)), 30)
                        print(f"⏳ [Gemini Rate Limit]: Đợi {wait_time:.0f}s rồi thử lại (lần {attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        continue
                    raise

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
