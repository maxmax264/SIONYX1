content = open(r'.\installer\OrgNameDlg.wxs', encoding='utf-8').read()

old = """      <Control Id="OrgInfo" Type="Text" X="20" Y="114" Width="330" Height="50"
               Text="{\OrgFont_Info}This identifies your organization in the SIONYX system.&#13;&#10;&#13;&#10;Use lowercase letters, numbers, and hyphens only.&#13;&#10;Examples: 'my-gaming-center', 'tech-hub'" />

      <!-- Bottom bar -->"""

new = """      <Control Id="OrgInfo" Type="Text" X="20" Y="114" Width="330" Height="30"
               Text="{\OrgFont_Info}This identifies your organization in the SIONYX system.&#13;&#10;Use lowercase letters, numbers, and hyphens only." />

      <Control Id="PcLabel" Type="Text" X="20" Y="152" Width="330" Height="18"
               Text="{\OrgFont_Label}Computer Name (optional):" />
      <Control Id="PcEdit" Type="Edit" X="20" Y="174" Width="330" Height="22"
               Property="COMPUTERNAME_CUSTOM" />
      <Control Id="PcInfo" Type="Text" X="20" Y="200" Width="330" Height="20"
               Text="{\OrgFont_Info}A friendly name for this PC (e.g. 'PC-1', 'Room-A'). Leave blank to use the Windows hostname." />

      <!-- Bottom bar -->"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\OrgNameDlg.wxs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
