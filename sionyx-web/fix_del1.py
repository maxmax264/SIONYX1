content = open(r'.\src\pages\MessagesPage.jsx', encoding='utf-8').read()
old = """import {
  MessageOutlined,
  SendOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons';"""
new = """import {
  MessageOutlined,
  SendOutlined,
  UserOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  SearchOutlined,
  ReloadOutlined,
  DeleteOutlined,
} from '@ant-design/icons';"""
count = content.count(old)
print(f"icons: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
