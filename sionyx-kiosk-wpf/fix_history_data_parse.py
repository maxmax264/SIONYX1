content = open(r'.\src\SionyxKiosk\ViewModels\HistoryViewModel.cs', encoding='utf-8').read()

old1 = '            if (data == null) return;\n            var logs = new List<SessionLogItem>();\n            try\n            {\n                foreach (var entry in data.Value.EnumerateObject())'
new1 = '            if (data == null) return;\n            var logs = new List<SessionLogItem>();\n            try\n            {\n                var root = data.Value;\n                var logsEl = root.TryGetProperty("data", out var d) ? d : root;\n                if (logsEl.ValueKind != System.Text.Json.JsonValueKind.Object) return;\n                foreach (var entry in logsEl.EnumerateObject())'

old2 = '            if (data == null) return;\n            var logs = new List<PrintLogItem>();\n            try\n            {\n                foreach (var entry in data.Value.EnumerateObject())'
new2 = '            if (data == null) return;\n            var logs = new List<PrintLogItem>();\n            try\n            {\n                var root = data.Value;\n                var logsEl = root.TryGetProperty("data", out var d) ? d : root;\n                if (logsEl.ValueKind != System.Text.Json.JsonValueKind.Object) return;\n                foreach (var entry in logsEl.EnumerateObject())'

c1 = content.count(old1)
c2 = content.count(old2)
print(f"Sessions: {c1}, Prints: {c2}")
if c1 == 1:
    content = content.replace(old1, new1, 1)
    print("Sessions OK")
if c2 == 1:
    content = content.replace(old2, new2, 1)
    print("Prints OK")
open(r'.\src\SionyxKiosk\ViewModels\HistoryViewModel.cs', 'w', encoding='utf-8').write(content)
