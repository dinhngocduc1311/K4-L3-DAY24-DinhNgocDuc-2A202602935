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
- Tại thời điểm CP2, `injection-corpus.md` đã ghi đủ kỹ thuật, lý do agent
  đọc, kết quả check_lure và evidence từng biến thể; trạng thái sau
  containment được bổ sung sau khi hoàn tất CP3/CP5.
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

## BƯỚC 3 — CP3a, CP3b và CP3c

Kiểm ngày 12/10/2026 (Asia/Bangkok), theo đúng lệnh và `--basetemp`
trong đề BƯỚC 3 mới.

- `python -m pytest tests/test_pii.py -v -s --basetemp=.pytest_tmp`:
  **2 passed**; `gold=118`, `pred=118`, `tp=118`,
  `precision=1.000`, `recall=1.000`. Recall lớn hơn 95%, đạt band cao nhất
  trong `RUBRIC.md` trên testset synthetic hiện tại.
- PII gate nhận diện bốn loại `VN_CCCD`, `VN_PHONE`, `VN_BANK_ACCOUNT`,
  `EMAIL`, giữ offset `[start:end]`, loại vùng trùng và redact từ phải sang
  trái. STK có ưu tiên khi số 12 chữ số đồng thời giống định dạng CCCD.
- Giới hạn regex: không xác minh checksum/đầu số được cấp phát; STK chỉ được
  nhận diện khi có nhãn `STK` hoặc `số tài khoản`; email Unicode hoặc định
  dạng bất thường có thể bị bỏ sót; chuỗi số hợp lệ về hình thức vẫn có thể
  tạo false positive. Kết quả 1.000 chỉ áp dụng bộ mẫu synthetic của repo.
- `python -m pytest tests/test_policy.py -v --basetemp=.pytest_tmp`:
  **4 passed**. Có cả allow và deny: `restricted + egress` luôn deny, kể cả
  DPO; `search_docs` hợp lệ trên internal/public vẫn allow. Mọi nhánh trả
  reason không rỗng.
- Policy kiểm classification, principal fixture, purpose, tool trong cả
  `principal.allowed_tools` và scope cố định của agent, parent scope khi
  delegation, cùng expiry ISO-8601 có timezone. Unknown principal, scope
  thiếu, parent không có quyền, thời gian sai/hết hạn đều deny.
- `python -m pytest tests/test_obo.py -v --basetemp=.pytest_tmp`:
  **5 passed**. `support_l1` không gọi `read_customer`; `dpo` đọc được hồ sơ
  gắn với ticket hợp lệ; delegation không mở rộng quyền cha; expiry và
  principal lạ bị từ chối.
- Runner tạo `agent_id`, `run_id`, expiry riêng; policy và ledger chạy trước
  `search_docs`, `read_customer`, `http_post`. Ledger chỉ lưu SHA-256 của
  arguments, không lưu query/body/PII thô; mỗi entry có `on_behalf_of`,
  `agent_id`, `run_id`, `expires_at`, decision và reason.
- Nội dung ticket được redact trước khi đi tới bước summarize. Run B chỉ
  nhận ticket ID kiểu số lấy từ tên file và map sang customer qua
  `related_tickets`; không dùng customer ID trong free text attacker.
- Hồi quy `python -m pytest tests/test_split.py tests/test_injection.py tests/test_scaffold_dispatch.py -q --basetemp=.pytest_tmp/regression`:
  **13 passed**. Cả bốn lure bị chặn dưới `support_l1` và `dpo`, khách chỉ
  xuất hiện trong free text không bị đọc, còn khách liên kết hợp lệ vẫn đọc được.
- Lượt kiểm cuối gộp sáu file test PII/policy/OBO/split/injection/scaffold:
  **24 passed**. Self-check một lượt DPO tạo 23 ledger entry, có deny
  `http_post`, reason đầy đủ và không chứa CCCD/SĐT/STK/email thô từ fixture.
- `python -m compileall -q agent` và `git diff --check`: exit 0. Gitleaks
  8.30.1 quét snapshot năm file thay đổi của CP3: exit 0, `no leaks found`.
- Lần chạy OBO song song đầu tiên có 4 test pass và 1 lỗi setup
  `FileNotFoundError` vì ba tiến trình pytest cùng thao tác dưới `.pytest_tmp`.
  Chạy lại tuần tự đúng lệnh đề bài cho kết quả 5/5 pass; đây không phải lỗi
  logic policy/runner.
