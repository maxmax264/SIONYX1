path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

changes = 0

# ---------------------------------------------------------------------------
# Root cause: ApplyIntervalFromRegistry() was called AFTER the try/finally
# block in CheckAndUpdateAsync. But the "no active session -> install
# immediately" branch does `return` from inside the try block, which exits
# the whole method (after running `finally`) WITHOUT ever reaching the
# ApplyIntervalFromRegistry() call below it. Since almost every check in
# practice ends up installing something, the periodic timer was in effect
# never started after the first install of a session - explaining why the
# Settings dialog showed "every 1 minute" (correctly read from the registry)
# but the check didn't actually run again until the user re-saved the
# setting (which calls ApplyIntervalFromRegistry() directly).
#
# Fix: call ApplyIntervalFromRegistry() from the `finally` block instead, so
# it always runs exactly once after every check, regardless of which branch
# (no update / install immediately / background download) was taken.
# ---------------------------------------------------------------------------

old_block = '''        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Update check failed (non-fatal)");
        }
        finally
        {
            _isCheckInProgress = false;
        }

        // Start periodic timer \u2014 default to 1 minute if no registry value set
        ApplyIntervalFromRegistry();
    }'''

new_block = '''        catch (Exception ex)
        {
            Logger.Warning(ex, "[Update] Update check failed (non-fatal)");
        }
        finally
        {
            _isCheckInProgress = false;

            // Start (or restart) the periodic timer here, in `finally`, so it
            // always runs exactly once after every check \u2014 regardless of
            // whether the check exited early via `return` (e.g. "no active
            // session, installing immediately"). Previously this call lived
            // after the try/finally block and was skipped by those early
            // returns, so the periodic timer effectively never started in
            // any session where an update was installed.
            ApplyIntervalFromRegistry();
        }
    }'''

count = content.count(old_block)
if count == 1:
    content = content.replace(old_block, new_block)
    changes += 1
    print("Applied: moved ApplyIntervalFromRegistry() into finally block.")
else:
    print(f"NOT applied: found {count} occurrences, expected 1.")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nTotal changes applied: {changes} of 1 expected.")
