"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
import os
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    {
        "name": "it_ticket_query",
        "description": "Tra cứu tình trạng xử lý của một ticket sự cố kỹ thuật (mạng, tài khoản, phần cứng, phần mềm) theo mã ticket.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "Mã ticket cần tra cứu (ví dụ: 'TCK-1001')"
                }
            },
            "required": ["ticket_id"]
        }
    },
    
    {
        "name": "create_support_ticket",
        "description": "Tạo yêu cầu hỗ trợ kỹ thuật IT mới cho nhân viên.",
        "parameters": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Mã nhân viên yêu cầu hỗ trợ (ví dụ: 'NV2026001')"
                },
                "issue_type": {
                    "type": "string",
                    "enum": ["network", "account", "hardware", "software"],
                    "description": "Loại sự cố kỹ thuật gặp phải"
                },
                "description": {
                    "type": "string",
                    "description": "Mô tả chi tiết vấn đề đang gặp phải"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Mức độ ưu tiên xử lý"
                }
            },
            "required": ["employee_id", "issue_type", "description"]
        }
    },

    {
        "name": "read_local_file",
        "description": "Đọc nội dung một file văn bản nội bộ (ví dụ log sự cố, ghi chú xử lý) đã lưu trong thư mục dữ liệu của Agent.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "Tên file cần đọc, không kèm đường dẫn thư mục (ví dụ: 'incident_log.txt')"
                }
            },
            "required": ["file_name"]
        }
    },

    {
        "name": "write_local_file",
        "description": "Ghi hoặc tạo mới một file văn bản nội bộ với nội dung cho trước, dùng để lưu ghi chú, tóm tắt hoặc báo cáo xử lý.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "Tên file cần ghi, không kèm đường dẫn thư mục (ví dụ: 'summary.txt')"
                },
                "content": {
                    "type": "string",
                    "description": "Nội dung văn bản cần ghi vào file"
                }
            },
            "required": ["file_name", "content"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

IT_TICKET_DATABASE = {
    "TCK-1001": {
        "employee_id": "NV2026001",
        "issue_type": "network",
        "description": "Không kết nối được VPN công ty",
        "status": "IN_PROGRESS",
        "priority": "high",
        "assigned_to": "IT Support - Nguyễn Văn C",
        "last_update": "2026-09-12 09:30"
    },
    "TCK-1002": {
        "employee_id": "NV2026002",
        "issue_type": "account",
        "description": "Quên mật khẩu email công ty",
        "status": "RESOLVED",
        "priority": "medium",
        "assigned_to": "IT Support - Trần Thị D",
        "last_update": "2026-09-10 14:00"
    }
}


def execute_it_ticket_query(ticket_id: str) -> str:
    """Thực thi tra cứu tình trạng ticket theo mã ticket"""
    ticket = IT_TICKET_DATABASE.get(ticket_id.strip().upper())
    if ticket:
        return json.dumps({
            "status": "SUCCESS",
            "ticket_id": ticket_id,
            "data": ticket
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy ticket có mã '{ticket_id}'"
        }, ensure_ascii=False)


def execute_create_support_ticket(employee_id: str, issue_type: str, description: str, priority: str = "medium") -> str:
    """Thực thi tạo yêu cầu hỗ trợ kỹ thuật mới"""
    new_id = f"TCK-{1000 + len(IT_TICKET_DATABASE) + 1}"
    return json.dumps({
        "status": "SUCCESS",
        "ticket_id": new_id,
        "employee_id": employee_id,
        "issue_type": issue_type,
        "priority": priority,
        "message": f"Đã tạo ticket {new_id} cho nhân viên {employee_id} ({issue_type}, ưu tiên {priority})."
    }, ensure_ascii=False)


# Thư mục dữ liệu riêng cho Agent đọc/ghi file — giới hạn trong phạm vi này để an toàn,
# không cho phép Agent đọc/ghi ra ngoài (ví dụ mã nguồn dự án).
AGENT_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "agent_files")
os.makedirs(AGENT_FILES_DIR, exist_ok=True)


def execute_read_local_file(file_name: str) -> str:
    """Thực thi đọc nội dung file trong thư mục dữ liệu Agent"""
    safe_name = os.path.basename(file_name)
    path = os.path.join(AGENT_FILES_DIR, safe_name)
    if not os.path.exists(path):
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy file '{safe_name}' trong thư mục dữ liệu Agent."
        }, ensure_ascii=False)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return json.dumps({
        "status": "SUCCESS",
        "file_name": safe_name,
        "content": content
    }, ensure_ascii=False)


def execute_write_local_file(file_name: str, content: str) -> str:
    """Thực thi ghi/tạo file trong thư mục dữ liệu Agent"""
    safe_name = os.path.basename(file_name)
    path = os.path.join(AGENT_FILES_DIR, safe_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return json.dumps({
        "status": "SUCCESS",
        "file_name": safe_name,
        "message": f"Đã ghi file '{safe_name}' thành công."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "it_ticket_query": execute_it_ticket_query,
    "create_support_ticket": execute_create_support_ticket,
    "read_local_file": execute_read_local_file,
    "write_local_file": execute_write_local_file
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
