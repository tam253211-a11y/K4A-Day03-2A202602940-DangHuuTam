# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Đặng Hữu Tâm  
> **Mã Sinh Viên / Mã Học viên:** 2A202602940
> **Chủ đề Lựa chọn:** Lĩnh vực Quản trị Nhân sự & Vận hành Nội bộ (HR & Operations)- Trợ lý Hỗ trợ Kỹ thuật IT Helpdesk
---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Cần tra cứu ticket cũ trước khi quyết định có tạo ticket escalate mới hay không |
| **2. Tool Interaction** | 5 / 5 | Bắt buộc gọi MCP Server để đọc/ghi dữ liệu ticket thời gian thực |
| **3. Dynamic Decision** | 4 / 5 | Hành động tạo ticket phụ thuộc vào kết quả của bước tra cứu trước |
| **4. Long Horizon Goal** | 3 / 5 | Mỗi yêu cầu xử lý độc lập trong 1 phiên, không cần giữ mục tiêu xuyên nhiều phiên dài |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | *Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu tình trạng ticket TCK-1001 giúp tôi.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "it_ticket_query",
    "arguments": { "ticket_id": "TCK-1001" },
    "observation": {
      "status": "SUCCESS",
      "ticket_id": "TCK-1001",
      "data": {
        "employee_id": "NV2026001",
        "issue_type": "network",
        "status": "IN_PROGRESS",
        "priority": "high",
        "assigned_to": "IT Support - Nguyễn Văn C"
      }
    },
    "latency_ms": 1694.68
  },
  {
    "step": 2,
    "query": "Hãy tra cứu tình trạng ticket TCK-1001 giúp tôi.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Kết quả tra cứu ticket TCK-1001: Loại sự cố: network, Trạng thái: IN_PROGRESS, Ưu tiên: high, Phụ trách: IT Support - Nguyễn Văn C, Cập nhật lần cuối: 2026-09-12 09:30.",
    "latency_ms": 10.0
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 4 lượt (TC02, TC03, TC04, TC05 mỗi case 1 lượt; TC01 không cần Tool).
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
