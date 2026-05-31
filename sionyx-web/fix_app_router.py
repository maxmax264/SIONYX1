content = open(r'.\src\App.jsx', encoding='utf-8').read()

old = """const SupervisorSettingsPage = lazy(() => import('./supervisor/pages/SupervisorSettingsPage'));"""

new = """const SupervisorSettingsPage = lazy(() => import('./supervisor/pages/SupervisorSettingsPage'));
const OwnerLoginPage = lazy(() => import('./owner/pages/OwnerLoginPage'));
const OwnerDashboardPage = lazy(() => import('./owner/pages/OwnerDashboardPage'));"""

count = content.count(old)
print(f"Step 1: {count} matches")
if count != 1:
    print("NOT FOUND - stop"); exit()
content = content.replace(old, new, 1)

old2 = """              {/* Catch all - redirect to home */}"""

new2 = """              {/* Owner Routes */}
              <Route path='/owner/login' element={<OwnerLoginPage />} />
              <Route path='/owner' element={<OwnerDashboardPage />} />

              {/* Catch all - redirect to home */}"""

count2 = content.count(old2)
print(f"Step 2: {count2} matches")
if count2 != 1:
    print("NOT FOUND - stop"); exit()
content = content.replace(old2, new2, 1)

open(r'.\src\App.jsx', 'w', encoding='utf-8').write(content)
print("OK - file written")