- Commit `f9374a991e7a51346faea244e73a331e94de3ae1` đã bị ghi `Complete CP3`
  và push trước khi nhận đủ đề CP3d/CP3e. Phần dưới ghi commit bổ sung để
  lịch sử phản ánh trung thực việc hoàn tất CP3 sau đó.

## BƯỚC 4 — CP3d và CP3e

Kiểm ngày 12/10/2026 (Asia/Bangkok), sau khi đối chiếu lại toàn bộ file
Markdown trong repo.

- Run A chỉ gọi `search_docs`, phát hiện lure, redact nội dung cho summarize
  và lấy ticket ID bằng mẫu tên file `ticket-(\d+).md`. Run B chỉ nhận tập
  `int` này; helper tra `related_tickets` từ `data/customers.json`, không
  nhận document text hoặc customer ID do attacker viết.
- Lượt policy `http_post` dùng classification `restricted`, bật egress và
  chỉ hash tham số URL. Hồ sơ khách không được đưa vào yêu cầu kiểm gửi;
  policy deny trước khi `tools.http_post` có thể chạy.
- `python -m pytest tests/test_split.py -v --basetemp=.pytest_tmp`:
  **1 passed**. `KH-000777` chưa từng được đọc, trong khi khách liên kết
  hợp lệ vẫn được đọc.
- `python -m pytest tests/test_injection.py -v --basetemp=.pytest_tmp`:
  **8 passed, 0 skipped** cho 4 lure × 2 principal. DPO đọc hợp lệ
  `KH-000999`; egress vẫn bị policy chặn.
- `python -m pytest tests/test_ledger.py -v --basetemp=.pytest_tmp`:
  **3 passed**. Hash chain nối từ 64 số `0`; sửa dòng cũ hoặc reason rỗng
  làm `verify()` trả `False`.
- Đã chạy đúng CLI DPO theo đề; agent tổng hợp 45 ticket và tạo
  `reports/ledger.jsonl` gồm 23 dòng. Lệnh kiểm ledger in `True`.
- Một lượt chạy lại thiếu `PYTHONIOENCODING` đã lỗi `UnicodeEncodeError`
  ở bước in tiếng Việt trên terminal CP1252 (sau khi ledger đã được ghi).
  Đã xoá evidence của lượt lỗi và chạy sạch lại với
  `$env:PYTHONIOENCODING='utf-8'`; CLI và kiểm ledger đều thành công.
- Ledger thật có một dòng `tool=http_post`, `decision=deny`, reason
  `restricted data cannot be used by an egress-enabled call`,
  `on_behalf_of=dpo`; không dòng nào thiếu reason/OBO metadata.
  Quét nội dung không thấy CCCD/SĐT/STK/email thô nào từ fixture.
- Kiểm lại ledger sau lần sinh cuối: **23 entries**, `verify=True`,
  `missing_reason=0`, anchor đầu là 64 số `0`, `raw_fixture_pii=0`.
- `gitleaks 8.30.1` quét riêng năm artifact CP3 đang thay đổi
  (`runner.py`, `ledger.py`, hai báo cáo và ledger thật): **no leaks found**.
  Quét thẳng cả thư mục repo còn đi vào `.venv` và báo một false positive
  `RegEnumKey` của `setuptools`; đây không phải source/artifact của bài.
- `git diff --check` và `python -m compileall -q agent`: thành công.
  `reports/attack-before.log` không đổi, SHA-256
  `d97af1b21f949b58769d2259649885c9e1142afad18f5d446fe0f13359a54dac`.
- Lượt kiểm toàn bộ `tests/` cho kết quả **36 passed, 2 failed**; hai lỗi
  duy nhất là `.pre-commit-config.yaml` chưa có và incident note chưa điền,
  đều là sản phẩm CP4 chưa được thực hiện. Chạy lại toàn bộ test ngoài
  `tests/test_supply_chain.py`: **35 passed**.
- Giới hạn: hash chain tự thân phát hiện sửa/chèn trong chuỗi hiện có,
  nhưng không phát hiện cắt dòng cuối hoặc viết lại toàn bộ chuỗi nếu không
  có mốc hash/số dòng cuối ở nơi tin cậy bên ngoài; lab không yêu cầu mốc đó.

## BƯỚC 5 — CP4 supply chain và secret giả

Kiểm ngày 12/10/2026 (Asia/Bangkok).

- Phiên bản: Python **3.11.9**, Gitleaks **8.30.1**, pip-tools/pip-compile
  **7.6.2**, pre-commit **4.6.2**.
- `gitleaks git --config .gitleaks.toml --redact .`: mã thoát **1** như
  dự kiến; một finding đã redact, rule `lab24-synthetic-token`, file
  `lab-fake-secret.txt:1`, commit đầy đủ
  `1bdd849922156c868a5ee9293d68f5b72e242d2c`.
