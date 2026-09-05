package net.kibotu.geofencerelay.ui

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.runtime.*
import net.kibotu.geofencerelay.BuildConfig
import net.kibotu.geofencerelay.ui.auth.GoogleSignInScreen
import net.kibotu.geofencerelay.ui.guardian.GuardianScreen
import net.kibotu.geofencerelay.ui.home.HomeScreen
import net.kibotu.geofencerelay.ui.navigation.AppScreen
import net.kibotu.geofencerelay.ui.theme.GeofenceRelayTheme
import net.kibotu.geofencerelay.ui.tracker.TrackerMainScreen
import net.kibotu.geofencerelay.util.NotificationHelper

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        NotificationHelper.createNotificationChannels(this)

        setContent {
            GeofenceRelayTheme {
                val context = this
                val prefs = remember { getSharedPreferences("auth_prefs", Context.MODE_PRIVATE) }
                val flavor = BuildConfig.FLAVOR

                var currentScreen by remember {
                    val savedEmail = prefs.getString("user_google_email", null)
                    val initialScreen: AppScreen = when (flavor) {
                        "tracker" -> {
                            if (!savedEmail.isNullOrBlank()) AppScreen.Tracker(savedEmail)
                            else AppScreen.Auth(isTracker = true)
                        }
                        "guardian" -> {
                            if (!savedEmail.isNullOrBlank()) AppScreen.Guardian(savedEmail)
                            else AppScreen.Auth(isTracker = false)
                        }
                        else -> {
                            val savedRole = prefs.getString("user_role", null)
                            if (!savedEmail.isNullOrBlank() && savedRole == "tracker") {
                                AppScreen.Tracker(savedEmail)
                            } else if (!savedEmail.isNullOrBlank() && savedRole == "guardian") {
                                AppScreen.Guardian(savedEmail)
                            } else {
                                AppScreen.RoleSelect
                            }
                        }
                    }
                    mutableStateOf(initialScreen)
                }

                when (val screen = currentScreen) {
                    is AppScreen.RoleSelect -> {
                        HomeScreen(
                            onSelectGuardian = {
                                prefs.edit().putString("user_role", "guardian").apply()
                                val savedEmail = prefs.getString("user_google_email", null)
                                currentScreen = if (!savedEmail.isNullOrBlank()) {
                                    AppScreen.Guardian(savedEmail)
                                } else {
                                    AppScreen.Auth(isTracker = false)
                                }
                            },
                            onSelectTracker = {
                                prefs.edit().putString("user_role", "tracker").apply()
                                val savedEmail = prefs.getString("user_google_email", null)
                                currentScreen = if (!savedEmail.isNullOrBlank()) {
                                    AppScreen.Tracker(savedEmail)
                                } else {
                                    AppScreen.Auth(isTracker = true)
                                }
                            }
                        )
                    }
                    is AppScreen.Auth -> {
                        val isTracker = screen.isTracker
                        GoogleSignInScreen(
                            appTitle = if (isTracker) "Beacon Tracker" else "Find My Guardian",
                            appSubtitle = if (isTracker)
                                "Real-Time Background GPS Sentinel\nTransmits location to authorized accounts"
                            else
                                "Live Radar & Geofence Controller\nTrack devices with real-time GPS fixes",
                            isTrackerMode = isTracker,
                            onSignInSuccess = { email ->
                                prefs.edit().putString("user_google_email", email).apply()
                                currentScreen = if (isTracker) AppScreen.Tracker(email) else AppScreen.Guardian(email)
                            }
                        )
                    }
                    is AppScreen.Guardian -> {
                        BackHandler {
                            if (flavor.isEmpty()) {
                                currentScreen = AppScreen.RoleSelect
                            } else {
                                finish()
                            }
                        }
                        GuardianScreen(
                            googleAccountEmail = screen.email,
                            onBack = {
                                if (flavor.isEmpty()) {
                                    currentScreen = AppScreen.RoleSelect
                                } else {
                                    finish()
                                }
                            },
                            onSignOut = {
                                prefs.edit().clear().apply()
                                try {
                                    val gso = com.google.android.gms.auth.api.signin.GoogleSignInOptions.Builder(
                                        com.google.android.gms.auth.api.signin.GoogleSignInOptions.DEFAULT_SIGN_IN
                                    ).requestEmail().build()
                                    com.google.android.gms.auth.api.signin.GoogleSignIn.getClient(context, gso).signOut()
                                } catch (_: Exception) {}
                                currentScreen = if (flavor.isEmpty()) AppScreen.RoleSelect else AppScreen.Auth(isTracker = false)
                            }
                        )
                    }
                    is AppScreen.Tracker -> {
                        BackHandler {
                            if (flavor.isEmpty()) {
                                currentScreen = AppScreen.RoleSelect
                            } else {
                                finish()
                            }
                        }
                        TrackerMainScreen(
                            userEmail = screen.email,
                            onSignOut = {
                                prefs.edit().clear().apply()
                                try {
                                    val gso = com.google.android.gms.auth.api.signin.GoogleSignInOptions.Builder(
                                        com.google.android.gms.auth.api.signin.GoogleSignInOptions.DEFAULT_SIGN_IN
                                    ).requestEmail().build()
                                    com.google.android.gms.auth.api.signin.GoogleSignIn.getClient(context, gso).signOut()
                                } catch (_: Exception) {}
                                currentScreen = if (flavor.isEmpty()) AppScreen.RoleSelect else AppScreen.Auth(isTracker = true)
                            }
                        )
                    }
                }
            }
        }
    }
}
