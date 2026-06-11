content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\chatService.js', encoding='utf-8').read()

old = """    const messages = Object.keys(messagesData).map(key => ({
      id: key,
      ...messagesData[key],
    }));

    // Sort by timestamp (newest first)
    messages.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    return {
      success: true,
      messages,
    };
  } catch (error) {
    logger.error('Error getting user messages:', error);"""

new = """    const messages = Object.keys(messagesData)
      .map(key => ({ id: key, ...messagesData[key] }))
      .filter(msg => !msg.fromSupervisor);

    // Sort by timestamp (newest first)
    messages.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    return {
      success: true,
      messages,
    };
  } catch (error) {
    logger.error('Error getting user messages:', error);"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\services\chatService.js', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
