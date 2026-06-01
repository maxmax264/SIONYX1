import { useState, useEffect } from "react";
import { Switch, Button, Input, Upload, Space, Typography, Divider, Image, Spin, App, Alert, Tooltip } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import { UploadOutlined, LinkOutlined, DeleteOutlined } from "@ant-design/icons";
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

const KioskBackgroundSettings = () => {
  const orgId = useOrgId();
  const { message } = App.useApp();
  const [enabled, setEnabled] = useState(false);
  const [imageUrl, setImageUrl] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [maxSizeMB, setMaxSizeMB] = useState(null);
  const [allowFileUpload, setAllowFileUpload] = useState(false);

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
      }
      const sysSnap = await get(dbRef(database, "systemSettings/maxImageSizeMB"));
      if (sysSnap.exists()) setMaxSizeMB(sysSnap.val());
      const uploadSnap = await get(dbRef(database, `systemSettings/orgs/${orgId}/allowFileUpload`));
      setAllowFileUpload(!uploadSnap.exists() || uploadSnap.val() !== false);
      setLoading(false);
    };
    load();
  }, [orgId]);

  const saveToDb = async (url, isEnabled) => {
    await set(dbRef(database, `organizations/${orgId}/metadata/kioskBackgroundEnabled`), isEnabled);
    await set(dbRef(database, `organizations/${orgId}/metadata/kioskBackgroundUrl`), url || "");
  };

  const handleToggle = async (val) => {
    setSaving(true);
    setEnabled(val);
    await saveToDb(imageUrl, val);
    message.success(val ? "תמונת רקע הופעלה" : "תמונת רקע בוטלה");
    setSaving(false);
  };

  const handleUrlSave = async () => {
    if (!urlInput.trim()) { message.warning("הכנס קישור"); return; }
    setSaving(true);
    setImageUrl(urlInput.trim());
    await saveToDb(urlInput.trim(), enabled);
    message.success("קישור נשמר");
    setSaving(false);
  };

  const handleUpload = async (file) => {
    const limitMB = maxSizeMB || 2;
    if (file.size > limitMB * 1024 * 1024) {
      message.error(`גודל מקסימלי: ${limitMB}MB`);
      return false;
    }
    setSaving(true);
    try {
      const base64 = await toBase64(file);
      setImageUrl(base64);
      setUrlInput(base64.substring(0, 40) + "...");
      await saveToDb(base64, enabled);
      message.success("תמונה עלתה בהצלחה");
    } catch (e) {
      message.error("שגיאה בהעלאה");
    }
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
    setImageUrl("");
    setUrlInput("");
    await saveToDb("", false);
    setEnabled(false);
    message.success("תמונה נמחקה");
    setSaving(false);
  };

  if (loading) return <Spin />;

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Alert
        type="info"
        showIcon
        message="איך להגדיר תמונת רקע לקיוסק?"
        description={
          <Space direction="vertical" size={4}>
            <Text>1. היכנס לאתר <a href="https://postimages.org" target="_blank" rel="noreferrer">postimages.org</a> והירשם — כדי שהתמונות ישמרו לצמיתות</Text>
            <Text>2. העלה את התמונה הרצויה</Text>
            <Text>3. מהרשימה שמופיעה העתק את השורה <strong>קישור ישיר</strong></Text>
            <Text type="secondary">הקישור נראה כך: https://i.postimg.cc/xxxxx/image.jpg</Text>
            <Text>4. הדבק את הקישור בשדה למטה ולחץ <strong>שמור</strong></Text>
          </Space>
        }
        style={{ marginBottom: 8 }}
      />
      <Space align="center" style={{ width: "100%", justifyContent: "space-between" }}>
        <Space align="center">
          <Switch checked={enabled} onChange={handleToggle} loading={saving} />
          <Text strong>הפעל תמונת רקע לקיוסק</Text>
        </Space>
        <Tooltip title="שולח פקודת רענון לקיוסק — התמונה תתעדכן תוך 3 שניות">
          <Button icon={<ReloadOutlined />} onClick={handleRefreshKiosk} loading={saving}>
            רענן קיוסק
          </Button>
        </Tooltip>
      </Space>

      {enabled && (
        <>
          {allowFileUpload && (
            <>
              <Divider>העלאת קובץ</Divider>
              <Upload beforeUpload={handleUpload} showUploadList={false} accept="image/*">
                <Button icon={<UploadOutlined />} loading={saving}>בחר תמונה</Button>
              </Upload>
              {maxSizeMB && <Text type="secondary">גודל מקסימלי: {maxSizeMB}MB</Text>}
            </>
          )}

          <Divider>הדבק קישור</Divider>
          <Space.Compact style={{ width: "100%" }}>
            <Input
              prefix={<LinkOutlined />}
              placeholder="https://..."
              value={urlInput.startsWith("data:") ? "(תמונה מקומית)" : urlInput}
              onChange={e => setUrlInput(e.target.value)}
            />
            <Button type="primary" onClick={handleUrlSave} loading={saving}>שמור</Button>
          </Space.Compact>

          {imageUrl && (
            <>
              <Divider>תצוגה מקדימה</Divider>
              <Image src={imageUrl} alt="kiosk background" style={{ maxHeight: 200, objectFit: "cover", borderRadius: 8 }} />
              <Button danger icon={<DeleteOutlined />} onClick={handleDelete} loading={saving}>מחק תמונה</Button>
            </>
          )}
        </>
      )}
    </Space>
  );
};

export default KioskBackgroundSettings;
