import { useEffect, useState } from "react";
import { Card, Row, Col, Typography, Statistic, Table, Tag, Button, Switch, Space, Spin, App, theme, Modal, Form, Input, InputNumber, Drawer, Tabs, Empty } from "antd";
import { BankOutlined, UserOutlined, TeamOutlined, EyeOutlined, EyeInvisibleOutlined, LaptopOutlined, ReloadOutlined, KeyOutlined, EditOutlined, SearchOutlined, PlusOutlined, WalletOutlined, ClockCircleOutlined, ShoppingOutlined } from "@ant-design/icons";
import { getAllOrgs, getAllSupervisors, connectToSupervision, disconnectFromSupervision, getOrgComputers, setAnyDeskPassword } from "../services/ownerOrgService";
import { getAllUsersAcrossOrgs, ownerAdjustUserBalance } from "../services/ownerUserService";
import { getOrganizationStats, registerOrganization } from "../../services/organizationService";
import { ref, get, set } from "firebase/database";
import { ownerAuth, ownerDatabase as database } from "../../config/firebase";
import { changeOwnerPassword, signOutOwner } from "../services/ownerAuthService";
import { useOwnerAuthStore } from "../store/ownerAuthStore";
import { useNavigate } from "react-router-dom";
import { formatTimeHebrewCompact } from "../../utils/timeFormatter";
import dayjs from "dayjs";
import OrgRegistrationModal from "../components/OrgRegistrationModal";

const { Title, Text } = Typography;

