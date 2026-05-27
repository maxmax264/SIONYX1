content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()
old = '''        lock (_knownJobs)
            {
                _knownJobs[printer] = new HashSet<int>(jobIds);
            }
        }
    }'''
new = '''        lock (_knownJobs)
            {
                _knownJobs[printer] = new HashSet<int>(jobIds);
            }
            lock (_processedJobs)
            {
                foreach (var id in jobIds)
                    _processedJobs.Add($"{printer}:{id}");
            }
        }
    }'''
if old in content:
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK')
else:
    print('NOT FOUND')