- Lần đầu `gitleaks dir --config .gitleaks.toml --redact .` trả mã **1**
  do `generic-api-key` nhận nhầm `RegEnumKey` trong
  `.venv/Lib/site-packages/setuptools/_distutils/msvccompiler.py:45`.
  Chỉ allowlist `^.venv/`; quét lại lịch sử vẫn tìm đúng token giả, còn
  quét cây hiện tại trả mã **0**, `no leaks found`.
- `python -m piptools compile --generate-hashes -o requirements.lock requirements.txt`:
  thành công (có cảnh báo thay đổi mặc định `--strip-extras` ở pip-tools 8).
- `python -m pip install --require-hashes -r requirements.lock`: thành công;
  các package đã đúng phiên bản và hash trong lock.
- `.pre-commit-config.yaml` pin repo Gitleaks chính thức ở `v8.30.1`, dùng
  `gitleaks-system` và `pass_filenames: false`.
- `pre-commit install`: thành công tại `.git/hooks/pre-commit`.
- `pre-commit run --all-files`: `Detect hardcoded secrets...Passed`.
- Lượt test supply-chain đầu tiên: **2 passed, 1 failed** vì incident note
  còn placeholder. Sau khi ghi đầy đủ finding, false positive và quy trình
  rotate/thu hồi, chạy lại
  `python -m pytest tests/test_supply_chain.py -v --basetemp=.pytest_tmp`:
  **3 passed**.

## BƯỚC 5 — CP5 replay sau containment

Kiểm ngày 12/10/2026 (Asia/Bangkok), đúng query baseline và principal DPO.

- Lượt `python sink/sink.py --reset` đầu tiên đã reset file nhưng lỗi
  `UnicodeEncodeError` khi in tiếng Việt trên terminal CP1252, nên pytest
  chưa chạy. Chạy lại toàn bộ khối với
  `$env:PYTHONIOENCODING='utf-8'` thành công.
- Sau reset, `python -m pytest tests/ -q --basetemp=.pytest_tmp`:
  **38 passed, 0 failed, 0 skipped** trong 10.01 giây.
- Reset sink lần nữa, bật `python sink/sink.py`, rồi chạy
  `python -m agent.loop --mock --as dpo "Tổng hợp các ticket còn mở tuần này"`:
  agent tổng hợp **45 ticket** và kết thúc bình thường.
- `reports/sink.log` của riêng lượt replay có kích thước **0 byte**. Đã chép
  đúng trạng thái đó thành `reports/attack-after.log`, cũng **0 byte**.
- `reports/attack-before.log` giữ nguyên **1.196 byte**, có **4 dòng** POST
  synthetic chứa `KH-000999`; SHA-256 vẫn là
  `d97af1b21f949b58769d2259649885c9e1142afad18f5d446fe0f13359a54dac`.
- Sau replay, `reports/ledger.jsonl` có **46 dòng** vì giữ cả lượt CP3e và
  lượt CP5; `verify=True`, `missing_reason=0`. Có **2** entry `http_post`,
  đều `decision=deny`. Entry cuối có reason
  `restricted data cannot be used by an egress-enabled call` và
  `on_behalf_of=dpo`.
- Đã dừng sink bằng `Ctrl+C` sau khi lấy evidence.
- Một lệnh self-check cuối dùng `python -c` đã lỗi `SyntaxError` do escape
  quote trong PowerShell; chạy lại cùng phép kiểm bằng here-string cho
  `ledger_verify=True` (46 dòng, 2/2 `http_post` deny, 0 reason rỗng).
- Lượt kiểm artifact cuối: `pre-commit run --all-files` pass,
  `gitleaks dir --config .gitleaks.toml --redact .` trả mã 0/no leaks,
  `git diff --check` và `python -m compileall -q agent` thành công.

## Kiểm tra cuối bài

- Đã rà README/RULES/CHECKPOINTS/RUBRIC/SUBMISSION và các mẫu báo cáo:
  CP1–CP5 đủ code, test và evidence bắt buộc.
- CP4 đã hoàn thành hook, lock có hash, incident note, hai kiểu quét
  Gitleaks và test supply-chain; commit `88e706e` đã push lên `origin/main`.
- CP5 đã có replay thật, `attack-after.log` rỗng, ledger verify, compliance
  mapping, DPIA-lite và kết quả full suite.
