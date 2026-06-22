path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "rb") as f:
    raw = f.read()

content = raw.decode("utf-8")

idx = content.find("Trigger file written")
if idx == -1:
    print("ERROR: not found")
else:
    # Find the full line
    line_start = content.rfind("\n", 0, idx) + 1
    line_end = content.find("\n", idx)
    full_line = content[line_start:line_end]
    print("Full line:", repr(full_line))
    
    # Find return true line
    ret_idx = content.find("return true;", idx)
    ret_start = content.rfind("\n", 0, ret_idx) + 1
    ret_end = content.find("\n", ret_idx)
    ret_line = content[ret_start:ret_end]
    print("Return line:", repr(ret_line))
    
    old = full_line + "\n" + ret_line
    new = full_line + "\n            // Also trigger the task directly in case the time trigger is disabled\n            try\n            {\n                var psi = new System.Diagnostics.ProcessStartInfo\n                {\n                    FileName = \"schtasks.exe\",\n                    Arguments = \"/run /tn \\\"SIONYX_Update\\\"\",\n                    UseShellExecute = true,\n                    Verb = \"runas\",\n                    CreateNoWindow = true,\n                    WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden\n                };\n                System.Diagnostics.Process.Start(psi);\n                Logger.Information(\"[Update] Scheduled task triggered directly\");\n            }\n            catch (Exception taskEx)\n            {\n                Logger.Warning(\"[Update] Could not trigger task directly: {Err}\", taskEx.Message);\n            }" + "\n" + ret_line
    
    if old in content:
        content = content.replace(old, new, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched successfully!")
    else:
        print("ERROR: exact match not found")
        print("old:", repr(old))
