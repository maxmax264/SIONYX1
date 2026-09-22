import { useEffect, useState } from "react";
import { Radio, Space, Typography, Alert, Spin, App } from "antd";
import { CloudServerOutlined, DesktopOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { getFailoverSettings, updateFailoverMode } from "../services/ownerFailoverService";

const { Text, Paragraph } = Typography;

// Manual override for the SIONYX/Render <-> local-PC failover (see the
// plan doc). Read by both the kiosk (ServerResolver.cs) and this dashboard
// (serverResolver.js), polled every ~20s, so a change here takes effect
// within about 20-40 seconds everywhere without redeploying anything.
const OPTIONS = [
  {
    value: "auto",
    icon: <ThunderboltOutlined />,
    label: "אוטומטי (מומלץ)",
    description: "המנגנון בודק בעצמו כל 20 שניות אם המחשב הראשי זמין, ועובר לרנדר/חזרה לבד.",
  },
  {
    value: "forceLocal",
    icon: <DesktopOutlined />,
    label: "תמיד המחשב הראשי",
    description: "מתעלם מבדיקת הבריאות ומכריח שימוש במחשב הראשי בלבד, גם אם הוא נראה לא זמין.",
  },
  {
    value: "forceRender",
    icon: <CloudServerOutlined />,
    label: "תמיד Render",
    description: "מתעלם מבדיקת הבריאות ומכריח שימוש ב-Render בלבד, גם אם המחשב הראשי זמין.",
  },
];

const FailoverSettings = () => {
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState("auto");
  const [saving, setSaving] = useState(false);
  const { message } = App.useApp();

  useEffect(() => {
    getFailoverSettings().then((res) => {
      if (res.success) setMode(res.mode);
      setLoading(false);
    });
  }, []);

  const handleChange = async (e) => {
    const newMode = e.target.value;
    const previous = mode;
    setMode(newMode);
    setSaving(true);
    const res = await updateFailoverMode(newMode);
    setSaving(false);
    if (res.success) {
      message.success("המצב עודכן - השינוי ייכנס לתוקף תוך כ-20-40 שניות");
    } else {
      setMode(previous);
      message.error(res.error || "שגיאה בשמירה");
    }
  };

  if (loading) {
    return <div style={{ padding: 24, textAlign: "center" }}><Spin /></div>;
  }

  return (
    <div style={{ maxWidth: 640 }}>
      <Paragraph type="secondary">
        קובע איזה שרת קיוסקים ודשבורד ישתמשו - המחשב הראשי (בחדר המחשבים) או Render.
        השינוי כאן משפיע גלובלית, על כל הארגונים.
      </Paragraph>
      <Radio.Group onChange={handleChange} value={mode} disabled={saving} style={{ width: "100%" }}>
        <Space direction="vertical" size={12} style={{ width: "100%" }}>
          {OPTIONS.map((opt) => (
            <Radio key={opt.value} value={opt.value} style={{ width: "100%" }}>
              <Space direction="vertical" size={0} style={{ marginRight: 4 }}>
                <Text strong>{opt.icon} {opt.label}</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>{opt.description}</Text>
              </Space>
            </Radio>
          ))}
        </Space>
      </Radio.Group>
      {mode === "forceLocal" && (
        <Alert
          style={{ marginTop: 16 }}
          type="warning"
          showIcon
          message="לתשומת לבך"
          description='"תמיד המחשב הראשי" עובד היום רק בקיוסקים. בדשבורד (הדפדפן) זה עדיין יעבור אוטומטית ל-Render בפועל, כי לדפדפן עדיין אין HTTPS למחשב הראשי (שלב ג׳ בתוכנית טרם בוצע).'
        />
      )}
    </div>
  );
};

export default FailoverSettings;
