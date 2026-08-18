import { useEffect, useState } from "react";
import { Card, Row, Col, Typography, Statistic, Table, Tag, Button, Switch, Space, Spin, App, theme, Modal, Form, Input, InputNumber } from "antd";
import { BankOutlined, UserOutlined, TeamOutlined, EyeOutlined, EyeInvisibleOutlined, LaptopOutlined, ReloadOutlined, KeyOutlined, PictureOutlined, EditOutlined, SearchOutlined } from "@ant-design/icons";
import { getAllOrgs, getAllSupervisors, connectToSupervision, disconnectFromSupervision } from "../services/ownerOrgService";
import { getAllUsersAcrossOrgs, ownerAdjustUserBalance } from "../services/ownerUserService";
import { ref, get, set } from "firebase/database";
import { database } from "../../config/firebase";
import { changeOwnerPassword, signOutOwner } from "../services/ownerAuthService";
import { useOwnerAuthStore } from "../store/ownerAuthStore";
import { useNavigate } from "react-router-dom";
import { formatTimeHebrewCompact } from "../../utils/timeFormatter";

const { Title, Text } = Typography;

const OwnerDashboardPage = () => {
  const [orgs, setOrgs] = useState([]);
  const [supervisors, setSupervisors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [passwordModal, setPasswordModal] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [maxImageSizeMB, setMaxImageSizeMB] = useState(0);
  const [savingSize, setSavingSize] = useState(false);
  const [orgSettings, setOrgSettings] = useState({});
  const [savingOrgSettings, setSavingOrgSettings] = useState({});
  const [allUsers, setAllUsers] = useState([]);
  const [userSearch, setUserSearch] = useState("");
  const [adjustingUser, setAdjustingUser] = useState(null);
  const [adjustBalanceVisible, setAdjustBalanceVisible] = useState(false);
  const [adjusting, setAdjusting] = useState(false);
  const [balanceForm] = Form.useForm();
  const { message } = App.useApp();
  const { token } = theme.useToken();
  const logout = useOwnerAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    const { getAuth } = await import("firebase/auth");
    const auth = getAuth();
    await new Promise(resolve => {
      if (auth.currentUser) return resolve();
      const unsub = auth.onAuthStateChanged(u => { unsub(); resolve(); });
    });
    const [orgsRes, supRes, usersRes] = await Promise.all([getAllOrgs(), getAllSupervisors(), getAllUsersAcrossOrgs()]);
    try {
      const sysSnap = await get(ref(database, "systemSettings/maxImageSizeMB"));
      if (sysSnap.exists()) setMaxImageSizeMB(sysSnap.val());
      const orgSettingsSnap = await get(ref(database, "systemSettings/orgs"));
      if (orgSettingsSnap.exists()) setOrgSettings(orgSettingsSnap.val() || {});
    } catch (e) {
      console.warn("systemSettings read failed:", e.message);
    }
    if (orgsRes.success) setOrgs(orgsRes.orgs);
    if (supRes.success) setSupervisors(supRes.supervisors);
    if (usersRes.success) setAllUsers(usersRes.users);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleSupervisionToggle = async (orgId, isSupervised, supervisedBy) => {
    if (supervisors.length === 0) { message.warning("אין supervisors במערכת"); return; }
    const supUid = supervisedBy || supervisors[0].uid;
    const result = isSupervised
      ? await disconnectFromSupervision(orgId, supUid)
      : await connectToSupervision(orgId, supUid);
    if (result.success) {
      message.success(isSupervised ? "נותק מפיקוח" : "חובר לפיקוח");
      load();
    } else {
      message.error(result.error);
    }
  };

  const handleChangePassword = async (values) => {
    setPasswordLoading(true);
    const result = await changeOwnerPassword(values.password);
    if (result.success) {
      message.success("סיסמה שונתה בהצלחה");
      setPasswordModal(false);
      form.resetFields();
    } else {
      message.error(result.error);
    }
    setPasswordLoading(false);
  };

  const handleSaveOrgSetting = async (orgId, field, value) => {
    setSavingOrgSettings(prev => ({ ...prev, [orgId + field]: true }));
    await set(ref(database, `systemSettings/orgs/${orgId}/${field}`), value);
    setOrgSettings(prev => ({ ...prev, [orgId]: { ...(prev[orgId] || {}), [field]: value } }));
    message.success("הגדרה נשמרה");
    setSavingOrgSettings(prev => ({ ...prev, [orgId + field]: false }));
  };
  const handleSaveMaxSize = async () => {
    setSavingSize(true);
    await set(ref(database, "systemSettings/maxImageSizeMB"), maxImageSizeMB || 0);
    message.success("הגדרה נשמרה");
    setSavingSize(false);
  };
  const handleLogout = async () => {
    await signOutOwner();
    logout();
    navigate("/owner/login");
  };

  const handleOpenAdjustBalance = (record) => {
    setAdjustingUser(record);
    balanceForm.setFieldsValue({
      minutes: Math.floor((record.remainingTime || 0) / 60),
      prints: record.printBalance || 0,
    });
    setAdjustBalanceVisible(true);
  };

  const handleBalanceSubmit = async () => {
    try {
      const values = await balanceForm.validateFields();
      setAdjusting(true);
      const currentTimeMinutes = Math.floor((adjustingUser.remainingTime || 0) / 60);
      const currentPrints = adjustingUser.printBalance || 0;
      const adjustments = {
        timeSeconds: (values.minutes - currentTimeMinutes) * 60,
        prints: values.prints - currentPrints,
      };
      const result = await ownerAdjustUserBalance(adjustingUser.orgId, adjustingUser.uid, adjustments);
      if (result.success) {
        message.success("יתרת המשתמש עודכנה בהצלחה");
        setAdjustBalanceVisible(false);
        balanceForm.resetFields();
        setAllUsers((prev) => prev.map((u) =>
          u.uid === adjustingUser.uid && u.orgId === adjustingUser.orgId
            ? { ...u, remainingTime: result.newBalance.remainingTime, printBalance: result.newBalance.printBalance }
            : u
        ));
      } else {
        message.error(result.error || "נכשל בעדכון היתרה");
      }
    } catch (e) {
      // validation error, ignore
    } finally {
      setAdjusting(false);
    }
  };

  const totalUsers = orgs.reduce((s, o) => s + o.userCount, 0);
  const totalActive = orgs.reduce((s, o) => s + o.activeUsers, 0);
  const totalComputers = orgs.reduce((s, o) => s + o.computerCount, 0);
  const supervised = orgs.filter((o) => o.isSupervised).length;

  const columns = [
    { title: "ארגון", dataIndex: "name", key: "name", render: (v, r) => <Text strong>{v || r.orgId}</Text> },
    { title: "משתמשים", dataIndex: "userCount", key: "userCount", render: (v) => <><UserOutlined /> {v}</> },
    { title: "פעילים", dataIndex: "activeUsers", key: "activeUsers", render: (v) => <Tag color={v > 0 ? "green" : "default"}>{v}</Tag> },
    { title: "מחשבים", dataIndex: "computerCount", key: "computerCount", render: (v) => <><LaptopOutlined /> {v}</> },
    { title: "סטטוס", dataIndex: "status", key: "status", render: (v) => <Tag color={v === "active" ? "green" : "red"}>{v === "active" ? "פעיל" : v}</Tag> },
    {
      title: "תמונת רקע",
      key: "bgSettings",
      render: (_, r) => {
        const s = orgSettings[r.orgId] || {};
        const allowUpload = s.allowFileUpload !== false;
        const maxMB = s.maxImageSizeMB || 0;
        return (
          <Space direction="vertical" size={2}>
            <Space size={4}>
              <Switch size="small" checked={allowUpload} loading={!!savingOrgSettings[r.orgId + "allowFileUpload"]} onChange={v => handleSaveOrgSetting(r.orgId, "allowFileUpload", v)} />
              <Text style={{ fontSize: 11 }}>העלאת קובץ</Text>
            </Space>
            <Space size={4}>
              <InputNumber size="small" min={0} value={maxMB} style={{ width: 60 }} onChange={v => setOrgSettings(prev => ({ ...prev, [r.orgId]: { ...(prev[r.orgId] || {}), maxImageSizeMB: v || 0 } }))} onBlur={() => handleSaveOrgSetting(r.orgId, "maxImageSizeMB", orgSettings[r.orgId]?.maxImageSizeMB || 0)} />
              <Text style={{ fontSize: 11 }}>MB</Text>
            </Space>
          </Space>
        );
      },
    },
    {
      title: "פיקוח",
      key: "supervision",
      render: (_, r) => (
        <Space>
          <Switch
            checked={r.isSupervised}
            checkedChildren={<EyeOutlined />}
            unCheckedChildren={<EyeInvisibleOutlined />}
            onChange={() => handleSupervisionToggle(r.orgId, r.isSupervised, r.supervisedBy)}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>{r.isSupervised ? "מפוקח" : "לא מפוקח"}</Text>
        </Space>
      ),
    },
  ];

  const userColumns = [
    { title: "ארגון", dataIndex: "orgName", key: "orgName", render: (v) => <Tag>{v}</Tag> },
    { title: "שם", key: "name", render: (_, r) => r.name || r.displayName || r.phoneNumber || r.uid },
    { title: "טלפון", dataIndex: "phoneNumber", key: "phoneNumber" },
    { title: "זמן נותר", dataIndex: "remainingTime", key: "remainingTime", render: (v) => formatTimeHebrewCompact(v || 0) },
    { title: "תקציב הדפסות", dataIndex: "printBalance", key: "printBalance", render: (v) => `₪${v || 0}` },
    { title: "פעיל", dataIndex: "isSessionActive", key: "isSessionActive", render: (v) => <Tag color={v ? "green" : "default"}>{v ? "כן" : "לא"}</Tag> },
    {
      title: "פעולות",
      key: "actions",
      render: (_, r) => (
        <Button size="small" icon={<EditOutlined />} onClick={() => handleOpenAdjustBalance(r)}>עדכן יתרה</Button>
      ),
    },
  ];

  const filteredUsers = allUsers.filter((u) => {
    if (!userSearch.trim()) return true;
    const q = userSearch.trim().toLowerCase();
    return (u.name || "").toLowerCase().includes(q) ||
      (u.displayName || "").toLowerCase().includes(q) ||
      (u.phoneNumber || "").includes(q) ||
      (u.orgName || "").toLowerCase().includes(q);
  });

  if (loading) return <div style={{ display: "flex", justifyContent: "center", padding: 80 }}><Spin size="large" /></div>;

  return (
    <div style={{ direction: "rtl", padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>ממשק בעל מערכת</Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={load}>רענן</Button>
          <Button icon={<KeyOutlined />} onClick={() => setPasswordModal(true)}>שנה סיסמה</Button>
          <Button danger onClick={handleLogout}>התנתק</Button>
        </Space>
      </div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {[
          { title: "ארגונים", value: orgs.length, icon: <BankOutlined />, color: token.colorPrimary },
          { title: "משתמשים", value: totalUsers, icon: <UserOutlined />, color: token.colorSuccess },
          { title: "פעילים עכשיו", value: totalActive, icon: <TeamOutlined />, color: token.colorInfo },
          { title: "מחשבים", value: totalComputers, icon: <LaptopOutlined />, color: token.colorWarning },
          { title: "תחת פיקוח", value: supervised, icon: <EyeOutlined />, color: token.colorError },
        ].map((s, i) => (
          <Col xs={12} sm={8} md={4} key={i}>
            <Card size="small" style={{ borderTop: `3px solid ${s.color}` }}>
              <Statistic title={<Text type="secondary" style={{ fontSize: 12 }}>{s.title}</Text>} value={s.value} prefix={s.icon} valueStyle={{ fontSize: 22 }} />
            </Card>
          </Col>
        ))}
      </Row>
      <Card title="כל הארגונים" size="small" style={{ marginBottom: 24 }}>
        <Table dataSource={orgs} columns={columns} rowKey="orgId" pagination={false} size="small" />
      </Card>
      <Card
        title={`כל המשתמשים (${allUsers.length})`}
        size="small"
        extra={
          <Input
            placeholder="חיפוש לפי שם, טלפון או ארגון"
            prefix={<SearchOutlined />}
            value={userSearch}
            onChange={(e) => setUserSearch(e.target.value)}
            style={{ width: 260 }}
            allowClear
          />
        }
      >
        <Table
          dataSource={filteredUsers}
          columns={userColumns}
          rowKey={(r) => `${r.orgId}-${r.uid}`}
          pagination={{ pageSize: 20, showSizeChanger: false }}
          size="small"
        />
      </Card>
      <Modal
        title={adjustingUser ? `עדכון יתרה - ${adjustingUser.name || adjustingUser.phoneNumber || adjustingUser.uid} (${adjustingUser.orgName})` : "עדכון יתרה"}
        open={adjustBalanceVisible}
        onCancel={() => setAdjustBalanceVisible(false)}
        footer={null}
      >
        <Form form={balanceForm} onFinish={handleBalanceSubmit} layout="vertical">
          <Form.Item name="minutes" label="זמן נותר (דקות)" rules={[{ required: true, message: "הזן ערך" }]}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item name="prints" label="תקציב הדפסות (₪)" rules={[{ required: true, message: "הזן ערך" }]}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={adjusting} block>שמור יתרה</Button>
        </Form>
      </Modal>
      <Modal title="שינוי סיסמה" open={passwordModal} onCancel={() => setPasswordModal(false)} footer={null}>
        <Form form={form} onFinish={handleChangePassword} layout="vertical">
          <Form.Item name="password" label="סיסמה חדשה" rules={[{ required: true, message: "הזן סיסמה" }, { min: 6, message: "לפחות 6 תווים" }]}>
            <Input.Password placeholder="סיסמה חדשה" />
          </Form.Item>
          <Form.Item name="confirm" label="אישור סיסמה" rules={[{ required: true }, ({ getFieldValue }) => ({ validator(_, v) { return v && getFieldValue("password") === v ? Promise.resolve() : Promise.reject("הסיסמאות לא תואמות"); } })]}>
            <Input.Password placeholder="אשר סיסמה" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={passwordLoading} block>שמור סיסמה</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default OwnerDashboardPage;
