# SIONYX connection monitor

Live view of how many Firebase streams each kiosk / InputInjector holds.
Runs on Render. Uses **no Firebase**: kiosks POST a heartbeat over plain HTTP
and state is kept in this process's RAM.

## Deploy on Render
1. New **Web Service** from this repo, root directory `monitor-server`.
2. Build command `npm install`, start command `npm start`.
3. Environment variables:
   - `REPORT_KEY` - shared secret the kiosks send (any long random string)
   - `DASH_PASSWORD` - password for the dashboard (user name is ignored)
4. Open the service URL, enter the password.

## Enable on the kiosks
Put the service URL and `REPORT_KEY` into `MonitorUrl` / `MonitorKey` in
`src/SionyxKiosk/Infrastructure/ConnectionReporter.cs` (empty = disabled),
or set the `SIONYX_MONITOR_URL` / `SIONYX_MONITOR_KEY` environment variables.
Rebuild and release. Each process then reports every 15s.

Note: free Render instances sleep after inactivity; the first heartbeat wakes
them. History is in memory and resets on restart.
