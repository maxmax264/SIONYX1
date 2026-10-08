import { useCallback, useEffect, useState } from "react";
import {
  Alert, App, Button, Card, Col, Descriptions, Form, Input, InputNumber, Modal, Popconfirm, Row, Space, Switch,
  Table, Tag, Typography,
} from "antd";
import { ReloadOutlined, StopOutlined, UnlockOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import {
  getBillingOverview, billingAction, saveBillingConfig, saveBillingApiValid, runBillingForAll,
} from "../services/ownerBillingService";

const { Text } = Typography;
const money = n => `₪${(Math.round((n || 0) * 100) / 100).toLocaleString("he-IL")}`;
const fmtMonth = ym => dayjs(`${ym}-01`).format("MM/YYYY");

const STATE_TAG = {
  free: { color: "blue", text: "חינם" },
  ok: { color: "green", text: "תקין" },
  warning: { color: "gold", text: "אזהרה" },
  blocked: { color: "red", text: "חסום" },
};
const INV_TAG = {
  unpaid: { color: "red", text: "לא שולם" }, claimed: { color: "gold", text: "ממתין לאימות" },
  paid: { color: "green", text: "שולם" }, void: { color: "default", text: "בוטל" },
};

const OwnerBillingTab = () => {
  const { message, modal } = App.useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cfgForm] = Form.useForm();
  const [orgForm] = Form.useForm();
  const [apiValid, setApiValid] = useState("");
  const [contractText, setContractText] = useState("");
  const [editOrg, setEditOrg] = useState(null);
  const [invOrg, setInvOrg] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const d = await getBillingOverview();
      setData(d);
      cfgForm.setFieldsValue(d.config);
      setContractText(d.config.contractText || "");
    } catch (e) {
      message.error(e.message);
    } finally {
      setLoading(false);
    }
  }, [cfgForm, message]);

  useEffect(() => { load(); }, [load]);

  const act = async (orgId, action, params, okText) => {
    try {
      await billingAction(orgId, action, params);
      if (okText) message.success(okText);
      await load();
    } catch (e) {
      message.error(e.message);
    }
  };

  const saveConfig = async values => {
    try {
      await saveBillingConfig({ ...values, contractText });
      message.success("ההגדרות נשמרו");
      load();
    } catch (e) { message.error(e.message); }
  };

  const openEdit = row => {
    setEditOrg(row);
    orgForm.setFieldsValue({
      exempt: row.exempt, pricePerComputer: row.pricePerComputer, minimumMonthly: row.minimumMonthly,
    });
  };
  const saveOrg = async v => {
    await act(editOrg.orgId, "saveSettings", {
      exempt: !!v.exempt, pricePerComputer: v.pricePerComputer ?? null, minimumMonthly: v.minimumMonthly ?? null,
    }, "נשמר");
    setEditOrg(null);
  };

  const blockNow = row => {
    let msg = "";
    modal.confirm({
      title: `לחסום את הדשבורד של ${row.name} מיד?`,
      content: (
        <Input placeholder="הודעה ללקוח (אופציונלי)" onChange={e => { msg = e.target.value; }} />
      ),
      okText: "חסום עכשיו", okButtonProps: { danger: true }, cancelText: "ביטול",
      onOk: () => act(row.orgId, "block", { message: msg }, "הדשבורד נחסם"),
    });
  };

  const columns = [
    { title: "ארגון", dataIndex: "name", render: (v, r) => <div><b>{v}</b><div><Text type="secondary" style={{ fontSize: 12 }}>{r.orgId}</Text></div></div> },
    { title: "מחשבים", dataIndex: "computers", width: 80 },
    {
      title: "סטטוס", dataIndex: "state",
      render: (s, r) => (
        <div>
          <Tag color={STATE_TAG[s]?.color}>{STATE_TAG[s]?.text || "—"}</Tag>
          {r.manualBlock && <Tag color="red">חסימה ידנית</Tag>}
          {s === "warning" && r.blockAt && <div style={{ fontSize: 12 }}>{`נחסם ב-${dayjs(r.blockAt).format("DD/MM")}`}</div>}
        </div>
      ),
    },
    { title: "החודש (הערכה)", dataIndex: "estimate", render: (v, r) => <div>{money(v)}<div style={{ fontSize: 12, color: "#888" }}>{`${r.estimateFull} מלא · ${r.estimateHalf} חצי`}</div></div> },
    { title: "חוב", dataIndex: "amountDue", render: v => (v > 0 ? <Text type="danger">{money(v)}</Text> : money(0)) },
    { title: "שולם", dataIndex: "totalPaid", render: money },
    {
      title: "מחיר", key: "price",
      render: (_, r) => (r.exempt ? "פטור" : (
        <div>
          {r.pricePerComputer != null ? `${money(r.pricePerComputer)} למחשב` : <Text type="secondary">ברירת מחדל</Text>}
          {r.minimumMonthly != null && <div style={{ fontSize: 12 }}>{`מינימום ${money(r.minimumMonthly)}`}</div>}
        </div>
      )),
    },
    { title: "חוזה", key: "c", render: (_, r) => (r.exempt ? "—" : r.contractAccepted ? <Tag color="green">{r.contractBy || "חתום"}</Tag> : <Tag>לא חתום</Tag>) },
    {
      title: "פעולות", key: "a", width: 330,
      render: (_, r) => (
        <Space wrap size={4}>
          <Button size="small" onClick={() => openEdit(r)}>מחיר / חינם</Button>
          <Button size="small" onClick={() => setInvOrg(r)}>חשבוניות</Button>
          {r.manualBlock || r.state === "blocked" ? (
            <Button size="small" type="primary" icon={<UnlockOutlined />}
              onClick={() => act(r.orgId, r.manualBlock ? "unblock" : "extendGrace", r.manualBlock ? {} : { days: 7 }, r.manualBlock ? "החסימה הוסרה" : "הוארך ב-7 ימים")}>
              {r.manualBlock ? "שחרר" : "הארך 7 ימים"}
            </Button>
          ) : (
            !r.exempt && <Button size="small" danger icon={<StopOutlined />} onClick={() => blockNow(r)}>חסום עכשיו</Button>
          )}
        </Space>
      ),
    },
  ];

  const invColumns = [
    { title: "חודש", dataIndex: "month", render: fmtMonth },
    { title: "סכום", dataIndex: "amount", render: money },
    { title: "שולם", dataIndex: "paidAmount", render: money },
    { title: "פירעון", dataIndex: "dueAt", render: v => dayjs(v).format("DD/MM/YYYY") },
    { title: "סטטוס", dataIndex: "status", render: s => <Tag color={INV_TAG[s]?.color}>{INV_TAG[s]?.text || s}</Tag> },
    {
      title: "", key: "x",
      render: (_, inv) => (inv.status === "paid" || inv.status === "void" ? null : (
        <Space size={4}>
          <Popconfirm title="לסמן כשולם (תשלום חיצוני)?" onConfirm={() => act(invOrg.orgId, "markPaid", { month: inv.month }, "סומן כשולם").then(() => setInvOrg(null))}>
            <Button size="small" type="primary">סמן שולם</Button>
          </Popconfirm>
          <Popconfirm title="לחשב מחדש לפי המחיר והשימוש הנוכחיים?" onConfirm={() => act(invOrg.orgId, "reissueInvoice", { month: inv.month }, "החשבונית חושבה מחדש").then(() => setInvOrg(null))}>
            <Button size="small">חשב מחדש</Button>
          </Popconfirm>
          <Popconfirm title="לבטל חשבונית?" onConfirm={() => act(invOrg.orgId, "voidInvoice", { month: inv.month }, "בוטלה").then(() => setInvOrg(null))}>
            <Button size="small" danger>בטל</Button>
          </Popconfirm>
        </Space>
      )),
    },
  ];

  const totals = (data?.rows || []).reduce((t, r) => ({ due: t.due + r.amountDue, paid: t.paid + r.totalPaid, est: t.est + (r.exempt ? 0 : r.estimate) }), { due: 0, paid: 0, est: 0 });

  return (
    <Space direction="vertical" style={{ width: "100%" }} size={16}>
      {data && !data.apiValidConfigured && (
        <Alert type="warning" showIcon message="טרם הוגדר ApiValid של נדרים - ארגונים לא יוכלו לשלם. הגדר אותו בהגדרות למטה." />
      )}
      <Row gutter={12}>
        <Col xs={8}><Card size="small"><Text type="secondary">חוב פתוח</Text><div style={{ fontSize: 22, fontWeight: 600 }}>{money(totals.due)}</div></Card></Col>
        <Col xs={8}><Card size="small"><Text type="secondary">התקבל</Text><div style={{ fontSize: 22, fontWeight: 600 }}>{money(totals.paid)}</div></Card></Col>
        <Col xs={8}><Card size="small"><Text type="secondary">צפי לחודש הנוכחי</Text><div style={{ fontSize: 22, fontWeight: 600 }}>{money(totals.est)}</div></Card></Col>
      </Row>

      <Card size="small" title="ארגונים" extra={
        <Space>
          <Button size="small" onClick={async () => { await runBillingForAll().catch(e => message.error(e.message)); load(); }}>הפק חיובים / רענן סטטוסים</Button>
          <Button size="small" icon={<ReloadOutlined />} onClick={load} loading={loading} />
        </Space>
      }>
        <Table rowKey="orgId" size="small" columns={columns} dataSource={data?.rows || []} loading={loading}
          pagination={false} scroll={{ x: "max-content" }} />
      </Card>

      <Card size="small" title="הגדרות חיוב כלליות (לכל הארגונים)">
        <Form form={cfgForm} layout="vertical" onFinish={saveConfig}>
          <Row gutter={12}>
            <Col xs={12} md={6}><Form.Item name="pricePerComputer" label="מחיר מחשב (₪)"><InputNumber min={0} step={0.1} style={{ width: "100%" }} /></Form.Item></Col>
            <Col xs={12} md={6}><Form.Item name="minimumMonthly" label="מינימום חודשי לארגון (₪)"><InputNumber min={0} style={{ width: "100%" }} /></Form.Item></Col>
            <Col xs={12} md={6}><Form.Item name="fullMonthThresholdPct" label="% ימי פעילות ל'רוב החודש'"><InputNumber min={1} max={100} style={{ width: "100%" }} /></Form.Item></Col>
            <Col xs={12} md={6}><Form.Item name="trialDays" label="ימי ניסיון לארגון חדש"><InputNumber min={0} style={{ width: "100%" }} /></Form.Item></Col>
            <Col xs={12} md={6}><Form.Item name="graceDays" label="ימים עד חסימה אחרי הפקת חשבונית"><InputNumber min={0} style={{ width: "100%" }} /></Form.Item></Col>
            <Col xs={12} md={6}><Form.Item name="claimWindowDays" label="ימי אימות תשלום"><InputNumber min={0} style={{ width: "100%" }} /></Form.Item></Col>
            <Col xs={12} md={6}><Form.Item name="firstBillableMonth" label="חודש חיוב ראשון (YYYY-MM)"><Input dir="ltr" /></Form.Item></Col>
            <Col xs={12} md={6}><Form.Item name="nedarimMosadId" label="מספר מוסד בנדרים"><Input dir="ltr" /></Form.Item></Col>
          </Row>
          <Form.Item label={`נוסח ההסכם (גרסה ${data?.config?.contractVersion ?? "-"}) - שינוי מחייב כל ארגון לחתום מחדש`}>
            <Input.TextArea rows={7} value={contractText} onChange={e => setContractText(e.target.value)} />
          </Form.Item>
          <Button type="primary" htmlType="submit">שמור הגדרות</Button>
        </Form>
        <div style={{ marginTop: 16 }}>
          <Space.Compact style={{ width: "100%", maxWidth: 520 }}>
            <Input.Password dir="ltr" placeholder="ApiValid של נדרים למוסד שלך (נשמר בצד שרת בלבד)" value={apiValid} onChange={e => setApiValid(e.target.value)} />
            <Button disabled={apiValid.trim().length < 4} onClick={async () => {
              try { await saveBillingApiValid(apiValid); setApiValid(""); message.success("נשמר"); load(); } catch (e) { message.error(e.message); }
            }}>שמור</Button>
          </Space.Compact>
        </div>
      </Card>

      <Modal title={editOrg ? `מחיר - ${editOrg.name}` : ""} open={!!editOrg} onCancel={() => setEditOrg(null)} onOk={() => orgForm.submit()} okText="שמור" cancelText="ביטול">
        <Form form={orgForm} layout="vertical" onFinish={saveOrg}>
          <Form.Item name="exempt" label="ארגון חינם (ללא חיוב, ללא הודעות וללא חסימה)" valuePropName="checked"><Switch /></Form.Item>
          <Form.Item name="pricePerComputer" label="מחיר מחשב מותאם (ריק = ברירת מחדל)"><InputNumber min={0} step={0.1} style={{ width: "100%" }} /></Form.Item>
          <Form.Item name="minimumMonthly" label="מינימום חודשי מותאם (ריק = ברירת מחדל)"><InputNumber min={0} style={{ width: "100%" }} /></Form.Item>
        </Form>
      </Modal>

      <Modal title={invOrg ? `חשבוניות - ${invOrg.name}` : ""} open={!!invOrg} onCancel={() => setInvOrg(null)} footer={null} width={720}>
        {invOrg && (
          <>
            <Descriptions size="small" column={2} style={{ marginBottom: 12 }}>
              <Descriptions.Item label="סוף תקופת ניסיון">{dayjs(invOrg.trialEndsAt).format("DD/MM/YYYY")}</Descriptions.Item>
              <Descriptions.Item label="חוב">{money(invOrg.amountDue)}</Descriptions.Item>
            </Descriptions>
            <Table rowKey="month" size="small" columns={invColumns} dataSource={invOrg.invoices} pagination={false} locale={{ emptyText: "אין חשבוניות" }} />
          </>
        )}
      </Modal>
    </Space>
  );
};

export default OwnerBillingTab;
