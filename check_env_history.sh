#!/bin/bash
# שלב 1: אבחון בלבד - הסקריפט הזה לא משנה שום דבר, רק בודק ומדפיס.
# הרץ אותו מתוך תיקיית הריפו (זה שבו רוצים לבדוק את ה-.env)

echo "=================================================="
echo "  בדיקת חשיפת .env בריפו: $(basename "$(pwd)")"
echo "=================================================="
echo ""

echo "--- 1) האם יש קובץ .env כרגע בתיקייה (working tree)? ---"
find . -maxdepth 3 -iname "*.env*" -not -path "./.git/*" 2>/dev/null
if [ -z "$(find . -maxdepth 3 -iname '*.env*' -not -path './.git/*' 2>/dev/null)" ]; then
  echo "(לא נמצא קובץ env בתיקייה הנוכחית)"
fi
echo ""

echo "--- 2) האם git עוקב (tracked) אחרי .env? אם זה מופיע, .env נמצא תחת מעקב git ---"
git ls-files | grep -i "\.env" 
if [ $? -ne 0 ]; then
  echo "(git לא עוקב אחרי שום קובץ env - טוב סימן)"
fi
echo ""

echo "--- 3) האם .env מופיע בהיסטוריה (בכל commit, בכל branch)? זה הבדיקה הקריטית ---"
git log --all --full-history --pretty=format:"COMMIT:%h %ad" --date=short --name-only | grep -B1 -i "\.env" 
if [ $? -ne 0 ]; then
  echo "(.env לא נמצא בשום commit בהיסטוריה - מעולה!)"
fi
echo ""

echo "--- 4) רשימת כל שמות הקבצים שאי פעם היו ברפו (לבדיקה ידנית, חפש .env) ---"
git log --all --pretty=format: --name-only --diff-filter=A 2>/dev/null | sort -u | grep -i env
if [ $? -ne 0 ]; then
  echo "(לא נמצאו קבצים עם 'env' בשם בכל ההיסטוריה)"
fi
echo ""

echo "--- 5) האם .gitignore קיים, והאם הוא כולל .env? ---"
if [ -f .gitignore ]; then
  echo "[.gitignore קיים, תוכן רלוונטי:]"
  grep -i "env" .gitignore
  if [ $? -ne 0 ]; then
    echo "אזהרה: .gitignore קיים אבל לא מכיל 'env' - .env לא מוגן!"
  fi
else
  echo "אזהרה: אין קובץ .gitignore בריפו הזה!"
fi
echo ""

echo "=================================================="
echo "  סיום בדיקה. שלח את כל הפלט הזה בחזרה."
echo "=================================================="
