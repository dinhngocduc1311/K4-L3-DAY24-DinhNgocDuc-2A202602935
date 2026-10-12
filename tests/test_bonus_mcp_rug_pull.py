from bonus.mcp_rug_pull import run_demo


def test_local_mcp_rug_pull_is_detected_before_second_call():
    result = run_demo()
    assert result["metadata_changed"] is True
    assert result["second_call_blocked"] is True
    assert result["pinned_hash"] != result["current_hash"]
    assert result["server_call_count"] == 1
    assert result["exfil_attempted"] is False
