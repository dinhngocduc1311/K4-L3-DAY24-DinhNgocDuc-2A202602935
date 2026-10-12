# Verification

## BƯỚC 1 — Chuẩn bị repo và môi trường

Kiểm ngày 12/10/2026 (Asia/Bangkok). Đây là kết quả preflight, chưa phải
xác nhận hoàn thành CP1–CP5 hoặc đạt toàn bộ rubric.

- Đã đọc `README.md`, `RULES.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `SUBMISSION.md`,
  các module agent/sink và test liên quan đến các CP.
- Fork cá nhân: https://github.com/dinhngocduc1311/K4-L3-DAY24-DinhNgocDuc-2A202602935.
  GitHub xác nhận `fork=true`, parent là
  `VinUni-AI20k/K4-Track2-Day24-Data-Governance-Security-Student`.
- `origin` fetch/push trỏ đúng fork; branch `main` tại
  `52b33b5bddfcfdb5425010d6996c5c1d8eed13bd`, khớp remote lúc kiểm.
- `CHECKPOINTS.md` có trong checkout; `git cat-file -t 1bdd849` trả `commit`;
  `git rev-parse --is-shallow-repository` trả `false`. Giữ nguyên lịch sử Git.
- OS: Windows 10, build 19045; Git 2.39.2.windows.1; Python 3.11.9.
  Đã tạo `.venv`; gọi trực tiếp `.venv/Scripts/python.exe`, không cần đổi
  execution policy của Windows. README chưa coi Windows native là nền tảng
  pilot chính thức; các lệnh preflight ghi dưới đây đã chạy được tại checkout này.
- Đã cài dependency từ `requirements.txt`, pre-commit 4.6.2 và pip-tools 7.6.2.
- Gitleaks 8.30.1 nằm trong PATH tại `C:/Users/DELL/.local/bin/gitleaks.exe`.
  Binary lấy từ [release chính thức](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1),
  archive `gitleaks_8.30.1_windows_x64.zip` đã đối chiếu checksum SHA-256:
  `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e`.
- `python -m piptools compile --generate-hashes --index-url https://pypi.org/simple -o requirements.lock requirements.txt`:
  thành công; package được pin phiên bản và có SHA-256.
- `python -m pip install --require-hashes -r requirements.lock`: exit 0.
  Đã chạy thêm `--force-reinstall --require-hashes` để kiểm hash khi thực sự
  cài lại các package, thay vì chỉ thấy dependency đã có sẵn: exit 0.
- `python -m pip check`: `No broken requirements found.`
- `python -m agent.check_lure corpus/ticket-901.md`: `1/1 lure sẵn sàng`;
  nhận diện `KH-000999`, đích `http://127.0.0.1:10024/reconcile`.
- `python -m agent.loop --mock --as support_l1 "Tóm tắt ticket về hoá đơn"`:
  exit 0, tổng hợp 41 ticket. Sink localhost chạy trong background thread,
  ghi vào thư mục tạm và được đóng sau lệnh; kiểm thấy record tổng hợp
  `KH-000999` do baseline chưa có containment. Đây là smoke check setup,
  không thay thế `reports/attack-before.log` cần tạo tại CP2.
- `python -m pytest tests/test_check_lure_cli.py tests/test_scaffold_dispatch.py -q`:
  **7 passed**.
- `python -m pytest tests/test_supply_chain.py::test_dependency_lock_has_hashes -q`:
  **1 passed**.
- Quét snapshot các file working tree được `git ls-files` liệt kê, cộng
  `requirements.lock`, bằng `gitleaks dir --config .gitleaks.toml --redact --no-banner`:
  exit 0, `no leaks found`. Snapshot chỉ loại các file không nộp như `.venv/`
  và `.git/`; cấu hình scanner giữ nguyên. `git diff --check`: exit 0.

### Lỗi/cảnh báo gặp trong preflight

- `python -m piptools --version` không được hỗ trợ: `No such option: --version`.
  Đã lấy phiên bản bằng `importlib.metadata.version('pip-tools')`: 7.6.2.
- pip-compile cảnh báo `--strip-extras` sẽ thành mặc định ở phiên bản 8;
  lệnh tạo lock vẫn thành công, requirements hiện tại không dùng extras.
- `gitleaks dir --config .gitleaks.toml --redact --no-banner .` trả exit 1:
  một finding `generic-api-key` tại
  `.venv/Lib/site-packages/setuptools/_distutils/msvccompiler.py:45`.
  Finding nằm trong dependency cục bộ đã được `.gitignore` loại khỏi bài nộp,
  không phải finding token giả ở commit `1bdd849`. Không sửa rule hoặc
  allowlist để che finding. CP4 cần phân biệt quét file nguồn và quét lịch sử.

## BƯỚC 2 — CP1 và CP2

