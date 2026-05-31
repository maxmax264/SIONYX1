content = r"""import { useEffect, useState } from "react";
import { Card, Row, Col, Typography, Statistic, Table, Tag, Button, Switch, Space, Spin, App, theme, Modal, Form, Input } from "antd";
import { BankOutlined, UserOutlined, TeamOutlined, EyeOutlined, EyeInvisibleOutlined, LaptopOutlined, ReloadOutlined, KeyOutlined } from "@ant-design/icons";
import { getAllOrgs, getAllSupervisors, connectToSupervision, disconnectFromSupervision } from "../services/ownerOrgService";
import { changeOwnerPassword, signOutOwner } from "../services/ownerAuthService";
import { useOwnerAuthStore } from "../store/ownerAuthStore";
import { useNavigate } from "react-router-dom";

const { Title, Text } = Typography;

const OwnerDashboardPage = () => {
  const [orgs, setOrgs] = useState([]);
  const [supervisors, setSupervisors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [passwordModal, setPasswordModal] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const { message } = App.useApp();
  const { token } = theme.useToken();
  const logout = useOwnerAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    const [orgsRes, supRes] = await Promise.all([getAllOrgs(), getAllSupervisors()]);
    if (orgsRes.success) setOrgs(orgsRes.orgs);
    if (supRes.success) setSupervisors(supRes.supervisors);
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

  const handleLogout = async () => {
    await signOutOwner();
    logout();
    navigate("/owner/login");
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
      <Card title="כל הארגונים" size="small">
        <Table dataSource={orgs} columns={columns} rowKey="orgId" pagination={false} size="small" />
      </Card>
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
"""
open(r'.\src\owner\pages\OwnerDashboardPage.jsx', 'w', encoding='utf-8').write(content)
print("OK")
