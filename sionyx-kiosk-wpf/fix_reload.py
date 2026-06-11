content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
old = """            Views.Controls.FloatingNotification.Show(
                toSupervisor ? "תגובה נשלחה לפיקוח"
                             : "תגובה נשלחה למנהל",
                text.Length > 40 ? text[..40] + "..." : text,
                Views.Controls.FloatingNotification.NotificationType.Success, 3000);
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to send reply");
        }
    }
}"""
new = """            Views.Controls.FloatingNotification.Show(
                toSupervisor ? "תגובה נשלחה לפיקוח"
                             : "תגובה נשלחה למנהל",
                text.Length > 40 ? text[..40] + "..." : text,
                Views.Controls.FloatingNotification.NotificationType.Success, 3000);

            await LoadMessagesAsync();
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to send reply");
        }
    }
}"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
