# Compliance mapping của bài lab

Đối chiếu ngày 12/10/2026 (Asia/Bangkok). Bảng này ánh xạ control kỹ thuật
trong lab, không phải ý kiến pháp lý hoặc chứng nhận tuân thủ.

| Nguồn / chủ đề | Control đã làm | Bằng chứng file:dòng thật | Giới hạn |
|---|---|---|---|
| [Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15](https://vanban.chinhphu.vn/?classid=1&docid=214590&pageid=27160&typegroup=) | Nhận diện/redact CCCD, điện thoại, STK, email; phân loại hồ sơ `restricted`; chặn restricted egress; replay không gửi hồ sơ. | `agent/pii.py:51`, `agent/pii.py:65`, `agent/policy.py:64`, `reports/verification.md:249` | Đã kiểm số hiệu, tên, ngày hiệu lực trên Cổng TTĐT Chính phủ; **chưa xác minh điều khoản cụ thể** từ toàn văn. Fixture synthetic và regex không chứng minh tuân thủ thực tế. |
| [Nghị định 356/2025/NĐ-CP](https://vanban.chinhphu.vn/?classid=1&docid=216387&pageid=27160) | Giới hạn theo principal, purpose, tool, scope và thời hạn; policy chạy trước tool; ledger ghi reason và hash tham số. | `agent/policy.py:69`, `agent/policy.py:73`, `agent/policy.py:79`, `agent/runner.py:162`, `agent/ledger.py:51` | Đã kiểm số hiệu, trích yếu và hiệu lực trên nguồn chính thức; **chưa xác minh điều khoản cụ thể**. Principal chỉ là fixture, chưa có authentication/IAM thật. |
| [Luật Trí tuệ nhân tạo 134/2025/QH15](https://vanban.chinhphu.vn/?classid=1&docid=216334&orggroupid=1&pageid=27160) | Tách nội dung không tin cậy khỏi private store, giữ utility cho DPO, kiểm tool theo policy và tạo audit trail tamper-evident. | `agent/runner.py:149`, `agent/runner.py:154`, `agent/runner.py:161`, `agent/ledger.py:72`, `reports/verification.md:245` | Đã kiểm số hiệu, tên và hiệu lực trên nguồn chính thức; **chưa xác minh điều khoản cụ thể**. Mock LLM và test cục bộ không phải hệ thống AI production. |
| [OWASP Top 10 for Agentic Applications — ASI01/03/04](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) | ASI01: ticket injection không quyết định customer ID; ASI03: OBO/least privilege/TTL; ASI04: dependency pin+hash, Gitleaks pin và quét secret lịch sử. | `agent/runner.py:154`, `agent/policy.py:75`, `agent/policy.py:79`, `.pre-commit-config.yaml:3`, `requirements.lock:7`, `reports/secrets-incident.md:10` | Mapping theo taxonomy OWASP, không phải chứng nhận. Chưa kiểm registry provenance/signature; Gitleaks và hash lock không thay thế rotate credential hoặc runtime isolation. |

Không viện dẫn điều/khoản pháp luật cụ thể vì lab chưa thực hiện phân tích toàn
văn và tình huống pháp lý. Mọi kết luận chỉ áp dụng cho evidence kỹ thuật của
repo này.
