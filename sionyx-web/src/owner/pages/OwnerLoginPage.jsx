import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Form, Input, Button, Card, Typography, Alert, App, theme } from "antd";
import { PhoneOutlined, LockOutlined, CrownOutlined } from "@ant-design/icons";
import { signInOwner } from "../services/ownerAuthService";
import { useOwnerAuthStore } from "../store/ownerAuthStore";

const { Title, Text } = Typography;

const OwnerLoginPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const setOwner = useOwnerAuthStore((s) => s.setOwner);
  const { message } = App.useApp();
  const { token } = theme.useToken();

  const onFinish = async (values) => {
    setLoading(true);
    setError(null);
    const result = await signInOwner(values.phone, values.password);
    if (result.success) {
      setOwner(result.owner);
      message.success("התחברת בהצלחה");
      navigate("/owner");
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: token.colorBgLayout, padding: 20, direction: "rtl" }}>
      <Card style={{ width: "100%", maxWidth: 450, borderRadius: 16 }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <CrownOutlined style={{ fontSize: 48, color: token.colorPrimary, marginBottom: 12 }} />
          <Title level={2} style={{ marginBottom: 8 }}>בעל מערכת</Title>
          <Text type="secondary">ממשק ניהול מרכזי</Text>
        </div>
        {error && <Alert message={error} type="error" showIcon closable onClose={() => setError(null)} style={{ marginBottom: 24 }} />}
        <Form name="owner-login" onFinish={onFinish} layout="vertical" size="large">
          <Form.Item name="phone" label="מספר טלפון" rules={[{ required: true, message: "אנא הזן מספר טלפון" }]}>
            <Input prefix={<PhoneOutlined />} placeholder="05xxxxxxxx" />
          </Form.Item>
          <Form.Item name="password" label="סיסמה" rules={[{ required: true, message: "אנא הזן סיסמה" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="סיסמה" />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            <Button type="primary" htmlType="submit" loading={loading} block style={{ height: 45, fontSize: 16 }}>
              התחבר
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default OwnerLoginPage;
