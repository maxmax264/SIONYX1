content = open(r'.\src\App.jsx', encoding='utf-8').read()

old = "    const unsubscribeSupervisor = onSupervisorAuthChange(async (user) => {\n      setSupervisor(user ? { uid: user.uid } : null);\n      if (user) {\n        try {\n          const supervisorData = await getCurrentSupervisorData(user.uid);\n          setSupervisor(supervisorData);\n        } catch (error) {\n          console.error('Error fetching supervisor data:', error);\n        }\n      } else {\n        setSupervisor(null);\n      }\n      setSupervisorLoading(false);\n    });"

new = "    const unsubscribeSupervisor = onSupervisorAuthChange(async (user) => {\n      if (user) {\n        try {\n          const result = await getCurrentSupervisorData(user.uid);\n          setSupervisor(result?.supervisor || { uid: user.uid });\n        } catch (error) {\n          console.error('Error fetching supervisor data:', error);\n          setSupervisor({ uid: user.uid });\n        }\n      } else {\n        setSupervisor(null);\n      }\n      setSupervisorLoading(false);\n    });"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\App.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
