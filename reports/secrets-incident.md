# Báo cáo token giả trong lịch sử Git

Kiểm ngày 12/10/2026 (Asia/Bangkok). Bài tập chỉ dùng token synthetic đã
vô hiệu; không tìm kiếm hoặc sử dụng credential thật.

## Phát hiện

- Scanner: Gitleaks **8.30.1**, cấu hình `.gitleaks.toml` của repo.
- Lệnh lịch sử: `gitleaks git --config .gitleaks.toml --redact .`.
- Kết quả: mã thoát **1** như dự kiến, một finding của rule
  `lab24-synthetic-token` trong `lab-fake-secret.txt:1`, commit
  `1bdd849922156c868a5ee9293d68f5b72e242d2c`. Giá trị token đã được redact.
- Token không còn trong HEAD. Việc finding vẫn xuất hiện chứng minh xoá file
  ở commit mới không xoá dữ liệu khỏi lịch sử Git và không thu hồi token.

## Quét cây làm việc và false positive

Lần đầu chạy `gitleaks dir --config .gitleaks.toml --redact .` trả mã **1**
vì rule mặc định `generic-api-key` nhận nhầm `RegEnumKey` tại
`.venv/Lib/site-packages/setuptools/_distutils/msvccompiler.py:45`.
Đây là thư viện được cài trong virtual environment, không phải source hay
artifact nộp bài.

Đã thêm allowlist chỉ cho đường dẫn `^.venv/` trong `.gitleaks.toml`, không
tắt rule mặc định, không tắt `lab24-synthetic-token` và không bỏ qua repo.
Sau thay đổi:

- Quét lịch sử vẫn trả mã **1** và bắt đúng token giả ở commit `1bdd849`.
- Quét cây làm việc trả mã **0**, **no leaks found**.

## Dependency và hook

- `requirements.lock` được tạo bằng
  `python -m piptools compile --generate-hashes -o requirements.lock requirements.txt`.
- `python -m pip install --require-hashes -r requirements.lock` thành công;
  mọi dependency được pin phiên bản và có SHA-256 hash.
- Pre-commit dùng repo chính thức `https://github.com/gitleaks/gitleaks`,
  pin `v8.30.1`, hook `gitleaks-system`, `pass_filenames: false`.
- `pre-commit install` thành công; `pre-commit run --all-files` báo
  `Detect hardcoded secrets...Passed`.

## Ứng phó nếu đây là credential thật

Phải thu hồi hoặc rotate token ngay tại dịch vụ đã cấp token, thay credential
ở các workload hợp lệ, kiểm audit log để tìm việc sử dụng sai và xử lý mọi
bản sao trong fork, clone, cache, artifact hoặc log theo quy trình của dịch
vụ. Sau đó mới cân nhắc làm sạch lịch sử Git và thông báo người đã clone đồng
bộ lại. Xoá file khỏi HEAD, rewrite lịch sử hoặc pin dependency không làm
credential đã lộ tự vô hiệu; quyền truy cập chỉ bị cắt khi phía cấp token thu
hồi hoặc rotate nó.
