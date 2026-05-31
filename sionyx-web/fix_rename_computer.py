content = open(r'.\src\pages\ComputersPage.jsx', encoding='utf-8').read()

# Step 1: Add EditOutlined to imports
old1 = "  DeleteOutlined,\n  ReloadOutlined,"
new1 = "  DeleteOutlined,\n  EditOutlined,\n  ReloadOutlined,"
count1 = content.count(old1)
print(f"Step 1: {count1} matches")
if count1 == 1:
    content = content.replace(old1, new1, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND - stop"); exit()

# Step 2: Add updateComputer to imports
old2 = "  deleteComputer,\n  deriveFromComputersAndUsers,"
new2 = "  deleteComputer,\n  updateComputer,\n  deriveFromComputersAndUsers,"
count2 = content.count(old2)
print(f"Step 2: {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    print("Step 2: OK")
else:
    print("Step 2: NOT FOUND - stop"); exit()

# Step 3: Add rename state and Modal/Input imports
old3 = "import {\n  Card,\n  Tabs,\n  Statistic,\n  Row,\n  Col,\n  Tag,\n  Button,\n  Space,\n  Typography,\n  Skeleton,\n  Modal,\n  message,\n  Badge,\n} from 'antd';"
new3 = "import {\n  Card,\n  Tabs,\n  Statistic,\n  Row,\n  Col,\n  Tag,\n  Button,\n  Space,\n  Typography,\n  Skeleton,\n  Modal,\n  message,\n  Badge,\n  Input,\n} from 'antd';"
count3 = content.count(old3)
print(f"Step 3: {count3} matches")
if count3 == 1:
    content = content.replace(old3, new3, 1)
    print("Step 3: OK")
else:
    print("Step 3: NOT FOUND - stop"); exit()

# Step 4: Add rename state variables after actionLoading state
old4 = "  const [actionLoading, setActionLoading] = useState({});\n\n  const orgId = useOrgId();"
new4 = "  const [actionLoading, setActionLoading] = useState({});\n  const [renameModal, setRenameModal] = useState(false);\n  const [renameComputer, setRenameComputer] = useState(null);\n  const [renameValue, setRenameValue] = useState('');\n  const [renameLoading, setRenameLoading] = useState(false);\n\n  const orgId = useOrgId();"
count4 = content.count(old4)
print(f"Step 4: {count4} matches")
if count4 == 1:
    content = content.replace(old4, new4, 1)
    print("Step 4: OK")
else:
    print("Step 4: NOT FOUND - stop"); exit()

# Step 5: Add handleRename function after handleDeleteComputer
old5 = "  const formatDuration = seconds => {"
new5 = """  const handleRenameComputer = (computer) => {
    setRenameComputer(computer);
    setRenameValue(computer.computerName || '');
    setRenameModal(true);
  };

  const handleRenameConfirm = async () => {
    if (!renameValue.trim()) { message.warning('נא להזין שם מחשב'); return; }
    setRenameLoading(true);
    try {
      const computerId = renameComputer.id || renameComputer.computerId;
      const result = await updateComputer(computerId, { computerName: renameValue.trim() });
      if (result.success) {
        message.success('שם המחשב עודכן בהצלחה');
        setRenameModal(false);
      } else {
        message.error('שגיאה בעדכון שם המחשב: ' + result.error);
      }
    } catch (err) {
      message.error('שגיאה: ' + err.message);
    } finally {
      setRenameLoading(false);
    }
  };

  const formatDuration = seconds => {"""
count5 = content.count(old5)
print(f"Step 5: {count5} matches")
if count5 == 1:
    content = content.replace(old5, new5, 1)
    print("Step 5: OK")
else:
    print("Step 5: NOT FOUND - stop"); exit()

# Step 6: Add edit button to AllComputerCard
old6 = """          {/* Delete Button */}
          <Col>
            <Button
              type='text'
              danger
              size='small'
              icon={<DeleteOutlined />}
              loading={actionLoading[`delete-${computerId}`]}
              onClick={() => handleDeleteComputer(computerId)}
            />
          </Col>"""
new6 = """          {/* Actions */}
          <Col>
            <Space>
              <Button
                type='text'
                size='small'
                icon={<EditOutlined />}
                onClick={() => handleRenameComputer(computer)}
                title='שנה שם'
              />
              <Button
                type='text'
                danger
                size='small'
                icon={<DeleteOutlined />}
                loading={actionLoading[`delete-${computerId}`]}
                onClick={() => handleDeleteComputer(computerId)}
              />
            </Space>
          </Col>"""
count6 = content.count(old6)
print(f"Step 6: {count6} matches")
if count6 == 1:
    content = content.replace(old6, new6, 1)
    print("Step 6: OK")
else:
    print("Step 6: NOT FOUND - stop"); exit()

# Step 7: Add Modal before closing return
old7 = "export default ComputersPage;"
new7 = """      {/* Rename Modal */}
      <Modal
        title="שינוי שם מחשב"
        open={renameModal}
        onOk={handleRenameConfirm}
        onCancel={() => setRenameModal(false)}
        okText="שמור"
        cancelText="ביטול"
        confirmLoading={renameLoading}
      >
        <div style={{ direction: 'rtl', marginTop: 16 }}>
          <p>שם נוכחי: <strong>{renameComputer?.computerName}</strong></p>
          <Input
            value={renameValue}
            onChange={e => setRenameValue(e.target.value)}
            placeholder="הזן שם חדש למחשב"
            onPressEnter={handleRenameConfirm}
            autoFocus
          />
        </div>
      </Modal>

export default ComputersPage;"""

# Need to add modal inside the component return, before export
old7b = "  return (\n    <motion.div"
new7b = """  return (
    <>
    <Modal
      title="שינוי שם מחשב"
      open={renameModal}
      onOk={handleRenameConfirm}
      onCancel={() => setRenameModal(false)}
      okText="שמור"
      cancelText="ביטול"
      confirmLoading={renameLoading}
    >
      <div style={{ direction: 'rtl', marginTop: 16 }}>
        <p>שם נוכחי: <strong>{renameComputer?.computerName}</strong></p>
        <Input
          value={renameValue}
          onChange={e => setRenameValue(e.target.value)}
          placeholder="הזן שם חדש למחשב"
          onPressEnter={handleRenameConfirm}
          autoFocus
        />
      </div>
    </Modal>
    <motion.div"""
count7 = content.count(old7b)
print(f"Step 7a: {count7} matches")
if count7 == 1:
    content = content.replace(old7b, new7b, 1)
    print("Step 7a: OK")
else:
    print("Step 7a: NOT FOUND - stop"); exit()

# Close the fragment
old8 = "    </motion.div>\n  );\n};\n\nexport default ComputersPage;"
new8 = "    </motion.div>\n    </>\n  );\n};\n\nexport default ComputersPage;"
count8 = content.count(old8)
print(f"Step 7b: {count8} matches")
if count8 == 1:
    content = content.replace(old8, new8, 1)
    open(r'.\src\pages\ComputersPage.jsx', 'w', encoding='utf-8').write(content)
    print("Step 7b: OK - file written")
else:
    print("Step 7b: NOT FOUND - stop")
