content = open(r'.\tests\SionyxKiosk.Tests\Services\AuthServiceFinalCoverageTests.cs', encoding='utf-8').read()
old = """        // Use a fixed known computer ID that matches what ComputerService returns
        var computerId = DeviceInfo.GetDeviceId();

        _handler.When("users/uid-same.json", new
        {
            firstName = "Test",
            lastName = "User",
            isLoggedIn = true,
            currentComputerId = computerId, // Same computer
        });
        // Register the computer ID in handler so AssociateUser calls succeed
        _handler.SetDefaultSuccess();"""
new = """        // Use a fixed known computer ID that matches what ComputerService returns
        var computerId = DeviceInfo.GetDeviceId();

        _handler.When("users/uid-same.json", new
        {
            firstName = "Test",
            lastName = "User",
            isLoggedIn = true,
            currentComputerId = computerId, // Same computer
        });"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\tests\SionyxKiosk.Tests\Services\AuthServiceFinalCoverageTests.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
