import { useEffect, useState } from "react";
import { Row, Col, List, Card, Tag, Button, Empty, Spin, App, Popconfirm, Typography, Space, Input } from "antd";
import { ReloadOutlined, DeleteOutlined, CheckCircleOutlined, CloseCircleOutlined, SearchOutlined, CopyOutlined } from "@ant-design/icons";
import { getLogComputers, getComputerLogs, deleteComputerLogs, deleteAllLogs } from "../services/ownerLogService";
import dayjs from "dayjs";

const { Text } = Typography;

const LEVEL_COLORS = {
  Fatal: "red",
  Error: "red",
  Warning: "orange",
  Information: "blue",
  Debug: "default",
  Verbose: "default",
};

/**
 * Owner-only "לוגים" tab: pc-sion.web.app/owner is the ONLY place these are
 * readable from - kiosks ship straight to the Understood bridge's Redis-
 * backed /logs endpoints (capped ring buffer + TTL per computer, so this
 * can never fill up storage the way the old entertainment-channel dump
 * did - no manual cleanup required, though per-computer/bulk delete is
 * still available here for explicit control).
 */
const OwnerLogsTab = () => {
  const { message } = App.useApp();
  const [computers, setComputers] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const loadComputers = async () => {
    setLoadingList(true);
    const result = await getLogComputers();
    if (result.success) setComputers(result.computers || []);
    else message.error(result.error || "שגיאה בטעינת רשימת המחשבים");
    setLoadingList(false);
  };

  useEffect(() => { loadComputers(); }, []);

  const openComputer = async (id) => {
    setSelectedId(id);
    setLoadingDetail(true);
    const result = await getComputerLogs(id);
    if (result.success) setDetail(result);
    else { message.error(result.error || "שגיאה בטעינת הלוגים"); setDetail(null); }
    setLoadingDetail(false);
  };

  const handleDeleteOne = async (id) => {
    const result = await deleteComputerLogs(id);
    if (result.success) {
      message.success("הלוגים נמחקו");
      if (selectedId === id) { setSelectedId(null); setDetail(null); }
      loadComputers();
    } else {
      message.error(result.error || "מחיקה נכשלה");
    }
  };

  const handleDeleteAll = async () => {
    const result = await deleteAllLogs();
    if (result.success) {
      message.success(`נמחקו לוגים של ${result.deleted ?? 0} מחשבים`);
      setSelectedId(null);
      setDetail(null);
      loadComputers();
    } else {
      message.error(result.error || "מחיקה נכשלה");
    }
  };

  const filteredComputers = computers.filter((c) =>
    !search || (c.name || c.id).toLowerCase().includes(search.toLowerCase())
  );

  const handleCopyLog = async () => {
    const lines = detail?.lines || [];
    if (!lines.length) return;
    const text = lines
      .map((line) => {
        const ts = line.timestamp ? dayjs(line.timestamp).format("DD/MM HH:mm:ss") : "";
        return `[${line.level || "-"}] ${ts} ${line.message || ""}`;
      })
      .join("\n");
    try {
      await navigator.clipboard.writeText(text);
      message.success("הלוג הועתק");
    } catch {
      message.error("ההעתקה נכשלה");
    }
  };

  const statusEntries = detail ? Object.entries(detail.status || {}) : [];

  return (
    <Row gutter={16}>
      <Col span={8}>
        <Card
          size="small"
          title={`מחשבים (${computers.length})`}
          extra={<Button size="small" icon={<ReloadOutlined />} onClick={loadComputers} />}
          styles={{ body: { padding: 0 } }}
        >
          <div style={{ padding: "8px 12px" }}>
            <Input
              placeholder="חיפוש מחשב"
              prefix={<SearchOutlined />}
              size="small"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              allowClear
            />
          </div>
          {loadingList ? (
            <div style={{ textAlign: "center", padding: 24 }}><Spin /></div>
          ) : computers.length === 0 ? (
            <Empty description="אין עדיין לוגים משום מחשב" style={{ padding: 24 }} />
          ) : (
            <List
              size="small"
              dataSource={filteredComputers}
              style={{ maxHeight: 480, overflowY: "auto" }}
              renderItem={(c) => (
                <List.Item
                  onClick={() => openComputer(c.id)}
                  style={{
                    cursor: "pointer",
                    padding: "8px 12px",
                    background: selectedId === c.id ? "#f0f5ff" : undefined,
                  }}
                  actions={[
                    <Popconfirm
                      key="del"
                      title="למחוק את הלוגים של המחשב הזה?"
                      onConfirm={(e) => { e?.stopPropagation?.(); handleDeleteOne(c.id); }}
                      onCancel={(e) => e?.stopPropagation?.()}
                    >
                      <Button size="small" danger type="text" icon={<DeleteOutlined />} onClick={(e) => e.stopPropagation()} />
                    </Popconfirm>,
                  ]}
                >
                  <Text>{c.name || c.id}</Text>
                </List.Item>
              )}
            />
          )}
          <div style={{ padding: 12, borderTop: "1px solid #f0f0f0" }}>
            <Popconfirm
              title="למחוק את הלוגים של כל המחשבים?"
              description="פעולה זו בלתי הפיכה"
              onConfirm={handleDeleteAll}
              okButtonProps={{ danger: true }}
            >
              <Button danger block icon={<DeleteOutlined />}>מחק את כל הלוגים</Button>
            </Popconfirm>
          </div>
        </Card>
      </Col>
      <Col span={16}>
        {!selectedId ? (
          <Card size="small"><Empty description="בחר מחשב כדי לראות את הלוגים שלו" /></Card>
        ) : loadingDetail ? (
          <Card size="small"><div style={{ textAlign: "center", padding: 40 }}><Spin size="large" /></div></Card>
        ) : (
          <>
            {statusEntries.length > 0 && (
              <Card size="small" title="סטטוס התקנות" style={{ marginBottom: 12 }}>
                <Space direction="vertical" style={{ width: "100%" }}>
                  {statusEntries.map(([feature, s]) => (
                    <div key={feature} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <Space>
                        {s.success ? <CheckCircleOutlined style={{ color: "#52c41a" }} /> : <CloseCircleOutlined style={{ color: "#ff4d4f" }} />}
                        <Text strong>{feature}</Text>
                        {s.message && <Text type="secondary" style={{ fontSize: 12 }}>{s.message}</Text>}
                      </Space>
                      <Tag color={s.success ? "green" : "red"}>{s.success ? "הצליח" : "נכשל"}</Tag>
                    </div>
                  ))}
                </Space>
              </Card>
            )}
            <Card
              size="small"
              title={`לוג גולמי (${detail?.lines?.length || 0} שורות אחרונות)`}
              extra={
                <Space size="small">
                  <Button
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={handleCopyLog}
                    disabled={!detail?.lines?.length}
                  >
                    העתק
                  </Button>
                  <Button size="small" icon={<ReloadOutlined />} onClick={() => openComputer(selectedId)} />
                </Space>
              }
            >
              {!detail?.lines?.length ? (
                <Empty description="אין שורות לוג" />
              ) : (
                <div style={{ maxHeight: 480, overflowY: "auto", direction: "ltr", fontFamily: "monospace", fontSize: 12 }}>
                  {detail.lines.map((line, i) => (
                    <div key={i} style={{ padding: "3px 6px", borderBottom: "1px solid #f5f5f5", display: "flex", gap: 8 }}>
                      <Tag color={LEVEL_COLORS[line.level] || "default"} style={{ flexShrink: 0 }}>{line.level || "-"}</Tag>
                      <Text type="secondary" style={{ flexShrink: 0, whiteSpace: "nowrap" }}>
                        {line.timestamp ? dayjs(line.timestamp).format("DD/MM HH:mm:ss") : ""}
                      </Text>
                      <Text style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{line.message}</Text>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </>
        )}
      </Col>
    </Row>
  );
};

export default OwnerLogsTab;
