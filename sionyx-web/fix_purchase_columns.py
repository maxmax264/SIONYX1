content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = """purchaseColumns = [
    {
      title: 'תאריך',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: date => (date ? dayjs(date).format('MMM D, YYYY HH:mm') : 'לא זמין'),
    },
    {
      title: 'חבילה',
      dataIndex: 'packageName',
      key: 'packageName',
    },
    {
      title: 'סכום',
      dataIndex: 'amount',
      key: 'amount',
      render: price => {
        const numPrice = parseFloat(price) || 0;
        return `₪${numPrice.toFixed(2)}`;
      },
    },
    {
      title: 'סטטוס',
      dataIndex: 'status',
      key: 'status',
      render: status => {
        return <Tag color={getPurchaseStatusColor(status)}>{getPurchaseStatusLabel(status)}</Tag>;
      },
    },
  ];"""

new = """purchaseColumns = [
    {
      title: 'תאריך',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: date => (date ? dayjs(date).format('DD/MM/YYYY HH:mm') : 'לא זמין'),
    },
    {
      title: 'סוג',
      dataIndex: 'type',
      key: 'type',
      render: (type, record) => {
        if (type === 'admin_charge') return <Tag color='blue'>טעינת מפעיל</Tag>;
        return <Tag color='green'>רכישה</Tag>;
      },
    },
    {
      title: 'חבילה / הערה',
      key: 'packageName',
      render: (_, record) => record.packageName || record.note || '—',
    },
    {
      title: 'דקות',
      key: 'timeSeconds',
      render: (_, record) => {
        if (!record.timeSeconds) return '—';
        const mins = Math.floor(Math.abs(record.timeSeconds) / 60);
        return (record.timeSeconds < 0 ? '-' : '+') + mins + ' דק';
      },
    },
    {
      title: 'סכום',
      dataIndex: 'amount',
      key: 'amount',
      render: price => {
        const numPrice = parseFloat(price) || 0;
        return '₪' + numPrice.toFixed(2);
      },
    },
    {
      title: 'סטטוס',
      dataIndex: 'status',
      key: 'status',
      render: status => {
        return <Tag color={getPurchaseStatusColor(status)}>{getPurchaseStatusLabel(status)}</Tag>;
      },
    },
  ];"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