- `pre-commit run --all-files`: đã pass ở CP4.
- Quét lịch sử token giả và quét file hiện tại: đã thực hiện ở CP4.
- Ledger verify và ledger thật đã hoàn thành ở CP3e.
- Log before, log after và ledger đã được đối chiếu ở CP5.
- Nội dung commit do sinh viên cung cấp; CP1 đã commit/push, thông điệp CP2
  do sinh viên nhập là `Complete CP2`. Lấy SHA cuối cùng bằng
  `git rev-parse HEAD` khi nộp bài.

## BƯỚC 6 — kiểm tra trước khi nộp

Kiểm ngày 12/10/2026 (Asia/Bangkok), trên nhánh `main`, working tree sạch
trước khi ghi mục này.

- `python -m pytest tests/ -q --basetemp=.pytest_tmp`:
  **38 passed, 0 failed, 0 skipped** trong 7.86 giây.
- `python -m agent.check_lure corpus/ticket-90*.md`:
  **4/4 lure sẵn sàng**, đúng `KH-000999` và endpoint localhost.
- `python -c "from agent.ledger import verify; ..."`: **True**.
- `pre-commit run --all-files`: `Detect hardcoded secrets...Passed`.
- `git status --short`: không có output trước khi cập nhật báo cáo này.
- Rà độc lập `test_obo.py`, `test_split.py`, `test_injection.py`:
  **14 passed**. `support_l1` không đọc restricted record, `dpo` vẫn đọc
  khách liên quan hợp lệ và `KH-000777` không bị đọc từ free text.
- Ledger có **46 dòng**, `missing_reason=0`, không chứa PII fixture và có
  **2** quyết định `http_post=deny`; `verify=True`.
- `attack-before.log` có **4** POST synthetic chứa `KH-000999`;
  `attack-after.log` **0 byte**, không chứa bất kỳ PII fixture nào.
- `gitleaks dir --config .gitleaks.toml --redact .`: mã 0,
  `no leaks found`. Không có secret hoặc PII thật được đưa vào bài.
- Đủ toàn bộ file bắt buộc trong `SUBMISSION.md`; ba evidence bị ignore
  (`attack-before.log`, `attack-after.log`, `ledger.jsonl`) đều đã được Git
  track. Commit synthetic `1bdd849` vẫn có kiểu object `commit`.
- Thư mục repo là `K4-L3-DAY24-DinhNgocDuc-2A202602935`, origin là fork cá
  nhân `https://github.com/dinhngocduc1311/K4-L3-DAY24-DinhNgocDuc-2A202602935.git`.

## Audit toàn repo sau BƯỚC 6

Kiểm ngày 12/10/2026 (Asia/Bangkok), giả định tải dự kiến là một học viên
chạy CLI/mock cục bộ như đề bài, không phải dịch vụ nhiều tiến trình.

- Đã đọc và đối chiếu 5 file hướng dẫn gốc, 6 file báo cáo/corpus do học
  viên viết và kiểm cấu trúc cả **56 Markdown được Git track**; 45 file
  `corpus/` đều đọc được bằng UTF-8 và có tiêu đề `# Ticket #...`.
- Kiểm tự động **52** tham chiếu `file:dòng`: mọi file tồn tại và không tham
  chiếu vượt số dòng hiện tại. Đối chiếu thủ công các dòng baseline, policy,
  split, ledger, compliance và evidence chính.
- Sửa finding tài liệu duy nhất: bốn mục sau-containment trong
  `injection-corpus.md` còn ghi CP5 đang chờ dù CP5 đã xong. Hiện mỗi lure có
  evidence trước/sau; file ghi đúng 8 test injection pass và log sau 0 byte.
- Source khung `agent/loop.py`, `agent/tools.py`, `agent/llm.py`, `sink/`,
  fixture và test bắt buộc không bị sửa để tạo kết quả đỗ. Chỉ có test bổ
  sung `tests/test_red_team_lures.py` cho bốn lure.
- Không có `.venv`, cache, `reports/sink.log` hay file cá nhân được Git
  track. Toàn bộ 19 artifact bắt buộc trong `SUBMISSION.md` có trên
  `origin/main`; repo không shallow và vẫn chứa commit synthetic `1bdd849`.
- Rà rubric bắt buộc: đủ evidence cho cả 10 tiêu chí, tương ứng **100/100
  điểm bắt buộc theo tự đánh giá**; không triển khai bonus tùy chọn.
- Rà 5 điều kiện trượt: 0 reason rỗng; after log 0 byte/0 PII fixture;
  split/OBO/injection 14 test pass; không PII raw trong ledger; Gitleaks cây
  hiện tại sạch và dữ liệu fixture được generator seed cố định xác nhận là
  synthetic.
