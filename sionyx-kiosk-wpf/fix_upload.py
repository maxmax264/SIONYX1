content = open('upload_release.py', encoding='utf-8').read()
old = '''if __name__ == "__main__":
    main()'''
new = '''if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        sys.exit(1)'''
if old in content:
    open('upload_release.py', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK')
else:
    print('NOT FOUND')
