import os

DEFAULTS = '''{
  "brandName": "SIONYX",
  "brandSubtitle": "ניהול מחשבים חכם",
  "overlayColor1": "#6366F1",
  "overlayColor2": "#8B5CF6",
  "showRegister": true,
  "welcomeText": "ברוכים הבאים",
  "welcomeSubtext": "התחבר לחשבון שלך"
}'''

content = '''import { useState, useEffect } from "react";
import { Button, Input, Space, Typography, Divider, Spin, App, Switch, ColorPicker } from "antd";
import { ref as dbRef, get, set } from "firebase/database";
import { database } from "../../config/firebase";
import { useOrgId } from "../../hooks/useOrgId";

const { Text } = Typography;

const DEFAULTS = {
  brandName: "SIONYX",
  brandSubtitle: "ניהול מחשבים חכם",
  overlayColor1: "#6366F1",
  overlayColor2: "#8B5CF6",
  showRegister: true,
  welcomeText: "ברוכים הבאים",
  welcomeSubtext: "התחבר לחשבון שלך",
};

const AuthDesignSettings = () => {
  const orgId = useOrgId();
  const { message } = App.useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [design, setDesign] = useState({ ...DEFAULTS });

  useEffect(() => {
    if (!orgId) return;
    const load = async () => {
      setLoading(true);
      const snap = await get(dbRef(database, `organizations/${orgId}/metadata/authDesign`));
      if (snap.exists()) setDesign({ ...DEFAULTS, ...snap.val() });
      setLoading(false);
    };
    load();
  }, [orgId]);

  const save = async (newDesign) => {
    setSaving(true);
    setDesign(newDesign);
    await set(dbRef(database, `organizations/${orgId}/metadata/authDesign`), newDesign);
    message.success("עיצוב נשמר");
    setSaving(false);
  };

  const handleChange = (field, value) => {
    save({ ...design, [field]: value });
  };

  const handleReset = () => {
    save({ ...DEFAULTS });
    message.success("אופס לברירת מחדל");
  };

  if (loading) return <Spin />;

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Text strong style={{ fontSize: 16 }}>עיצוב מסך התחברות</Text>
        <Button danger onClick={handleReset} loading={saving}>ברירת מחדל</Button>
      </Space>

      <div style={{ background: "#f5f5f5", borderRadius: 12, padding: 16, marginBottom: 8 }}>
        <div style={{
          background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`,
          borderRadius: 10, padding: "24px 32px", color: "white", textAlign: "center"
        }}>
          <div style={{ fontSize: 28, fontWeight: 800 }}>{design.brandName || "SIONYX"}</div>
          <div style={{ fontSize: 14, opacity: 0.85, marginTop: 6 }}>{design.brandSubtitle || "ניהול מחשבים חכם"}</div>
        </div>
        <div style={{ background: "white", borderRadius: 10, padding: "16px 24px", marginTop: 8 }}>
          <div style={{ fontWeight: 700, fontSize: 18 }}>{design.welcomeText || "ברוכים הבאים"}</div>
          <div style={{ color: "#888", fontSize: 13, marginTop: 4 }}>{design.welcomeSubtext || "התחבר לחשבון שלך"}</div>
          <div style={{ background: "#e8e8e8", borderRadius: 6, height: 36, marginTop: 12 }} />
          <div style={{ background: "#e8e8e8", borderRadius: 6, height: 36, marginTop: 8 }} />
          <div style={{ background: design.overlayColor1, borderRadius: 6, height: 36, marginTop: 12 }} />
          {design.showRegister && (
            <div style={{ textAlign: "center", marginTop: 8, color: "#888", fontSize: 12 }}>אין לך חשבון? הירשם</div>
          )}
        </div>
      </div>

      <Divider>פאנל צבעים</Divider>
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <Space align="center">
          <Text style={{ width: 120 }}>צבע ראשי:</Text>
          <ColorPicker value={design.overlayColor1}
            onChange={(_, hex) => handleChange("overlayColor1", hex)} />
          <Text type="secondary">{design.overlayColor1}</Text>
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>צבע משני:</Text>
          <ColorPicker value={design.overlayColor2}
            onChange={(_, hex) => handleChange("overlayColor2", hex)} />
          <Text type="secondary">{design.overlayColor2}</Text>
        </Space>
      </Space>

      <Divider>טקסטים</Divider>
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <Space align="center">
          <Text style={{ width: 120 }}>שם המערכת:</Text>
          <Input value={design.brandName}
            onChange={e => setDesign({ ...design, brandName: e.target.value })}
            onBlur={() => save(design)}
            style={{ width: 200 }} />
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>כותרת משנה:</Text>
          <Input value={design.brandSubtitle}
            onChange={e => setDesign({ ...design, brandSubtitle: e.target.value })}
            onBlur={() => save(design)}
            style={{ width: 200 }} />
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>כותרת פתיחה:</Text>
          <Input value={design.welcomeText}
            onChange={e => setDesign({ ...design, welcomeText: e.target.value })}
            onBlur={() => save(design)}
            style={{ width: 200 }} />
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>תת כותרת:</Text>
          <Input value={design.welcomeSubtext}
            onChange={e => setDesign({ ...design, welcomeSubtext: e.target.value })}
            onBlur={() => save(design)}
            style={{ width: 200 }} />
        </Space>
      </Space>

      <Divider>אפשרויות</Divider>
      <Space align="center">
        <Switch checked={design.showRegister}
          onChange={val => handleChange("showRegister", val)} />
        <Text>הצג כפתור הרשמה</Text>
      </Space>
    </Space>
  );
};

export default AuthDesignSettings;
'''

path = r'.\src\components\settings\AuthDesignSettings.jsx'
open(path, 'w', encoding='utf-8').write(content)
print("OK")
