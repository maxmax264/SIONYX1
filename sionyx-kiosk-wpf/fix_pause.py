path = r'.\src\SionyxKiosk\Services\ForceLogoutService.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    'private bool _isFirstEvent;',
    'private bool _isFirstEvent;\n    private bool _isPaused;'
)
content = content.replace(
    'public void StopListening()',
    'public void Pause() { _isPaused = true; }\n    public void Resume() { _isPaused = false; }\n\n    public void StopListening()'
)
content = content.replace(
    'if (_isFirstEvent)\n        {',
    'if (_isPaused) return;\n        if (_isFirstEvent)\n        {'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
