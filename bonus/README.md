# Bonus Day 24

Bốn bonus độc lập với luồng chấm bắt buộc. Chạy từ thư mục gốc repo:

```powershell
# OPA v1.21.1 tải từ release chính thức, không commit binary vào repo
python -m bonus.opa_parity --opa .tools\opa.exe

# GLiNER là dependency tùy chọn, không thay đổi requirements.lock của lab
python -m pip install -r bonus/requirements.txt
python -m bonus.compare_pii

python -m bonus.mcp_rug_pull
python -m bonus.delete_cascade
python -m pytest tests -k bonus -q --basetemp=.pytest_tmp
```

`delete_cascade` luôn làm demo trên thư mục tạm. Không lệnh bonus nào sửa
`data/`, `corpus/` hoặc `reports/ledger.jsonl` của bài chính.
