# SIH CogniCare — Real-Time GPS Tracking & Geofencing Sentinel

An enterprise-grade, zero-cost Android tracking and geofence monitoring system built for the **SIH CogniCare (PS 26003)** cognitive care platform. Designed to safeguard dementia, Alzheimer's, and elderly care patients from wandering while giving caregivers real-time location visibility.

---

## Key Highlights

- **100% Free & Zero-Cost Stack**: No Google Cloud API billing, no Firebase subscriptions, and no paid mapping tiers. Uses open-standard **OpenStreetMap (osmdroid)** and public **EMQX MQTT telemetry**.
- **Dual App Architecture**:
  - **Tracker Beacon (`trackerDebug`)**: Runs on the patient's phone as an Android Foreground Service with continuous stationary heartbeats, auto-recovery on boot, and background location streaming.
  - **Guardian Sentinel (`guardianDebug`)**: Runs on the caregiver's phone with live radar map visualization, boundary breach alerts, remote Find My sound trigger, and one-tap directions.
- **Google Account Authorization**: Direct Google Sign-In with fine-grained access control—only authorized caregiver emails can stream the patient's live telemetry.
- **Auto GPS Hardware Resolution**: Automatically detects if system GPS is off and prompts Google Play Services' 1-tap activation dialog.
- **IRCTC RailConnect Vibrant Theme**: High-contrast, accessibility-first design palette optimized for all lighting conditions.

---

## Architecture

```
[ Patient / Tracker Device ]                   [ Caregiver / Guardian Device ]
          |                                                   |
          | 1. Starts Foreground Service                     | 1. Sets Safe Zone (e.g., Home 300m)
          | 2. Checks Geofence boundary                       | 2. Connects to Live Radar
          v                                                   v
  +-------------------------------------------------------------+
  |              Global EMQX MQTT Telemetry Relay               |
  |         bmtc_findmy/v2/{authorized_account_email}/#         |
  +-------------------------------------------------------------+
          |                                                   ^
          | 3. Transmits Live Telemetry Ping (every 3s)        | 4. Delivers Coordinates & Battery
          +---------------------------------------------------+
                                                              |
                                                    - Red Marker Pin on OSM
                                                    - Distance & Speed Badges
                                                    - ?? BREACH Alarm on Exit
                                                    - Remote Audio Alarm Trigger
```

---

## Project Structure

```
gps_tracking/
??? app/
?   ??? src/main/
?   ?   ??? java/net/kibotu/geofencerelay/
?   ?   ?   ??? model/            # Data models (LocationPing, GeofenceZone, BreachAlert, RemoteCommand)
?   ?   ?   ??? relay/            # MQTT Relay Client (broker.emqx.io)
?   ?   ?   ??? service/          # TrackerForegroundService, BootReceiver
?   ?   ?   ??? ui/               # Jetpack Compose UI (GuardianScreen, TrackerMainScreen, OsmMapView)
?   ?   ?   ??? util/             # LocationUtils, BatteryUtils, SoundPlayer, NotificationHelper
?   ?   ??? res/                  # Drawable icons, colors, themes, network configs
?   ?   ??? AndroidManifest.xml
?   ??? build.gradle.kts          # App-level build config (dependencies, flavors)
??? gradle/                       # Gradle wrapper distribution
??? build.gradle.kts              # Root project build config
??? settings.gradle.kts           # Module definitions
??? gradle.properties
??? gradlew / gradlew.bat
```

---

## How to Build

From this directory (`gps_tracking`):

```bash
# Build Tracker Beacon APK (Phone 1)
./gradlew assembleTrackerDebug

# Build Guardian Sentinel APK (Phone 2)
./gradlew assembleGuardianDebug

# Or build both simultaneously
./gradlew assembleDebug
```

Built APK outputs:
- `app/build/outputs/apk/tracker/debug/app-tracker-debug.apk`
- `app/build/outputs/apk/guardian/debug/app-guardian-debug.apk`

---

## Testing on 2 Physical Devices

1. **Install APKs**: Install `app-tracker-debug.apk` on Phone 1 (Patient) and `app-guardian-debug.apk` on Phone 2 (Caregiver).
2. **On Phone 1 (Patient / Tracker)**:
   - Sign in with Google (e.g. `patient@gmail.com`).
   - Tap **Start Live Broadcasting**, grant Fine Location & background permission ("Allow all the time").
   - Under **Who Can View My Location**, tap `+` and add the caregiver's email (e.g. `caregiver@gmail.com`).
3. **On Phone 2 (Caregiver / Guardian)**:
   - Sign in with Google using `caregiver@gmail.com`.
   - The live radar immediately displays the patient's position on OpenStreetMap, live battery %, distance, and status.
