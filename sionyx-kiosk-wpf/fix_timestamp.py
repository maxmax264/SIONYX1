path = r'.\src\SionyxKiosk\Services\ForceLogoutService.cs'
content = open(path, encoding='utf-8').read()

# הוסף timestamp field
content = content.replace(
    'private volatile bool _isPaused;\n    public bool IsPaused => _isPaused;',
    'private volatile bool _isPaused;\n    public bool IsPaused => _isPaused;\n    private DateTime _pausedAt = DateTime.MinValue;'
)

# עדכן Pause להכיל timestamp
content = content.replace(
    'public void Pause() { _isPaused = true; }',
    'public void Pause() { _isPaused = true; _pausedAt = DateTime.UtcNow; }'
)

# עדכן את ה-check ב-OnEvent להשתמש ב-timestamp במקום flag
content = content.replace(
    'if (_isPaused) return;',
    'if (_isPaused || (DateTime.UtcNow - _pausedAt).TotalSeconds < 10) return;'
)

open(path, 'w', encoding='utf-8').write(content)
print('OK')
