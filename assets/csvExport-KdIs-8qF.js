const b=(o,s,c)=>{if(!o||o.length===0)return;const l=s.map(e=>e.title).join(","),i=o.map(e=>s.map(r=>{let t=e[r.dataIndex]??"";return typeof t=="string"&&(t.includes(",")||t.includes('"')||t.includes(`
`))&&(t=`"${t.replace(/"/g,'""')}"`),t}).join(",")),d="\uFEFF"+[l,...i].join(`
`),h=new Blob([d],{type:"text/csv;charset=utf-8;"}),a=URL.createObjectURL(h),n=document.createElement("a");n.href=a,n.download=c.endsWith(".csv")?c:`${c}.csv`,n.click(),URL.revokeObjectURL(a)},g=(o,s,c)=>{if(!o||o.length===0)return;const l=s.map(t=>t.title),i=o.map(t=>s.map(m=>{const x=t[m.dataIndex]??"";return String(x).replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")})),p=`<tr>${l.map(t=>`<th>${t}</th>`).join("")}</tr>`,d=i.map(t=>`<tr>${t.map(m=>`<td>${m}</td>`).join("")}</tr>`).join(""),h=`<!DOCTYPE html>
<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">
<head>
<meta charset="UTF-8">
<!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>Sheet1</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]-->
</head>
<body dir="rtl">
<table border="1">${p}${d}</table>
</body>
</html>`,a="\uFEFF",n=new Blob([a+h],{type:"application/vnd.ms-excel;charset=utf-8;"}),e=URL.createObjectURL(n),r=document.createElement("a");r.href=e,r.download=c.endsWith(".xls")?c:`${c}.xls`,r.click(),URL.revokeObjectURL(e)},f=(o,s,c,l="ייצוא")=>{if(!o||o.length===0)return;const i=s.map(e=>e.title),p=o.map(e=>s.map(r=>{const t=e[r.dataIndex]??"";return String(t).replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")})),d=`<tr>${i.map(e=>`<th>${e}</th>`).join("")}</tr>`,h=p.map(e=>`<tr>${e.map(r=>`<td>${r}</td>`).join("")}</tr>`).join(""),a=`<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
<meta charset="UTF-8">
<title>${l}</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; direction: rtl; }
h1 { font-size: 18px; margin-bottom: 16px; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
th { background: #f5f5f5; font-weight: 600; }
@media print { body { padding: 0; } }
</style>
</head>
<body>
<h1>${l}</h1>
<p>תאריך ייצוא: ${new Date().toLocaleDateString("he-IL")}</p>
<table>${d}${h}</table>
</body>
</html>`,n=window.open("","_blank");n.document.write(a),n.document.close(),n.focus(),setTimeout(()=>{n.print(),n.close()},250)};export{g as a,f as b,b as e};
