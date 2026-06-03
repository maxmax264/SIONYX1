import { useState, useEffect } from "react";
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
  buttonColor: "#6366F1",
  showRegister: true,
  cleanMode: false,
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
      if (snap.exists()) { const val = snap.val(); console.log('RAW:', JSON.stringify(val)); const filtered = Object.fromEntries(Object.entries(val).filter(([k,v]) => v !== '' && v !== null && v !== undefined)); console.log('FILTERED:', JSON.stringify(filtered)); setDesign({ ...DEFAULTS, ...filtered }); }
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
    const updated = { ...design, [field]: value };
    setDesign(updated);
    save(updated);
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

      <div style={{ background: "#e8e8e8", borderRadius: 12, padding: 12, marginBottom: 8 }}>
        <div style={{
          display: "flex", flexDirection: "row-reverse",
          borderRadius: 10, overflow: "hidden",
          boxShadow: "0 4px 24px rgba(99,102,241,0.2)",
          height: 280, background: "white"
        }}>
          {!design.cleanMode && (
            <div style={{
              width: "50%", height: "100%",
              background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`,
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              color: "white", padding: "24px"
            }}>
              <div style={{ fontSize: 22, fontWeight: 800, letterSpacing: 2 }}>{design.brandName || "SIONYX"}</div>
              <div style={{ fontSize: 12, opacity: 0.85, marginTop: 8, textAlign: "center" }}>{design.brandSubtitle || "ניהול מחשבים חכם"}</div>
            </div>
          )}
          <div style={{
            width: design.cleanMode ? "100%" : "50%", height: "100%",
            background: "white", padding: "24px",
            display: "flex", flexDirection: "column", justifyContent: "center",
            direction: "rtl"
          }}>
            {design.cleanMode && (
              <div style={{ textAlign: "center", marginBottom: 16 }}>
                <div style={{ fontSize: 22, fontWeight: 800, color: design.overlayColor1 }}>{design.brandName || "SIONYX"}</div>
                <div style={{ fontSize: 11, color: "#888", marginTop: 4 }}>{design.brandSubtitle || "ניהול מחשבים חכם"}</div>
              </div>
            )}
            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{design.welcomeText || "ברוכים הבאים"}</div>
            <div style={{ color: "#888", fontSize: 11, marginBottom: 16 }}>{design.welcomeSubtext || "התחבר לחשבון שלך"}</div>
            <div style={{ background: "#f0f0f0", borderRadius: 6, height: 28, marginBottom: 8 }} />
            <div style={{ background: "#f0f0f0", borderRadius: 6, height: 28, marginBottom: 12 }} />
            <div style={{ background: design.buttonColor, borderRadius: 6, height: 32, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12 }}>כניסה לחשבון</div>
            {design.showRegister && (
              <div style={{ textAlign: "center", marginTop: 8, color: "#888", fontSize: 11 }}>אין לך חשבון? הירשם</div>
            )}
          </div>
        </div>
      </div>

      <Divider>פאנל צבעים</Divider>
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <Space align="center">
          <Text style={{ width: 120 }}>צבע ראשי:</Text>
          <ColorPicker value={design.overlayColor1}
            onChange={(color) => handleChange("overlayColor1", color.toHexString())} />
          <Text type="secondary">{design.overlayColor1}</Text>
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>צבע משני:</Text>
          <ColorPicker value={design.overlayColor2}
            onChange={(color) => handleChange("overlayColor2", color.toHexString())} />
          <Text type="secondary">{design.overlayColor2}</Text>
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>צבע כפתורים:</Text>
          <ColorPicker value={design.buttonColor}
            onChange={(color) => { console.log("NEW COLOR:", color.toHexString()); handleChange("buttonColor", color.toHexString()); }} />
          <Text type="secondary">{design.buttonColor || design.overlayColor1}</Text>
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
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <Space align="center">
          <Switch checked={design.showRegister}
            onChange={val => handleChange("showRegister", val)} />
          <Text>הצג כפתור הרשמה</Text>
        </Space>
        <Space align="center">
          <Switch checked={design.cleanMode || false}
            onChange={val => handleChange("cleanMode", val)} />
          <Space direction="vertical" size={0}>
            <Text>מצב נקי — טופס בלבד</Text>
            <Text type="secondary" style={{ fontSize: 11 }}>מסתיר את הפאנל הצבעוני, הלוגו יופיע מעל הטופס</Text>
          </Space>
        </Space>
      </Space>
    </Space>
  );
};

export default AuthDesignSettings;
