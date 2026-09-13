"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
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



# Router gọi tool thực tế
TOOL_ROUTER = {
    "it_ticket_query": execute_it_ticket_query,
    "create_support_ticket": execute_create_support_ticket
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
