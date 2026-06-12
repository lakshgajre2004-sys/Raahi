import server
print("Registered routes:")
for rule in server.app.url_map.iter_rules():
    methods = ",".join(sorted(rule.methods - {"HEAD","OPTIONS"}))
    print(f"{rule.rule:40s}  -> {methods}")