const PURCHASE_TYPE_LABELS = {
  time: "זמן",
  print: "הדפסות",
  ragil: "תשלום רגיל",
  savedCard: "כרטיס שמור",
};

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
  const [registerModalOpen, setRegisterModalOpen] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [registerForm] = Form.useForm();

  // Org detail drawer
  const [orgDetailOrg, setOrgDetailOrg] = useState(null);
  const [orgDetailVisible, setOrgDetailVisible] = useState(false);
  const [orgStats, setOrgStats] = useState(null);
  const [orgStatsLoading, setOrgStatsLoading] = useState(false);
  const [orgComputers, setOrgComputers] = useState([]);
  const [anyDeskPwEdits, setAnyDeskPwEdits] = useState({});
  const [anyDeskPwSaving, setAnyDeskPwSaving] = useState({});

  const { message } = App.useApp();
  const { token } = theme.useToken();
  const logout = useOwnerAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    await new Promise(resolve => {
      if (ownerAuth.currentUser) return resolve();
      const unsub = ownerAuth.onAuthStateChanged(u => { unsub(); resolve(); });
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

  // ── Org detail drawer ──────────────────────────────────────────
  const handleOpenOrgDetail = async (org) => {
    setOrgDetailOrg(org);
    setOrgDetailVisible(true);
    setOrgStats(null);
    setOrgComputers([]);
    setOrgStatsLoading(true);
    const [result, computersResult] = await Promise.all([
      getOrganizationStats(org.orgId, database),
      getOrgComputers(org.orgId),
    ]);
    if (result.success) setOrgStats(result.stats);
    else message.error(result.error || "נכשל בטעינת נתוני הארגון");
    if (computersResult.success) setOrgComputers(computersResult.computers);
    setOrgStatsLoading(false);
  };

  const handleCloseOrgDetail = () => {
    setOrgDetailVisible(false);
    setOrgDetailOrg(null);
    setOrgStats(null);
    setOrgComputers([]);
    setAnyDeskPwEdits({});
  };

  const handleSetAnyDeskPassword = async (computerId) => {
    const password = (anyDeskPwEdits[computerId] || "").trim();
    if (!password) { message.warning("הזן סיסמה חדשה"); return; }
    setAnyDeskPwSaving((prev) => ({ ...prev, [computerId]: true }));
    const result = await setAnyDeskPassword(orgDetailOrg.orgId, computerId, password);
    if (result.success) {
      message.success("סיסמת AnyDesk עודכנה - הקיוסק יעדכן תוך שניות");
      setOrgComputers((prev) => prev.map((c) => c.computerId === computerId
        ? { ...c, anydesk: { ...(c.anydesk || {}), password } }
        : c));
      setAnyDeskPwEdits((prev) => ({ ...prev, [computerId]: "" }));
    } else {
      message.error(result.error || "נכשל בעדכון הסיסמה");
    }
    setAnyDeskPwSaving((prev) => ({ ...prev, [computerId]: false }));
  };

  const handleAddOrg = () => {
    setRegisterModalOpen(true);
  };

  const handleCloseRegisterModal = () => {
    setRegisterModalOpen(false);
    registerForm.resetFields();
  };

  const handleRegisterOrgSubmit = async (values) => {
    setRegistering(true);
    try {
      const result = await registerOrganization(values);
      if (result.success) {
        message.success("הארגון נוצר בהצלחה");
        registerForm.resetFields();
        setRegisterModalOpen(false);
        load();
      } else {
        message.error(result.error || "שגיאה ביצירת הארגון");
      }
    } catch {
      message.error("שגיאה ביצירת הארגון");
    } finally {
      setRegistering(false);
    }
  };

  const totalUsers = orgs.reduce((s, o) => s + o.userCount, 0);
  const totalActive = orgs.reduce((s, o) => s + o.activeUsers, 0);
  const totalComputers = orgs.reduce((s, o) => s + o.computerCount, 0);
  const supervised = orgs.filter((o) => o.isSupervised).length;

  // Slim, tidy org table - detailed settings moved into the org detail drawer
  const columns = [
    {
      title: "ארגון",
      dataIndex: "name",
      key: "name",
      render: (v, r) => (
        <Button type="link" style={{ padding: 0, fontWeight: 600 }} onClick={() => handleOpenOrgDetail(r)}>
          {v || r.orgId}
        </Button>
      ),
    },
    { title: "סטטוס", dataIndex: "status", key: "status", render: (v) => <Tag color={v === "active" ? "green" : "red"}>{v === "active" ? "פעיל" : v}</Tag> },
    { title: "משתמשים", dataIndex: "userCount", key: "userCount", render: (v) => <><UserOutlined /> {v}</> },
    { title: "פעילים", dataIndex: "activeUsers", key: "activeUsers", render: (v) => <Tag color={v > 0 ? "green" : "default"}>{v}</Tag> },
    { title: "מחשבים", dataIndex: "computerCount", key: "computerCount", render: (v) => <><LaptopOutlined /> {v}</> },
    { title: "פיקוח", key: "supervision", render: (_, r) => <Tag icon={r.isSupervised ? <EyeOutlined /> : <EyeInvisibleOutlined />} color={r.isSupervised ? "blue" : "default"}>{r.isSupervised ? "מפוקח" : "לא מפוקח"}</Tag> },
    {
      title: "",
      key: "open",
      render: (_, r) => <Button size="small" onClick={() => handleOpenOrgDetail(r)}>פרטים מלאים</Button>,
    },
  ];

  const userColumns = [
    {
      title: "ארגון",
      dataIndex: "orgName",
      key: "orgName",
      render: (v) => <Tag>{v}</Tag>,
      sorter: (a, b) => (a.orgName || "").localeCompare(b.orgName || ""),
      defaultSortOrder: "ascend",
      filters: orgs.map((o) => ({ text: o.name || o.orgId, value: o.orgId })),
      onFilter: (value, record) => record.orgId === value,
    },
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

  // Same as userColumns, minus the org tag column - used inside the org detail drawer
  const orgUserColumns = userColumns.filter((c) => c.key !== "orgName");

  const purchaseColumns = [
    {
      title: "תאריך",
      dataIndex: "createdAt",
      key: "createdAt",
      render: (v) => (v ? dayjs(v).format("D/M/YYYY HH:mm") : "—"),
      sorter: (a, b) => (a.createdAt || 0) - (b.createdAt || 0),
      defaultSortOrder: "descend",
    },
    { title: "סכום", dataIndex: "amount", key: "amount", render: (v) => v ? `₪${v}` : "—" },
    { title: "חבילה", dataIndex: "packageName", key: "packageName", render: (v) => v || "—" },
    { title: "סוג", dataIndex: "type", key: "type", render: (v) => PURCHASE_TYPE_LABELS[v] || v || "—" },
    { title: "דקות", dataIndex: "minutes", key: "minutes", render: (v) => v || "—" },
    {
      title: "סטטוס",
      dataIndex: "status",
      key: "status",
      render: (v) => <Tag color={v === "completed" ? "green" : v === "pending" ? "orange" : "red"}>{v || "—"}</Tag>,
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

  const orgDetailUsers = orgDetailOrg ? allUsers.filter((u) => u.orgId === orgDetailOrg.orgId) : [];
  const orgDetailSettings = orgDetailOrg ? (orgSettings[orgDetailOrg.orgId] || {}) : {};

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
      <Card
        title="כל הארגונים"
        size="small"
        style={{ marginBottom: 24 }}
        extra={<Button type="primary" icon={<PlusOutlined />} onClick={handleAddOrg}>ארגון חדש</Button>}
      >
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

      {/* Org detail drawer - everything about one org, organized into categories */}
      <Drawer
        title={orgDetailOrg ? (orgDetailOrg.name || orgDetailOrg.orgId) : ""}
        placement="right"
        width={720}
        open={orgDetailVisible}
        onClose={handleCloseOrgDetail}
      >
        {orgStatsLoading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: 60 }}><Spin size="large" /></div>
        ) : (
          <Tabs
            defaultActiveKey="overview"
            tabBarGutter={28}
            items={[
              {
                key: "overview",
                label: "סקירה",
                children: (
                  <div style={{ paddingTop: 8 }}>
                    <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
                      <Col span={12}>
                        <Card size="small" bodyStyle={{ padding: 16 }}>
                          <Statistic title="סה״כ הכנסות" value={orgStats?.totalRevenue || 0} prefix={<WalletOutlined />} suffix="₪" valueStyle={{ color: token.colorSuccess }} />
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card size="small" bodyStyle={{ padding: 16 }}>
                          <Statistic title="מספר רכישות" value={orgStats?.purchasesCount || 0} prefix={<ShoppingOutlined />} />
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card size="small" bodyStyle={{ padding: 16 }}>
                          <Statistic title="סה״כ דקות שנרכשו" value={orgStats?.totalTimeMinutes || 0} prefix={<ClockCircleOutlined />} />
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card size="small" bodyStyle={{ padding: 16 }}>
                          <Statistic title="משתמשים" value={orgDetailOrg?.userCount || 0} prefix={<UserOutlined />} />
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card size="small" bodyStyle={{ padding: 16 }}>
                          <Statistic title="פעילים עכשיו" value={orgDetailOrg?.activeUsers || 0} prefix={<TeamOutlined />} />
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card size="small" bodyStyle={{ padding: 16 }}>
                          <Statistic title="מחשבים" value={orgDetailOrg?.computerCount || 0} prefix={<LaptopOutlined />} />
                        </Card>
                      </Col>
                    </Row>
                    <Card size="small" title="פרטים כלליים" style={{ marginTop: 4 }} bodyStyle={{ padding: 16 }}>
                      <Space direction="vertical" size={10}>
                        <Text>סטטוס: <Tag color={orgDetailOrg?.status === "active" ? "green" : "red"}>{orgDetailOrg?.status === "active" ? "פעיל" : orgDetailOrg?.status}</Tag></Text>
                        <Text>נוצר בתאריך: {orgDetailOrg?.createdAt ? dayjs(orgDetailOrg.createdAt).format("D/M/YYYY HH:mm") : "לא זמין"}</Text>
                        <Text>פיקוח: {orgDetailOrg?.isSupervised ? "מפוקח" : "לא מפוקח"}</Text>
                      </Space>
                    </Card>
                  </div>
                ),
              },
              {
                key: "purchases",
                label: "תשלומים והכנסות",
                children: (
                  <Table
                    dataSource={orgStats?.purchases || []}
                    columns={purchaseColumns}
                    rowKey={(r, i) => r.id || i}
                    pagination={{ pageSize: 10, showSizeChanger: false }}
                    size="small"
                    locale={{ emptyText: <Empty description="אין רכישות" /> }}
                  />
                ),
              },
              {
                key: "users",
                label: `משתמשים (${orgDetailUsers.length})`,
                children: (
                  <Table
                    dataSource={orgDetailUsers}
                    columns={orgUserColumns}
                    rowKey={(r) => r.uid}
                    pagination={{ pageSize: 10, showSizeChanger: false }}
                    size="small"
                  />
                ),
              },
              {
                key: "remoteControl",
                label: `מחשבים ושליטה מרחוק (${orgComputers.length})`,
                children: (
                  <Space direction="vertical" size={16} style={{ width: "100%" }}>
                    {orgComputers.length === 0 ? (
                      <Empty description="אין מחשבים רשומים" />
                    ) : orgComputers.map((c) => (
                      <Card
                        key={c.computerId}
                        size="small"
                        title={<Space><LaptopOutlined />{c.computerName}<Tag color={c.isActive ? "green" : "default"}>{c.isActive ? "פעיל" : "לא פעיל"}</Tag></Space>}
                      >
                        <Row gutter={[16, 12]}>
                          <Col span={12}>
                            <Text type="secondary">RustDesk (סיסמת מנהל הארגון)</Text>
                            <div>ID: <Text copyable>{c.rustdesk?.id || "—"}</Text></div>
                            <div>סיסמה: <Text copyable style={{ fontFamily: "monospace" }}>{c.rustdesk?.password || "—"}</Text></div>
                          </Col>
                          <Col span={12}>
                            <Text type="secondary">AnyDesk (המסטר בלבד)</Text>
                            <div>ID: <Text copyable>{c.anydesk?.id || "—"}</Text></div>
                            <div>סיסמה: <Text copyable style={{ fontFamily: "monospace" }}>{c.anydesk?.password || "—"}</Text></div>
                          </Col>
                        </Row>
                        <Space.Compact style={{ marginTop: 12, width: "100%" }}>
                          <Input
                            placeholder="סיסמת AnyDesk חדשה"
                            value={anyDeskPwEdits[c.computerId] || ""}
                            onChange={(e) => setAnyDeskPwEdits((prev) => ({ ...prev, [c.computerId]: e.target.value }))}
                            onPressEnter={() => handleSetAnyDeskPassword(c.computerId)}
                          />
                          <Button
                            type="primary"
                            loading={!!anyDeskPwSaving[c.computerId]}
                            onClick={() => handleSetAnyDeskPassword(c.computerId)}
                          >
                            עדכן
                          </Button>
                        </Space.Compact>
                      </Card>
                    ))}
                  </Space>
                ),
              },
              {
                key: "settings",
                label: "הגדרות",
                children: orgDetailOrg && (
                  <Space direction="vertical" size={20} style={{ width: "100%" }}>
                    <Card size="small" title="פיקוח">
                      <Space>
                        <Switch
                          checked={orgDetailOrg.isSupervised}
                          checkedChildren={<EyeOutlined />}
                          unCheckedChildren={<EyeInvisibleOutlined />}
                          onChange={async () => {
                            await handleSupervisionToggle(orgDetailOrg.orgId, orgDetailOrg.isSupervised, orgDetailOrg.supervisedBy);
                            setOrgDetailOrg((prev) => prev ? { ...prev, isSupervised: !prev.isSupervised } : prev);
                          }}
                        />
                        <Text type="secondary">{orgDetailOrg.isSupervised ? "מפוקח" : "לא מפוקח"}</Text>
                      </Space>
                    </Card>
                    <Card size="small" title="תמונת רקע">
                      <Space direction="vertical" size={10}>
                        <Space size={8}>
                          <Switch
                            checked={orgDetailSettings.allowFileUpload !== false}
                            loading={!!savingOrgSettings[orgDetailOrg.orgId + "allowFileUpload"]}
                            onChange={(v) => handleSaveOrgSetting(orgDetailOrg.orgId, "allowFileUpload", v)}
                          />
                          <Text>אפשר העלאת קובץ</Text>
                        </Space>
                        <Space size={8}>
                          <InputNumber
                            min={0}
                            value={orgDetailSettings.maxImageSizeMB || 0}
                            onChange={(v) => setOrgSettings((prev) => ({ ...prev, [orgDetailOrg.orgId]: { ...(prev[orgDetailOrg.orgId] || {}), maxImageSizeMB: v || 0 } }))}
                            onBlur={() => handleSaveOrgSetting(orgDetailOrg.orgId, "maxImageSizeMB", orgSettings[orgDetailOrg.orgId]?.maxImageSizeMB || 0)}
                          />
                          <Text>MB מקסימום לקובץ</Text>
                        </Space>
                      </Space>
                    </Card>
                  </Space>
                ),
              },
            ]}
          />
        )}
      </Drawer>

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
      <OrgRegistrationModal
        open={registerModalOpen}
        onClose={handleCloseRegisterModal}
        onSubmit={handleRegisterOrgSubmit}
        loading={registering}
        form={registerForm}
      />
    </div>
  );
};

export default OwnerDashboardPage;
