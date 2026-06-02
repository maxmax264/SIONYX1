import { useState, useEffect } from "react";
import { Switch, Button, Input, Upload, Space, Typography, Divider, Spin, App, Alert, Tooltip, ColorPicker, Card } from "antd";
import { ReloadOutlined, UploadOutlined, LinkOutlined, DeleteOutlined } from "@ant-design/icons";
import { ref as dbRef, get, set } from "firebase/database";
import { database } from "../../config/firebase";
import { useOrgId } from "../../hooks/useOrgId";

const { Text } = Typography;

const toBase64 = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = () => resolve(reader.result);
  reader.onerror = reject;
  reader.readAsDataURL(file);
});

const DESIGN_DEFAULTS = {
  brandName: "SIONYX",
  brandSubtitle: "ניהול מחשבים חכם",
  overlayColor1: "#6366F1",
  overlayColor2: "#8B5CF6",
  showRegister: true,
  cleanMode: false,
  formPosition: "center",
  welcomeText: "ברוכים הבאים",
  welcomeSubtext: "התחבר לחשבון שלך",
};

const KioskDesignSettings = () => {
  const orgId = useOrgId();
  const { message } = App.useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  // תמונת רקע
  const [enabled, setEnabled] = useState(false);
  const [imageUrl, setImageUrl] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [maxSizeMB, setMaxSizeMB] = useState(null);
  const [allowFileUpload, setAllowFileUpload] = useState(false);
  // עיצוב
  const [design, setDesign] = useState({ ...DESIGN_DEFAULTS });

  useEffect(() => {
    if (!orgId) return;
    const load = async () => {
      setLoading(true);
      const snap = await get(dbRef(database, `organizations/${orgId}/metadata`));
      if (snap.exists()) {
        const data = snap.val();
        setEnabled(!!data.kioskBackgroundEnabled);
        setImageUrl(data.kioskBackgroundUrl || "");
        setUrlInput(data.kioskBackgroundUrl || "");
        if (data.authDesign) setDesign({ ...DESIGN_DEFAULTS, ...data.authDesign });
      }
      const sysSnap = await get(dbRef(database, "systemSettings/maxImageSizeMB"));
      if (sysSnap.exists()) setMaxSizeMB(sysSnap.val());
      const uploadSnap = await get(dbRef(database, `systemSettings/orgs/${orgId}/allowFileUpload`));
      setAllowFileUpload(!uploadSnap.exists() || uploadSnap.val() !== false);
      setLoading(false);
    };
    load();
  }, [orgId]);

  const saveBg = async (url, isEnabled) => {
    await set(dbRef(database, `organizations/${orgId}/metadata/kioskBackgroundEnabled`), isEnabled);
    await set(dbRef(database, `organizations/${orgId}/metadata/kioskBackgroundUrl`), url || "");
  };

  const saveDesign = async (newDesign) => {
    setDesign(newDesign);
    await set(dbRef(database, `organizations/${orgId}/metadata/authDesign`), newDesign);
  };

  const handleToggle = async (val) => {
    setSaving(true);
    setEnabled(val);
    await saveBg(imageUrl, val);
    message.success(val ? "תמונת רקע הופעלה" : "תמונת רקע בוטלה");
    setSaving(false);
  };

  const handleUrlSave = async () => {
    if (!urlInput.trim()) { message.warning("הכנס קישור"); return; }
    setSaving(true);
    setImageUrl(urlInput.trim());
    await saveBg(urlInput.trim(), enabled);
    message.success("קישור נשמר");
    setSaving(false);
  };

  const handleUpload = async (file) => {
    const limitMB = maxSizeMB || 2;
    if (file.size > limitMB * 1024 * 1024) { message.error(`גודל מקסימלי: ${limitMB}MB`); return false; }
    setSaving(true);
    try {
      const base64 = await toBase64(file);
      setImageUrl(base64);
      setUrlInput(base64.substring(0, 40) + "...");
      await saveBg(base64, enabled);
      message.success("תמונה עלתה בהצלחה");
    } catch { message.error("שגיאה בהעלאה"); }
    setSaving(false);
    return false;
  };

  const handleRefreshKiosk = async () => {
    setSaving(true);
    await set(dbRef(database, `organizations/${orgId}/metadata/kioskRefreshAt`), Date.now().toString());
    message.success("הקיוסק יתרענן תוך 3 שניות");
    setSaving(false);
  };

  const handleDelete = async () => {
    setSaving(true);
    setImageUrl(""); setUrlInput("");
    await saveBg("", false);
    setEnabled(false);
    message.success("תמונה נמחקה");
    setSaving(false);
  };

  const handleDesignChange = async (field, value) => {
    const nd = { ...design, [field]: value };
    await saveDesign(nd);
    message.success("נשמר");
  };

  const handleReset = async () => {
    setSaving(true);
    await saveDesign({ ...DESIGN_DEFAULTS });
    message.success("אופס לברירת מחדל");
    setSaving(false);
  };

  if (loading) return <Spin />;

  const Preview = () => (
    <div style={{ borderRadius: 12, overflow: "hidden", boxShadow: "0 4px 24px rgba(99,102,241,0.2)", height: 260, position: "relative", background: "#333" }}>
      {enabled && imageUrl && (
        <img src={imageUrl} alt="bg" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", opacity: 0.55 }} />
      )}
      <div style={{ position: "absolute", inset: 0, zIndex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ display: "flex", flexDirection: "row", width: "80%", height: "80%", borderRadius: 10, overflow: "hidden", boxShadow: "0 2px 16px rgba(0,0,0,0.3)" }}>
          {/* צד ימין - טופס */}
          <div style={{ width: design.cleanMode ? "100%" : "50%", background: design.cleanMode ? "transparent" : "rgba(255,255,255,0.95)", padding: 16, display: "flex", flexDirection: "column", justifyContent: "center", direction: "rtl",
            alignItems: design.cleanMode ? (design.formPosition === "right" ? "flex-end" : design.formPosition === "left" ? "flex-start" : "center") : "stretch" }}>
            {design.cleanMode && (
              <div style={{ width: 180, background: "rgba(255,255,255,0.93)", borderRadius: 8, padding: 12, boxShadow: "0 2px 12px rgba(0,0,0,0.15)" }}>
            {design.cleanMode && <div style={{ textAlign: "center", marginBottom: 8, fontWeight: 800, fontSize: 14, color: design.overlayColor1 }}>{design.brandName}</div>}
            <div style={{ fontWeight: 700, fontSize: 12, marginBottom: 2 }}>{design.welcomeText}</div>
            <div style={{ color: "#888", fontSize: 9, marginBottom: 8 }}>{design.welcomeSubtext}</div>
            <div style={{ background: "#f0f0f0", borderRadius: 4, height: 18, marginBottom: 4 }} />
            <div style={{ background: "#f0f0f0", borderRadius: 4, height: 18, marginBottom: 8 }} />
            <div style={{ background: design.overlayColor1, borderRadius: 4, height: 22, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 9 }}>כניסה לחשבון</div>
            {design.showRegister && <div style={{ textAlign: "center", marginTop: 4, color: "#888", fontSize: 8 }}>אין לך חשבון? הירשם</div>}
          </div>
          )}
        </div>
          {/* צד שמאל - פאנל צבעוני */}
          {!design.cleanMode && (
            <div style={{ width: "50%", height: "100%", background: `linear-gradient(135deg, ${design.overlayColor1}, ${design.overlayColor2})`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "white", padding: 12 }}>
              <div style={{ fontSize: 14, fontWeight: 800 }}>{design.brandName || "SIONYX"}</div>
              <div style={{ fontSize: 9, opacity: 0.85, marginTop: 4, textAlign: "center" }}>{design.brandSubtitle}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Space style={{ width: "100%", justifyContent: "space-between" }}>
        <Text strong style={{ fontSize: 16 }}>עיצוב מסך כניסה לקיוסק</Text>
        <Space>
          <Tooltip title="שולח פקודת רענון לקיוסק">
            <Button icon={<ReloadOutlined />} onClick={handleRefreshKiosk} loading={saving}>רענן קיוסק</Button>
          </Tooltip>
          <Button danger onClick={handleReset} loading={saving}>ברירת מחדל</Button>
        </Space>
      </Space>

      <Preview />

      <Divider>תמונת רקע</Divider>
      <Alert type="info" showIcon message="איך להגדיר תמונת רקע?"
        description={
          <Space direction="vertical" size={2}>
            <Text>1. היכנס ל-<a href="https://postimages.org" target="_blank" rel="noreferrer">postimages.org</a> והירשם</Text>
            <Text>2. העלה תמונה → העתק <strong>קישור ישיר</strong></Text>
            <Text>3. הדבק למטה ולחץ שמור</Text>
          </Space>
        } />
      <Space align="center">
        <Switch checked={enabled} onChange={handleToggle} loading={saving} />
        <Text strong>הפעל תמונת רקע</Text>
      </Space>
      {enabled && (
        <>
          {allowFileUpload && (
            <Upload beforeUpload={handleUpload} showUploadList={false} accept="image/*">
              <Button icon={<UploadOutlined />} loading={saving}>בחר תמונה</Button>
            </Upload>
          )}
          <Space.Compact style={{ width: "100%" }}>
            <Input prefix={<LinkOutlined />} placeholder="https://i.postimg.cc/..." value={urlInput.startsWith("data:") ? "(תמונה מקומית)" : urlInput} onChange={e => setUrlInput(e.target.value)} />
            <Button type="primary" onClick={handleUrlSave} loading={saving}>שמור</Button>
          </Space.Compact>
          {imageUrl && <Button danger icon={<DeleteOutlined />} onClick={handleDelete} loading={saving}>מחק תמונה</Button>}
        </>
      )}

      <Divider>עיצוב פאנל</Divider>
      <Space direction="vertical" size={12} style={{ width: "100%" }}>
        <Space align="center">
          <Text style={{ width: 110 }}>צבע ראשי:</Text>
          <ColorPicker value={design.overlayColor1} onChange={(_, hex) => handleDesignChange("overlayColor1", hex)} />
        </Space>
        <Space align="center">
          <Text style={{ width: 110 }}>צבע משני:</Text>
          <ColorPicker value={design.overlayColor2} onChange={(_, hex) => handleDesignChange("overlayColor2", hex)} />
        </Space>
        <Space align="center">
          <Text style={{ width: 110 }}>שם המערכת:</Text>
          <Text strong>{design.brandName}</Text>
        </Space>
        <Space align="center">
          <Text style={{ width: 110 }}>כותרת משנה:</Text>
          <Input value={design.brandSubtitle} onChange={e => setDesign({ ...design, brandSubtitle: e.target.value })} onBlur={() => saveDesign(design)} style={{ width: 180 }} />
        </Space>
        <Space align="center">
          <Text style={{ width: 110 }}>כותרת פתיחה:</Text>
          <Input value={design.welcomeText} onChange={e => setDesign({ ...design, welcomeText: e.target.value })} onBlur={() => saveDesign(design)} style={{ width: 180 }} />
        </Space>
        <Space align="center">
          <Text style={{ width: 110 }}>תת כותרת:</Text>
          <Input value={design.welcomeSubtext} onChange={e => setDesign({ ...design, welcomeSubtext: e.target.value })} onBlur={() => saveDesign(design)} style={{ width: 180 }} />
        </Space>
      </Space>

      <Divider>אפשרויות</Divider>
      <Space direction="vertical" size={12}>
        <Space align="center">
          <Switch checked={design.showRegister} onChange={val => handleDesignChange("showRegister", val)} />
          <Text>הצג כפתור הרשמה</Text>
        </Space>
        <Space align="center">
          <Switch checked={design.cleanMode || false} onChange={val => handleDesignChange("cleanMode", val)} />
          <Space direction="vertical" size={0}>
            <Text>מצב נקי — טופס בלבד</Text>
            <Text type="secondary" style={{ fontSize: 11 }}>מסתיר את הפאנל הצבעוני</Text>
          </Space>
        </Space>
        {design.cleanMode && (
          <Space align="center">
            <Text style={{ width: 110 }}>מיקום טופס:</Text>
            {["right","center","left"].map(pos => (
              <Button key={pos} size="small" type={design.formPosition === pos ? "primary" : "default"}
                onClick={() => handleDesignChange("formPosition", pos)}>
                {pos === "right" ? "ימין" : pos === "center" ? "מרכז" : "שמאל"}
              </Button>
            ))}
          </Space>
        )}
      </Space>
    </Space>
  );
};

export default KioskDesignSettings;
