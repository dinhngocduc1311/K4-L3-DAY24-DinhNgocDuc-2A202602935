# Baseline — CP1

1. **Baseline đã có danh tính để kiểm quyền chưa?**
   Chưa: `_naive_loop()` chỉ nhận `message` và `llm`, không tạo `agent_id`/`run_id`
   hay nhận danh tính người dùng để kiểm quyền (`agent/loop.py:27`).
   Tuy `run_once()` có `principal_id` (`agent/loop.py:58`), nhánh scaffold gọi
   `_naive_loop(message, llm)` mà không chuyển danh tính này (`agent/loop.py:73`,
   `agent/loop.py:74`), nên baseline không áp dụng quyền của `support_l1`.

2. **Ai quyết định gửi và có policy trước `http_post` không?**
   Không có cổng kiểm mục đích, quyền hay loại dữ liệu trước `read_customer()`
   và `http_post()` (`agent/loop.py:39`, `agent/loop.py:44`).
   Ticket là dữ liệu, nhưng baseline ghép nội dung rồi xử lý chỉ thị bên trong
   như lệnh: kết quả `llm.find_injection()` quyết định mã khách cần đọc và URL
   cần gửi (`agent/loop.py:31`, `agent/loop.py:32`, `agent/loop.py:34`,
   `agent/loop.py:37`, `agent/loop.py:44`).
   `http_post()` chỉ kiểm URL có scheme HTTP, host `127.0.0.1`, port `10024`
   rồi gửi body; allowlist này không quyết định dữ liệu nào được phép gửi
   (`agent/tools.py:76`, `agent/tools.py:77`, `agent/tools.py:78`,
   `agent/tools.py:84`).

3. **Body POST được tạo ở đâu và sink ghi bằng chứng vào file nào?**
   Hồ sơ nguyên bản được thêm vào `collected` tại `agent/loop.py:39`, rồi
   body `{"records": collected}` được tạo ngay trong lời gọi `http_post()`
   tại `agent/loop.py:44`; `agent/tools.py:84` gửi body đó dưới dạng JSON.
   Sink ghi đường dẫn request và body nhận được vào `reports/sink.log`
   qua `make_handler().Handler.do_POST()` (`sink/sink.py:37`, `sink/sink.py:42`,
   `sink/sink.py:45`, `sink/sink.py:46`, `sink/sink.py:47`).
   CP2 cần chép log này thành `reports/attack-before.log` và đối chiếu body
   chứa `KH-000999` cùng CCCD/STK synthetic; CP1 chưa tạo bằng chứng POST.
