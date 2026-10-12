package lab24

import rego.v1

valid_classifications := {"public", "internal", "restricted"}

default decision := {"allow": false, "reason": "policy input is invalid"}

decision := {"allow": false, "reason": sprintf("unknown data classification: %q", [input.data_classification])} if {
	not valid_classifications[input.data_classification]
} else := {"allow": false, "reason": "restricted data cannot be used by an egress-enabled call"} if {
	input.data_classification == "restricted"
	input.egress_enabled == true
} else := {"allow": false, "reason": "delegation depth cannot be negative"} if {
	input.delegation_depth < 0
} else := {"allow": false, "reason": sprintf("unknown principal: %q", [input.principal_id])} if {
	not data.principals[input.principal_id]
} else := {"allow": false, "reason": sprintf("purpose %q is not allowed for %s", [input.request_purpose, input.principal_id])} if {
	principal := data.principals[input.principal_id]
	not input.request_purpose in principal.purposes
} else := {"allow": false, "reason": sprintf("principal %s cannot use %q", [input.principal_id, input.requested_tool])} if {
	principal := data.principals[input.principal_id]
	not input.requested_tool in principal.allowed_tools
} else := {"allow": false, "reason": sprintf("agent scope does not include %q", [input.requested_tool])} if {
	not input.requested_tool in input.agent_scopes
} else := {"allow": false, "reason": sprintf("parent scope does not include %q", [input.requested_tool])} if {
	input.delegation_depth > 0
	not input.requested_tool in input.parent_scopes
} else := {"allow": false, "reason": "expires_at must be an RFC-3339 timestamp with a UTC offset"} if {
	not regex.match(`^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$`, input.expires_at)
} else := {"allow": false, "reason": "delegated authority has expired"} if {
	time.parse_rfc3339_ns(input.expires_at) <= time.now_ns()
} else := {"allow": true, "reason": sprintf("principal %s may use %s for %s", [input.principal_id, input.requested_tool, input.request_purpose])} if {
	time.parse_rfc3339_ns(input.expires_at) > time.now_ns()
}
