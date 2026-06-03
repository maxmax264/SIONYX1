import { useState, useEffect } from "react";
import { Switch, Button, Input, Upload, Space, Typography, Divider, Spin, App, Alert, Tooltip, ColorPicker, Slider, Select } from "antd";
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
  welcomeText: "ברוכים הבאים",
  welcomeSubtext: "התחבר לחשבון שלך",
  formX: 50,
  formY: 50,
  formWidth: 340,
};

const KioskDesignSettings = () => {
  const orgId = useOrgId();
  const { message } = App.useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [enabled, setEnabled] = useState(false);
  const [imageUrl, setImageUrl] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [maxSizeMB, setMaxSizeMB] = useState(null);
  const [allowFileUpload, setAllowFileUpload] = useState(false);
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
      setUrlInput("(תמונה מקומית)");
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
    // גם איפוס תמונה
    setImageUrl(""); setUrlInput(""); setEnabled(false);
    await saveBg("", false);
    message.success("אופס לברירת מחדל");
    setSaving(false);
  };

  if (loading) return <Spin />;

  // תצוגה מקדימה — מדמה את מסך הקיוסק האמיתי
  const PREV_W = 760;
  const PREV_H = 280;
  const scaleX = design.formWidth / PREV_W;

  const FormBox = () => (
    <div style={{
      width: design.formWidth,
      background: "rgba(255,255,255,0.96)",
      borderRadius: 10,
      padding: "20px 24px",
      boxShadow: "0 4px 24px rgba(0,0,0,0.18)",
      direction: "rtl",
      position: "absolute",
      left: `${design.formX}%`,
      top: `${design.formY}%`,
      transform: "translate(-50%, -50%)",
      minWidth: 180,
      maxWidth: "90%",
    }}>
      <div style={{ textAlign: "center", marginBottom: 10, fontWeight: 800, fontSize: 15, color: design.overlayColor1 }}>{design.brandName}</div>
      <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 2 }}>{design.welcomeText}</div>
      <div style={{ color: "#888", fontSize: 10, marginBottom: 10 }}>{design.welcomeSubtext}</div>
      <div style={{ background: "#f0f0f0", borderRadius: 5, height: 20, marginBottom: 6 }} />
      <div style={{ background: "#f0f0f0", borderRadius: 5, height: 20, marginBottom: 10 }} />
      <div style={{ background: design.buttonColor || design.overlayColor1, borderRadius: 5, height: 26, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600 }}>כניסה לחשבון</div>
      {design.showRegister && <div style={{ textAlign: "center", marginTop: 6, color: "#888", fontSize: 9 }}>אין לך חשבון? הירשם</div>}
    </div>
  );

  const Preview = () => (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: 500,
        background: "linear-gradient(135deg, #0F172A, #1E1B4B, #0F172A)",
        borderRadius: 16,
        overflow: "hidden",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: 20,
      }}
    >
      {enabled && imageUrl && (
        <img
          src={imageUrl}
          alt=""
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            zIndex: 0,
          }}
        />
      )}
      {design.cleanMode ? (
        <>
          <FormBox />
          <div style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            background: "rgba(0,0,0,0.6)",
            padding: "12px 20px",
            zIndex: 10,
            display: "flex",
            gap: 24,
            alignItems: "center",
            direction: "rtl",
          }}>
            <div style={{ flex: 1 }}>
              <Text style={{ color: "white", fontSize: 11 }}>אופקי: {design.formX ?? 50}%</Text>
              <Slider min={5} max={95} value={design.formX ?? 50}
                onChange={val => setDesign({ ...design, formX: val })}
                onChangeComplete={val => handleDesignChange("formX", val)}
                style={{ margin: "4px 0 0" }} />
            </div>
            <div style={{ flex: 1 }}>
              <Text style={{ color: "white", fontSize: 11 }}>אנכי: {design.formY ?? 50}%</Text>
              <Slider min={10} max={90} value={design.formY ?? 50}
                onChange={val => setDesign({ ...design, formY: val })}
                onChangeComplete={val => handleDesignChange("formY", val)}
                style={{ margin: "4px 0 0" }} />
            </div>
            <div style={{ flex: 1 }}>
              <Text style={{ color: "white", fontSize: 11 }}>רוחב: {design.formWidth ?? 340}px</Text>
              <Slider min={200} max={500} step={10} value={design.formWidth ?? 340}
                onChange={val => setDesign({ ...design, formWidth: val })}
                onChangeComplete={val => handleDesignChange("formWidth", val)}
                style={{ margin: "4px 0 0" }} />
            </div>
          </div>
        </>
      ) : (
        <div
          style={{
            width: 800,
            height: 560,
            background: "white",
            borderRadius: 20,
            overflow: "hidden",
            boxShadow: "0 20px 60px rgba(0,0,0,.25)",
            position: "relative",
            display: "flex",
            zIndex: 1,
          }}
        >
          <div
            style={{
              flex: 1,
              padding: 50,
              direction: "rtl",
              background: "white",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}
          >
            <h2>{design.welcomeText}</h2>
            <div style={{ color: "#888", marginBottom: 30 }}>{design.welcomeSubtext}</div>
            <div style={{ height: 46, background: "#f1f1f1", borderRadius: 8, marginBottom: 14 }} />
            <div style={{ height: 46, background: "#f1f1f1", borderRadius: 8, marginBottom: 20 }} />
            <div
              style={{
                height: 48,
                background: design.buttonColor || design.overlayColor1,
                borderRadius: 8,
                color: "white",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                fontWeight: 700,
              }}
            >
              התחברות
            </div>
            {design.showRegister && (
              <div style={{ textAlign: "center", marginTop: 15, color: "#888" }}>אין חשבון? הירשם</div>
            )}
          </div>
          <div
            style={{
              width: 320,
              background: `linear-gradient(160deg, ${design.overlayColor1}, ${design.overlayColor2})`,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              color: "white",
              padding: 40,
            }}
          >
            <div style={{ fontSize: 42, fontWeight: 800 }}>SIONYX</div>
            <div style={{ marginTop: 14, opacity: 0.9, textAlign: "center" }}>{design.brandSubtitle}</div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      {/* כותרת */}
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

      {/* תמונת רקע */}
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

      {/* עיצוב פאנל */}
      <Divider>עיצוב פאנל</Divider>
      <Space direction="vertical" size={14} style={{ width: "100%" }}>
        <Space align="center">
          <Text style={{ width: 120 }}>צבע ראשי:</Text>
          <ColorPicker value={design.overlayColor1} onChange={(color) => handleDesignChange("overlayColor1", color.toHexString())} />
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>צבע משני:</Text>
          <ColorPicker value={design.overlayColor2} onChange={(color) => handleDesignChange("overlayColor2", color.toHexString())} />
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>צבע כפתורים:</Text>
          <ColorPicker value={design.buttonColor || design.overlayColor1} onChange={(color) => handleDesignChange("buttonColor", color.toHexString())} />
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>שם המערכת:</Text>
          <Text strong>SIONYX</Text>
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>כותרת משנה:</Text>
          <Input value={design.brandSubtitle} onChange={e => setDesign({ ...design, brandSubtitle: e.target.value })} onBlur={() => saveDesign(design)} style={{ width: 200 }} />
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>כותרת פתיחה:</Text>
          <Input value={design.welcomeText} onChange={e => setDesign({ ...design, welcomeText: e.target.value })} onBlur={() => saveDesign(design)} style={{ width: 200 }} />
        </Space>
        <Space align="center">
          <Text style={{ width: 120 }}>תת כותרת:</Text>
          <Input value={design.welcomeSubtext} onChange={e => setDesign({ ...design, welcomeSubtext: e.target.value })} onBlur={() => saveDesign(design)} style={{ width: 200 }} />
        </Space>
      </Space>

      {/* אפשרויות */}
      <Divider>אפשרויות</Divider>
      <Space direction="vertical" size={14} style={{ width: "100%" }}>
        <Space align="center">
          <Switch checked={design.showRegister} onChange={val => handleDesignChange("showRegister", val)} />
          <Text>הצג כפתור הרשמה</Text>
        </Space>
        <Space align="center">
          <Switch checked={design.cleanMode || false} onChange={val => handleDesignChange("cleanMode", val)} />
          <Space direction="vertical" size={0}>
            <Text>מצב נקי — טופס בלבד</Text>
            <Text type="secondary" style={{ fontSize: 11 }}>מסתיר את הפאנל הצבעוני, הטופס ניתן למיקום חופשי</Text>
          </Space>
        </Space>


      </Space>
    </Space>
  );
};

export default KioskDesignSettings;
