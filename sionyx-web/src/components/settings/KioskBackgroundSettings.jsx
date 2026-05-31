import { useState, useEffect } from "react";
import { Switch, Button, Input, Upload, Space, Typography, Divider, Image, Spin, App } from "antd";
import { UploadOutlined, LinkOutlined, DeleteOutlined } from "@ant-design/icons";
import { ref as dbRef, get, set } from "firebase/database";
import { ref as storageRef, uploadBytes, getDownloadURL, deleteObject } from "firebase/storage";
import { database, storage } from "../../config/firebase";
import { useOrgId } from "../../hooks/useOrgId";

const { Text } = Typography;

const KioskBackgroundSettings = () => {
  const orgId = useOrgId();
  const { message } = App.useApp();
  const [enabled, setEnabled] = useState(false);
  const [imageUrl, setImageUrl] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [maxSizeMB, setMaxSizeMB] = useState(null);

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
    if (maxSizeMB && file.size > maxSizeMB * 1024 * 1024) {
      message.error(`גודל מקסימלי: ${maxSizeMB}MB`);
      return false;
    }
    setSaving(true);
    try {
      const sRef = storageRef(storage, `organizations/${orgId}/kioskBackground`);
      await uploadBytes(sRef, file);
      const url = await getDownloadURL(sRef);
      setImageUrl(url);
      setUrlInput(url);
      await saveToDb(url, enabled);
      message.success("תמונה עלתה בהצלחה");
    } catch (e) {
      message.error("שגיאה בהעלאה");
    }
    setSaving(false);
    return false;
  };

  const handleDelete = async () => {
    setSaving(true);
    try {
      const sRef = storageRef(storage, `organizations/${orgId}/kioskBackground`);
      await deleteObject(sRef).catch(() => {});
      setImageUrl("");
      setUrlInput("");
      await saveToDb("", false);
      setEnabled(false);
      message.success("תמונה נמחקה");
    } catch (e) {
      message.error("שגיאה");
    }
    setSaving(false);
  };

  if (loading) return <Spin />;

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Space align="center">
        <Switch checked={enabled} onChange={handleToggle} loading={saving} />
        <Text strong>הפעל תמונת רקע לקיוסק</Text>
      </Space>

      {enabled && (
        <>
          <Divider>העלאת קובץ</Divider>
          <Upload beforeUpload={handleUpload} showUploadList={false} accept="image/*">
            <Button icon={<UploadOutlined />} loading={saving}>בחר תמונה</Button>
          </Upload>
          {maxSizeMB && <Text type="secondary">גודל מקסימלי: {maxSizeMB}MB</Text>}

          <Divider>או הדבק קישור</Divider>
          <Space.Compact style={{ width: "100%" }}>
            <Input
              prefix={<LinkOutlined />}
              placeholder="https://..."
              value={urlInput}
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
