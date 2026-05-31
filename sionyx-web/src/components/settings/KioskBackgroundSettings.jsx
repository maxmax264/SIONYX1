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
    message.success(val ? "\u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2 \u05d4\u05d5\u05e4\u05e2\u05dc\u05d4" : "\u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2 \u05d1\u05d5\u05d8\u05dc\u05d4");
    setSaving(false);
  };

  const handleUrlSave = async () => {
    if (!urlInput.trim()) { message.warning("\u05d4\u05db\u05e0\u05e1 \u05e7\u05d9\u05e9\u05d5\u05e8"); return; }
    setSaving(true);
    setImageUrl(urlInput.trim());
    await saveToDb(urlInput.trim(), enabled);
    message.success("\u05e7\u05d9\u05e9\u05d5\u05e8 \u05e0\u05e9\u05de\u05e8");
    setSaving(false);
  };

  const handleUpload = async (file) => {
    if (maxSizeMB && file.size > maxSizeMB * 1024 * 1024) {
      message.error(`\u05d2\u05d5\u05d3\u05dc \u05de\u05e7\u05e1\u05d9\u05de\u05dc\u05d9: ${maxSizeMB}MB`);
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
      message.success("\u05ea\u05de\u05d5\u05e0\u05d4 \u05e2\u05dc\u05ea\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4");
    } catch (e) {
      message.error("\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05d4\u05e2\u05dc\u05d0\u05d4");
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
      message.success("\u05ea\u05de\u05d5\u05e0\u05d4 \u05e0\u05de\u05d7\u05e7\u05d4");
    } catch (e) {
      message.error("\u05e9\u05d2\u05d9\u05d0\u05d4");
    }
    setSaving(false);
  };

  if (loading) return <Spin />;

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Space align="center">
        <Switch checked={enabled} onChange={handleToggle} loading={saving} />
        <Text strong>\u05d4\u05e4\u05e2\u05dc \u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2 \u05dc\u05e7\u05d9\u05d5\u05e1\u05e7</Text>
      </Space>

      {enabled && (
        <>
          <Divider>\u05d4\u05e2\u05dc\u05d0\u05ea \u05e7\u05d5\u05d1\u05e5</Divider>
          <Upload beforeUpload={handleUpload} showUploadList={false} accept="image/*">
            <Button icon={<UploadOutlined />} loading={saving}>\u05d1\u05d7\u05e8 \u05ea\u05de\u05d5\u05e0\u05d4</Button>
          </Upload>
          {maxSizeMB && <Text type="secondary">\u05d2\u05d5\u05d3\u05dc \u05de\u05e7\u05e1\u05d9\u05de\u05dc\u05d9: {maxSizeMB}MB</Text>}

          <Divider>\u05d0\u05d5 \u05d4\u05d3\u05d1\u05e7 \u05e7\u05d9\u05e9\u05d5\u05e8</Divider>
          <Space.Compact style={{ width: "100%" }}>
            <Input
              prefix={<LinkOutlined />}
              placeholder="https://..."
              value={urlInput}
              onChange={e => setUrlInput(e.target.value)}
            />
            <Button type="primary" onClick={handleUrlSave} loading={saving}>\u05e9\u05de\u05d5\u05e8</Button>
          </Space.Compact>

          {imageUrl && (
            <>
              <Divider>\u05ea\u05e6\u05d5\u05d2\u05d4 \u05de\u05e7\u05d3\u05d9\u05de\u05d4</Divider>
              <Image src={imageUrl} alt="kiosk background" style={{ maxHeight: 200, objectFit: "cover", borderRadius: 8 }} />
              <Button danger icon={<DeleteOutlined />} onClick={handleDelete} loading={saving}>\u05de\u05d7\u05e7 \u05ea\u05de\u05d5\u05e0\u05d4</Button>
            </>
          )}
        </>
      )}
    </Space>
  );
};

export default KioskBackgroundSettings;
