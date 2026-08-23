/**
 * Organization registration modal.
 *
 * Extracted from the public LandingPage (where it used to be reachable by
 * anyone visiting "/") so that creating a new organization is only possible
 * from inside the authenticated owner dashboard ("/owner"). The UI itself
 * is unchanged - only where it lives and who can open it.
 */
import { memo } from 'react';
import { motion } from 'framer-motion';
import { Form, Input, Row, Col, Modal } from 'antd';
import {
  TeamOutlined,
  BankOutlined,
  KeyOutlined,
  SafetyOutlined,
  CrownOutlined,
  PhoneOutlined,
  LockOutlined,
  MailOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { AnimatedButton } from '../../components/animated';

const colors = {
  primary: '#667eea',
  warning: '#f59e0b',
};

const OrgRegistrationModal = memo(({ open, onClose, onSubmit, loading, form }) => {
  const inputStyle = {
    textAlign: 'right',
    height: 50,
    fontSize: 15,
    borderRadius: 12,
    width: '100%',
    border: '1.5px solid #e8e8e8',
    transition: 'all 0.2s ease',
  };

  const labelStyle = {
    fontSize: 13,
    fontWeight: 600,
    color: '#444',
    marginBottom: 6,
  };

  const sectionStyle = {
    padding: 'clamp(20px, 4vw, 28px)',
    borderRadius: 18,
    marginBottom: 20,
  };

  return (
    <Modal
      open={open}
      onCancel={onClose}
      footer={null}
      width='95%'
      centered
      className='registration-modal'
      styles={{
        body: {
          padding: 0,
          direction: 'rtl',
          maxHeight: '85vh',
          overflowY: 'auto',
        },
        content: {
          maxWidth: 680,
          margin: '0 auto',
          borderRadius: 24,
          overflow: 'hidden',
        },
      }}
      title={null}
      closable={false}
    >
      {/* Custom Header */}
      <div
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: 'clamp(24px, 5vw, 36px) clamp(20px, 4vw, 32px)',
          textAlign: 'center',
          position: 'relative',
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 16,
            left: 16,
            background: 'rgba(255,255,255,0.2)',
            border: 'none',
            borderRadius: 10,
            width: 36,
            height: 36,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: 18,
            transition: 'background 0.2s',
          }}
          onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.3)')}
          onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.2)')}
        >
          ×
        </button>

        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
          style={{
            width: 72,
            height: 72,
            borderRadius: 18,
            background: 'rgba(255,255,255,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
          }}
        >
          <TeamOutlined style={{ fontSize: 36, color: '#fff' }} />
        </motion.div>

        <h2
          style={{
            color: '#fff',
            margin: '0 0 6px',
            fontSize: 'clamp(1.3rem, 4vw, 1.6rem)',
            fontWeight: 700,
          }}
        >
          הרשמת ארגון חדש
        </h2>
        <p
          style={{
            color: 'rgba(255,255,255,0.85)',
            margin: 0,
            fontSize: 'clamp(0.9rem, 2.5vw, 1rem)',
          }}
        >
          מלא את הפרטים ליצירת ארגון וחשבון מנהל
        </p>
      </div>

      {/* Form Body */}
      <div style={{ padding: 'clamp(20px, 4vw, 32px)' }}>
        <Form form={form} onFinish={onSubmit} layout='vertical' size='large'>
          {/* Organization Details Section */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            style={{
              ...sectionStyle,
              background: 'linear-gradient(135deg, #f8f9ff 0%, #f2f5ff 100%)',
              border: '1px solid #e4e9ff',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 10,
                  background: `${colors.primary}15`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginLeft: 12,
                }}
              >
                <BankOutlined style={{ fontSize: 20, color: colors.primary }} />
              </div>
              <div>
                <h4 style={{ margin: 0, color: '#333', fontSize: 16, fontWeight: 600 }}>
                  פרטי הארגון
                </h4>
                <span style={{ fontSize: 12, color: '#888' }}>מידע בסיסי על הארגון</span>
              </div>
            </div>

            <Form.Item
              name='organizationName'
              label={<span style={labelStyle}>שם הארגון</span>}
              rules={[
                { required: true, message: 'נא להזין שם ארגון' },
                { min: 2, message: 'שם הארגון חייב להכיל לפחות 2 תווים' },
              ]}
            >
              <Input
                prefix={<BankOutlined style={{ color: '#bfbfbf' }} />}
                placeholder='לדוגמה: ישיבת אור החיים'
                style={inputStyle}
              />
            </Form.Item>

            <Row gutter={[16, 0]}>
              <Col xs={24} sm={12}>
                <Form.Item
                  name='nedarimMosadId'
                  label={<span style={labelStyle}>מזהה מוסד NEDARIM (אופציונלי)</span>}
                >
                  <Input
                    prefix={<KeyOutlined style={{ color: '#bfbfbf' }} />}
                    placeholder='ניתן להשלים בהגדרות מאוחר יותר'
                    style={inputStyle}
                  />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  name='nedarimApiValid'
                  label={<span style={labelStyle}>מפתח API של NEDARIM (אופציונלי)</span>}
                >
                  <Input
                    prefix={<SafetyOutlined style={{ color: '#bfbfbf' }} />}
                    placeholder='ניתן להשלים בהגדרות מאוחר יותר'
                    style={inputStyle}
                  />
                </Form.Item>
              </Col>
            </Row>
            <div style={{ fontSize: 12, color: '#888', marginTop: -8, marginBottom: 8 }}>
              ניתן להזין את פרטי החיוב של נדרים פלוס בהמשך מתוך מסך ההגדרות.
            </div>
          </motion.div>

          {/* Admin User Section */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            style={{
              ...sectionStyle,
              background: 'linear-gradient(135deg, #fff9f0 0%, #fff5e6 100%)',
              border: '1px solid #ffe4c4',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 10,
                  background: `${colors.warning}15`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginLeft: 12,
                }}
              >
                <CrownOutlined style={{ fontSize: 20, color: colors.warning }} />
              </div>
              <div>
                <h4 style={{ margin: 0, color: '#333', fontSize: 16, fontWeight: 600 }}>
                  פרטי המנהל הראשי
                </h4>
                <span style={{ fontSize: 12, color: '#888' }}>יצירת חשבון מנהל לארגון</span>
              </div>
            </div>

            <Row gutter={[16, 0]}>
              <Col xs={24} sm={12}>
                <Form.Item
                  name='adminFirstName'
                  label={<span style={labelStyle}>שם פרטי</span>}
                  rules={[{ required: true, message: 'נא להזין שם פרטי' }]}
                >
                  <Input placeholder='שם פרטי' style={inputStyle} />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  name='adminLastName'
                  label={<span style={labelStyle}>שם משפחה</span>}
                  rules={[{ required: true, message: 'נא להזין שם משפחה' }]}
                >
                  <Input placeholder='שם משפחה' style={inputStyle} />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              name='adminPhone'
              label={<span style={labelStyle}>מספר טלפון (ישמש להתחברות)</span>}
              rules={[
                { required: true, message: 'נא להזין מספר טלפון' },
                { pattern: /^0\d{9}$/, message: 'מספר טלפון לא תקין (10 ספרות)' },
              ]}
            >
              <Input
                prefix={<PhoneOutlined style={{ color: '#bfbfbf' }} />}
                placeholder='0501234567'
                style={inputStyle}
                maxLength={10}
              />
            </Form.Item>

            <Form.Item
              name='adminPassword'
              label={<span style={labelStyle}>סיסמה</span>}
              rules={[
                { required: true, message: 'נא להזין סיסמה' },
                { min: 6, message: 'הסיסמה חייבת להכיל לפחות 6 תווים' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                placeholder='לפחות 6 תווים'
                style={inputStyle}
              />
            </Form.Item>

            <Form.Item
              name='adminEmail'
              label={<span style={labelStyle}>אימייל (אופציונלי)</span>}
              rules={[{ type: 'email', message: 'כתובת אימייל לא תקינה' }]}
              style={{ marginBottom: 0 }}
            >
              <Input
                prefix={<MailOutlined style={{ color: '#bfbfbf' }} />}
                placeholder='admin@example.com'
                style={inputStyle}
              />
            </Form.Item>
          </motion.div>

          {/* Submit Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            style={{
              display: 'flex',
              gap: 12,
              justifyContent: 'center',
              flexWrap: 'wrap',
              paddingTop: 8,
            }}
          >
            <AnimatedButton
              variant='ghost'
              onClick={onClose}
              style={{
                color: '#666',
                borderColor: '#ddd',
                background: '#fff',
                minWidth: 100,
                height: 48,
                borderRadius: 12,
              }}
            >
              ביטול
            </AnimatedButton>
            <AnimatedButton
              variant='primary'
              loading={loading}
              onClick={() => form.submit()}
              icon={<RocketOutlined />}
              style={{
                minWidth: 180,
                height: 48,
                borderRadius: 12,
                fontWeight: 600,
              }}
            >
              {loading ? 'יוצר ארגון...' : 'צור ארגון חדש'}
            </AnimatedButton>
          </motion.div>
        </Form>
      </div>
    </Modal>
  );
});

OrgRegistrationModal.displayName = 'OrgRegistrationModal';

export default OrgRegistrationModal;