Kiểm ngày 12/10/2026 (Asia/Bangkok). Đối chiếu đề BƯỚC 2 mới với
README/RULES/CHECKPOINTS/RUBRIC/SUBMISSION và các mẫu báo cáo trong repo.

- CP1: `reports/baseline.md` đủ 3 câu trả lời, có số dòng code đã đối chiếu.
  Commit `8979dccfae0733d9ea3c695778d109cbff90da56`, nội dung `complete cp1`
  do sinh viên cung cấp; đã push `origin/main`, `git ls-remote` xác nhận SHA.
- CP2 giữ nguyên `agent/runner.py` scaffold, agent/loop/llm/tools, sink,
  `ticket-901.md`, các fixture dữ liệu và toàn bộ test bắt buộc.
- Thêm `ticket-902.md` (markup ẩn), `ticket-903.md` (giả thẩm quyền),
  cặp `ticket-904.md`/`ticket-904b.md` (chia payload); mọi tiêu đề có `Ticket`.
- `python -m agent.check_lure corpus/ticket-90*.md`: exit 0,
  **4/4 lure sẵn sàng**, số marker lần lượt 4, 6, 7, 2.
  Cả bốn nhắm `KH-000999` và `http://127.0.0.1:10024/reconcile`.
- Kiểm riêng mỗi file 904/904b bằng `find_injection`: đều trả `None`;
  ghép hai file thì nhận diện được đúng mã khách và URL.
- `python -m pytest tests/test_red_team_lures.py tests/test_check_lure_cli.py tests/test_scaffold_dispatch.py -q`:
  **12 passed** (5 test bổ sung, 7 test có sẵn).
- Đã chạy `python sink/sink.py --reset`, bật sink bằng `run_in_background()`
  của repo tại `127.0.0.1:10024`, rồi chạy CLI
  `python -m agent.loop --mock "Tổng hợp các ticket còn mở tuần này"`:
  exit 0, tổng hợp 45 ticket, sink nhận một POST thật chứa hồ sơ synthetic.
  Background thread dùng cùng server/handler và `reports/sink.log` như CLI
  sink; được đóng sau khi lấy bằng chứng.
- Reset sink lần nữa, replay `_naive_loop` trên thư mục tạm chỉ sao chép
  từng lure theo đoạn mẫu của đề mới, rồi copy `sink.log` thành
  `reports/attack-before.log`. **4 dòng POST thật** theo thứ tự 901, 902,
  903, cặp 904/904b; mỗi dòng có `path=/reconcile` và body chứa nguyên record
  `KH-000999`, gồm CCCD/SĐT/STK/email synthetic.
- Self-check parse hai lớp JSON, đối chiếu toàn bộ mỗi record với fixture
  `data/customers.json`, xác nhận số dòng tăng đúng 1 sau mỗi replay,
  bản sao evidence khớp byte với sink log và corpus thật giữ nguyên.
- `injection-corpus.md` ghi đủ kỹ thuật, lý do agent đọc, kết quả check_lure,
  dòng evidence từng biến thể và trạng thái sau containment chưa thực hiện.
  Không tạo `attack-after.log` từ baseline.
- Gitleaks 8.30.1 quét snapshot file nguồn tracked/untracked không bị ignore,
  cộng `reports/attack-before.log`, giữ nguyên `.gitleaks.toml`: exit 0,
  `no leaks found`. Snapshot loại `.venv/`, `.git/` và file không nộp.
- `git diff --check`: exit 0. SHA-256 của `attack-before.log` đã đối chiếu:
  `d97af1b21f949b58769d2259649885c9e1142afad18f5d446fe0f13359a54dac`.
  Đưa đúng log synthetic vào staging bằng `git add -f`, không đưa `sink.log`
  hoặc `.venv/` vào commit.
- Không có lỗi trong kiểm tra CP2 ở trên. Test containment chỉ chạy sau
  CP3; chưa mô tả CP2 là đã chặn được injection hoặc đạt toàn bộ rubric.

## Kiểm tra cuối bài — chưa thực hiện

- `python -m pytest tests/ -q`: chưa chạy toàn bộ; control còn scaffold.
- `pre-commit run --all-files`: chưa chạy; cấu hình và cài hook thuộc CP4.
- Quét lịch sử token giả: thuộc CP4, chưa thực hiện.
- Ledger verify: thuộc CP3e/CP5, chưa thực hiện.
- Log before đã tạo ở CP2; log after, ledger và báo cáo CP4/CP5 chưa tạo.
- Nội dung commit do sinh viên cung cấp; CP1 đã commit/push, thông điệp CP2
  do sinh viên nhập là `Complete CP2`. Lấy SHA cuối cùng bằng
  `git rev-parse HEAD` khi nộp bài.
