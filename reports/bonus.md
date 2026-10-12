# Báo cáo bonus

Kiểm ngày 12/10/2026 (Asia/Bangkok). Bốn phần dưới đây có code, test và
log riêng. Rubric giới hạn tổng bonus ở 10 điểm dù bốn mục cộng thô là 14.

## OPA/Rego policy port

- `bonus/policy.rego` chuyển đủ thứ tự rule của `agent/policy.py`: phân loại,
  restricted + egress, delegation depth, principal, purpose, quyền tool,
  agent scope, parent scope và TTL. Mọi nhánh đều có reason.
- `bonus/opa_parity.py` chạy policy bằng OPA CLI thật và đối chiếu allow/deny
  với `agent.policy.check()` trên 13 ca. `bonus/opa_data.json` có test chống
  lệch với fixture principal gốc.
- OPA v1.21.1 `windows/amd64`; SHA-256 binary tải từ release chính thức là
  `25406f7c6e147d687fd7fd546f835bafa160a6242c605ee94a23ba6cd7bccdcd`,
  khớp checksum công bố. `opa fmt --fail` và `opa check --strict` đều pass.
- Kết quả: `reports/bonus-opa.log` ghi `OPA_PARITY=13/13`; test riêng ở
  `tests/test_bonus_opa.py`.
- Nguồn: [OPA Policy Language](https://www.openpolicyagent.org/docs/policy-language)
  và [OPA CLI](https://www.openpolicyagent.org/docs/cli).

Giới hạn: đây là parity test trên các nhánh của lab, chưa thay PEP Python bằng
OPA service trong runtime và chưa đo tải đồng thời.

## GLiNER so với regex

- `bonus/compare_pii.py` dùng đúng 120 dòng của
  `tests/vn_pii_testset.jsonl`; log giữ SHA-256 dataset để chứng minh hai bộ
  nhận diện chạy trên cùng input. Metric overlap giống `tests/test_pii.py`.
- Regex: gold/pred/tp = **118/118/118**, precision/recall = **1.000/1.000**.
- GLiNER 0.2.29, model `urchade/gliner_multi_pii-v1` ghim revision
  `1fcf13e85f4eef5394e1fcd406cf2ca9ea82351d`, threshold cố định 0.3:
  gold/pred/tp = **118/97/96**, precision = **0.990**, recall = **0.814**;
  thời gian CPU 51.321 giây. Kết quả thật nằm ở `reports/bonus-gliner.log`,
  test metric/log ở `tests/test_bonus_gliner.py`.
- Lần chạy đầu thiếu `protobuf` ở tokenizer; cài `protobuf==6.33.5` rồi chạy
  lại thành công. Dependency tái hiện nằm trong `bonus/requirements.txt`.
- Nguồn model PII đa ngôn ngữ: [GLiNER models](https://github.com/urchade/GLiNER/blob/main/docs/intro.md).

Regex thắng trên test set synthetic có nhãn/format ổn định. GLiNER bỏ sót
nhiều hơn nhưng không cần regex riêng cho mỗi cách diễn đạt; kết quả này
không chứng minh model tốt hơn trên dữ liệu thật. Không tinh chỉnh threshold
trên chính test set để tránh báo một kết quả đã fit vào tập đánh giá.

## MCP rug pull local

- `bonus/mcp_rug_pull.py` mở server JSON-RPC local bằng subprocess. Lần
  `tools/list` đầu công bố tool tóm tắt chỉ có `query`; sau lần gọi hợp lệ,
  server đổi description/schema để đòi `destination` và upload dữ liệu.
- Client ghim SHA-256 của toàn bộ metadata tool. Lần list tiếp theo có hash
  khác nên client chặn trước `tools/call`: `metadata_changed=true`,
  `second_call_blocked=true`, `server_call_count=1`,
  `exfil_attempted=false` trong `reports/bonus-mcp.log`.
- Test end-to-end local ở `tests/test_bonus_mcp_rug_pull.py`. Theo tài liệu
  SDK chính thức, name/description/input schema là metadata client nhận qua
  `tools/list`: [MCP tools](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/servers/tools.md).

Giới hạn: demo chỉ hiện thực các method JSON-RPC cần cho kịch bản, không phải
MCP conformance suite. Metadata pinning cần quy trình chấp thuận khi server
nâng cấp hợp lệ; hash một mình không xác định thay đổi tốt hay xấu.

## Delete cascade và ledger

- `bonus/delete_cascade.py` từ chối chạy nếu ledger đầu vào không verify,
  xoá đúng một customer synthetic cùng ticket liên quan, rồi append audit
  tombstone chỉ chứa `args_hash`; không ghi customer ID hay PII thô.
- Demo dùng bản sao trong thư mục tạm: xoá 1 customer và 2 ticket, dữ liệu
  nguồn vẫn nguyên, ledger verify trước/sau đều `true`. Bằng chứng ở
  `reports/bonus-delete-cascade.log`; test ở
  `tests/test_bonus_delete_cascade.py` còn kiểm các giá trị PII đã biến mất,
  record khác còn nguyên và unknown customer không sửa dữ liệu.

Giới hạn: rollback file local xử lý lỗi trong demo nhưng không thay thế giao
dịch database/object-store. Ledger một file vẫn có giới hạn cắt đuôi đã nêu
trong báo cáo chính.
