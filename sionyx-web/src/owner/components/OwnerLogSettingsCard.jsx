import { useEffect, useState } from "react";
import { Card, Switch, Radio, Input, InputNumber, Select, Button, Space, Typography, Alert, Spin, App, Popconfirm } from "antd";
import { SaveOutlined, SendOutlined } from "@ant-design/icons";
import { getLogConfig, saveLogConfig, requestLogSend } from "../services/ownerLogService";

const { Text } = Typography;

const EMPTY_CONFIG = {
  autoEnabled: false,
  mode: "internal",
  intervalMs: 0,
  external: { url: "", apiKey: "", format: "sionyx" },
};

/**
 * Master-dashboard log management. Two directions for now:
 *   internal - the existing Understood/Redis store, read in the tab below
 *   external - an outside site (url + API key + format)
 * Nothing is shipped automatically unless "automatic sending" is switched on;
 * "send now" always works and is the normal way to pull a log.
 */
const OwnerLogSettingsCard = () => {
  const { message } = App.useApp();
  const [config, setConfig] = useState(EMPTY_CONFIG);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [sendingAll, setSendingAll] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    (async () => {
      const result = await getLogConfig();
      if (result.success) setConfig({ ...EMPTY_CONFIG, ...result.config, external: { ...EMPTY_CONFIG.external, ...(result.config?.external || {}) } });
      else message.error(result.error || "שגיאה בטעינת הגדרות הלוגים");
      setLoading(false);
    })();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const update = (patch) => { setConfig((c) => ({ ...c, ...patch })); setDirty(true); };
  const updateExternal = (patch) => { setConfig((c) => ({ ...c, external: { ...c.external, ...patch } })); setDirty(true); };

  const handleSave = async () => {
    setSaving(true);
    const result = await saveLogConfig(config);
    if (result.success) {
      setConfig({ ...EMPTY_CONFIG, ...result.config });
      setDirty(false);
      message.success("ההגדרות נשמרו והוחלו על כל המחשבים");
    } else {
      message.error(result.error || "השמירה נכשלה");
    }
    setSaving(false);
  };

  const handleSendAll = async () => {
    setSendingAll(true);
    const result = await requestLogSend();
    if (result.success) message.success("הבקשה נשלחה לכל המחשבים - הלוגים יגיעו תוך שניות (למחשבים מקוונים)");
    else message.error(result.error || "שליחת הבקשה נכשלה");
    setSendingAll(false);
  };

  if (loading) return <Card size="small" style={{ marginBottom: 16 }}><div style={{ textAlign: "center", padding: 16 }}><Spin /></div></Card>;

  const external = config.mode === "external";

  return (
    <Card size="small" title="ניהול שליחת לוגים" style={{ marginBottom: 16 }}>
      <Space direction="vertical" size="middle" style={{ width: "100%" }}>
        <Space wrap>
          <Text strong>יעד הלוגים:</Text>
          <Radio.Group value={config.mode} onChange={(e) => update({ mode: e.target.value })} optionType="button" buttonStyle="solid">
            <Radio.Button value="internal">שרת פנימי (Understood - קיים)</Radio.Button>
            <Radio.Button value="external">אתר חיצוני</Radio.Button>
          </Radio.Group>
        </Space>

        {external && (
          <Space direction="vertical" style={{ width: "100%" }}>
            <Input addonBefore="כתובת האתר" placeholder="https://example.onrender.com" dir="ltr"
              value={config.external.url} onChange={(e) => updateExternal({ url: e.target.value })} />
            <Input.Password addonBefore="API Key" dir="ltr"
              value={config.external.apiKey} onChange={(e) => updateExternal({ apiKey: e.target.value })} />
            <Space>
              <Text>פורמט:</Text>
              <Select value={config.external.format} onChange={(v) => updateExternal({ format: v })} style={{ width: 260 }}
                options={[
                  { value: "sionyx", label: "Sionyx (‎/logs/ingest)" },
                  { value: "channel", label: "TheChannel (‎/api/import/post)" },
                ]} />
            </Space>
            <Alert type="info" showIcon
              message="הלוגים שנשלחים לאתר חיצוני נצפים באתר עצמו - הרשימה למטה מציגה רק את השרת הפנימי." />
          </Space>
        )}

        <Space wrap>
          <Switch checked={config.autoEnabled} onChange={(v) => update({ autoEnabled: v })} />
          <Text>שליחה אוטומטית רציפה</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {config.autoEnabled ? "פעילה - שגיאות ואזהרות נשלחות כל הזמן" : "כבויה - לוגים נשלחים רק בלחיצה על \"שלח עכשיו\""}
          </Text>
        </Space>

        {config.autoEnabled && (
          <Space>
            <Text>מרווח מינימלי בין שורות:</Text>
            <InputNumber min={0} step={500} addonAfter="ms" value={config.intervalMs}
              onChange={(v) => update({ intervalMs: v || 0 })} />
          </Space>
        )}

        <Space wrap>
          <Button type="primary" icon={<SaveOutlined />} loading={saving} disabled={!dirty} onClick={handleSave}>שמור הגדרות</Button>
          <Popconfirm title="לבקש לוג מכל המחשבים עכשיו?" onConfirm={handleSendAll} okText="שלח" cancelText="ביטול">
            <Button icon={<SendOutlined />} loading={sendingAll}>שלח לוגים עכשיו מכל המחשבים</Button>
          </Popconfirm>
        </Space>
      </Space>
    </Card>
  );
};

export default OwnerLogSettingsCard;
