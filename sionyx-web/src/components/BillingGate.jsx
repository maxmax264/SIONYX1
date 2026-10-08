import { Alert, Button, Result } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';

const BILLING_PATH = '/admin/billing';

/**
 * Wraps the admin pages. Free orgs (state 'free') and orgs in good standing
 * see nothing at all. Orgs with an open invoice see a countdown banner; once
 * the deadline passes (or the owner blocks the org) the pages are replaced by a
 * blocked screen - for a debt the billing page itself stays reachable so the
 * org can pay, and access returns the instant the payment is recorded.
 */
const BillingGate = ({ billing, children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const onBillingPage = location.pathname === BILLING_PATH;

  if (billing?.state === 'blocked') {
    if (billing.reason === 'unpaid' && onBillingPage) return children;
    const unpaid = billing.reason === 'unpaid';
    return (
      <Result
        status='warning'
        title='הגישה ללוח הבקרה הוגבלה'
        subTitle={
          unpaid
            ? `קיימת יתרה לתשלום${billing.amountDue ? ` בסך ₪${billing.amountDue}` : ''}. לאחר התשלום הגישה תיפתח מיד.`
            : billing.message || 'הגישה ללוח הבקרה הוגבלה על ידי מנהל המערכת. לפרטים נוספים יש לפנות אליו.'
        }
        extra={
          unpaid ? (
            <Button type='primary' size='large' onClick={() => navigate(BILLING_PATH)}>
              מעבר לתשלום
            </Button>
          ) : null
        }
      />
    );
  }

  return (
    <>
      {billing?.state === 'warning' && (
        <Alert
          type='warning'
          showIcon
          style={{ marginBottom: 16 }}
          message={`לוח הבקרה ייחסם בעוד ${billing.daysLeft} ${billing.daysLeft === 1 ? 'יום' : 'ימים'} אם לא יסולק התשלום`}
          description={billing.amountDue ? `יתרה לתשלום: ₪${billing.amountDue}` : undefined}
          action={
            !onBillingPage && (
              <Button size='small' type='primary' onClick={() => navigate(BILLING_PATH)}>
                לתשלום
              </Button>
            )
          }
        />
      )}
      {children}
    </>
  );
};

export default BillingGate;
