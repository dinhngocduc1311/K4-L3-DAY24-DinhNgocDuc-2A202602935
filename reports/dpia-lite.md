# DPIA-lite cho bài lab

Kiểm ngày 12/10/2026 (Asia/Bangkok). Đây là mô tả học tập trên dữ liệu
synthetic, không phải hồ sơ đánh giá tác động pháp lý chính thức.

## 1. Dữ liệu nào được xử lý?

Run A đọc ticket giả trong `corpus/`. Ticket là dữ liệu không tin cậy và có
thể chứa prompt injection hoặc PII. Run B có thể đọc hồ sơ khách giả trong
`data/customers.json`, gồm customer ID, CCCD, số điện thoại, tài khoản ngân
hàng và email; runner phân loại lời gọi này là `restricted`. Ledger chỉ lưu
metadata quyết định và SHA-256 của tham số, không lưu tham số hoặc hồ sơ thô.

## 2. Ai xử lý và với mục đích nào?

`support_l1` được tìm ticket cho mục đích `summarize-tickets` nhưng không có
quyền đọc hồ sơ. `dpo` được đọc hồ sơ liên quan cho mục đích `support-reply`.
Các principal và quyền đều là fixture mô phỏng; `--as` không xác thực người
đang dùng máy và không đại diện cho IAM production.

## 3. Dữ liệu đi qua đâu?

Run A gọi `search_docs`, phát hiện lure và redact PII trước khi tóm tắt. Qua
ranh giới sang Run B chỉ có ticket ID kiểu số lấy từ tên file. Run B tra
`related_tickets` trong nguồn tin cậy, xin policy trước từng `read_customer`
và ghi mọi allow/deny vào `reports/ledger.jsonl`. Lure trỏ tới sink local
`http://127.0.0.1:10024/reconcile`; policy kiểm riêng `http_post` với dữ liệu
`restricted` và egress bật trước khi tool có thể chạy.

## 4. Chặn, cho phép và giới hạn nào còn lại?

Policy chặn `support_l1` đọc hồ sơ; vẫn cho `dpo` đọc khách thật sự liên quan
để giữ chức năng hợp lệ. Cả hai không thể gửi dữ liệu restricted: replay DPO
ghi `http_post=deny`, `attack-after.log` 0 byte, trong khi log baseline có bốn
POST synthetic. PII regex đạt precision/recall 1.0 trên fixture hiện có nhưng
không bảo đảm bao phủ mọi cách viết thực tế. Mock LLM, localhost sink, quyền
fixture và corpus nhỏ không mô phỏng authentication, mạng, concurrency hoặc
model production. Hash chain phát hiện sửa/chèn trong chuỗi hiện có, nhưng
không tự phát hiện cắt đuôi hay viết lại cả chuỗi nếu thiếu mốc tin cậy ngoài
file. Các control và test này không tự tạo ra chứng nhận tuân thủ pháp luật.
