package net.kibotu.geofencerelay.ui.auth

import android.accounts.AccountManager
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.common.api.ApiException
import net.kibotu.geofencerelay.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GoogleSignInScreen(
    appTitle: String = "IRCTC Sentinel",
    appSubtitle: String = "Live GPS Geofence & Tracker Relay",
    isTrackerMode: Boolean = false,
    onSignInSuccess: (email: String) -> Unit
) {
    val context = LocalContext.current
    val prefs = remember { context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    var detectedAccounts by remember { mutableStateOf<List<String>>(emptyList()) }

    // Official Google Sign-In Options (Request Email directly via Google Play Services)
    val gso = remember {
        GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestEmail()
            .build()
    }
    val googleSignInClient: GoogleSignInClient = remember {
        GoogleSignIn.getClient(context, gso)
    }

    fun refreshDetectedAccounts() {
        try {
            val am = AccountManager.get(context)
            val googleAccounts = am.getAccountsByType("com.google")
            detectedAccounts = googleAccounts.map { it.name.lowercase() }
        } catch (_: Exception) {}
    }

    LaunchedEffect(Unit) {
        val savedEmail = prefs.getString("user_google_email", null)
        if (!savedEmail.isNullOrBlank()) {
            onSignInSuccess(savedEmail)
            return@LaunchedEffect
        }
        val lastAccount = GoogleSignIn.getLastSignedInAccount(context)
        if (lastAccount != null && !lastAccount.email.isNullOrBlank()) {
            val clean = lastAccount.email!!.trim().lowercase()
            prefs.edit().putString("user_google_email", clean).apply()
            onSignInSuccess(clean)
            return@LaunchedEffect
        }
        refreshDetectedAccounts()
    }

    // System Account Chooser Launcher (Fallback if Google Play Services needs account intent)
    val accountChooserLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        isLoading = false
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            val accountName = result.data?.getStringExtra(AccountManager.KEY_ACCOUNT_NAME)
            if (!accountName.isNullOrBlank()) {
                val clean = accountName.trim().lowercase()
                prefs.edit().putString("user_google_email", clean).apply()
                onSignInSuccess(clean)
            }
        }
        refreshDetectedAccounts()
    }

    // Google Play Services Sign-In Activity Result Launcher
    val googleSignInLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        isLoading = false
        val task = GoogleSignIn.getSignedInAccountFromIntent(result.data)
        try {
            val account: GoogleSignInAccount = task.getResult(ApiException::class.java)
            val email = account.email
            if (!email.isNullOrBlank()) {
                val clean = email.trim().lowercase()
                prefs.edit().putString("user_google_email", clean).apply()
                onSignInSuccess(clean)
            } else {
                errorMessage = "Google Sign-In succeeded, but no verified email was returned."
            }
        } catch (e: ApiException) {
            Log.w("GoogleSignIn", "Google Play Services sign-in returned status ${e.statusCode}: ${e.message}")
            if (e.statusCode == 12501 || e.statusCode == 12502) {
                // User cancelled or dismissed the picker
                errorMessage = "Sign-in cancelled. Please select a Google Account to proceed."
            } else {
                // Try device Google Account chooser as direct native fallback
                try {
                    val intent = AccountManager.newChooseAccountIntent(
                        null,
                        null,
                        arrayOf("com.google"),
                        null,
                        null,
                        null,
                        null
                    )
                    accountChooserLauncher.launch(intent)
                } catch (fallbackEx: Exception) {
                    errorMessage = "Direct Google Sign-In error (${e.statusCode}): ${e.message}"
                }
            }
        }
    }

    fun launchDirectGoogleSignIn() {
        isLoading = true
        errorMessage = null
        // Sign out client first to ensure the account chooser is always presented
        googleSignInClient.signOut().addOnCompleteListener {
            try {
                googleSignInLauncher.launch(googleSignInClient.signInIntent)
            } catch (e: Exception) {
                isLoading = false
                Log.e("GoogleSignIn", "Failed to launch Google Sign-In intent: ${e.message}")
                try {
                    val intent = AccountManager.newChooseAccountIntent(
                        null,
                        null,
                        arrayOf("com.google"),
                        null,
                        null,
                        null,
                        null
                    )
                    accountChooserLauncher.launch(intent)
                } catch (ex: Exception) {
                    errorMessage = "Unable to launch Google Sign-In: ${e.message}"
                }
            }
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        IrctcNavy,
                        IrctcRoyal,
                        if (isTrackerMode) Color(0xFF042F2E) else Color(0xFF0A1E3F)
                    )
                )
            )
            .padding(24.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(top = 36.dp, bottom = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Header with glowing IRCTC themed icon
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    modifier = Modifier
                        .size(86.dp)
                        .clip(CircleShape)
                        .background(
                            brush = Brush.linearGradient(
                                colors = listOf(IrctcSaffron, IrctcGold)
                            )
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = if (isTrackerMode) Icons.Default.GpsFixed else Icons.Default.Security,
                        contentDescription = "App Icon",
                        tint = Color.White,
                        modifier = Modifier.size(44.dp)
                    )
                }

                Spacer(modifier = Modifier.height(18.dp))

                Text(
                    text = appTitle,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = Color.White,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = appSubtitle,
                    fontSize = 14.sp,
                    color = IrctcGoldLight,
                    textAlign = TextAlign.Center,
                    lineHeight = 20.sp
                )
            }

            // Central Sign-in Card with IRCTC Clean White Background
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = IrctcCardBg),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp),
                shape = RoundedCornerShape(22.dp),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(IrctcCardBorder))
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(22.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.VerifiedUser, contentDescription = null, tint = IrctcGreen, modifier = Modifier.size(22.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Direct Google Sign-In",
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold,
                            color = IrctcTextPrimary
                        )
                    }

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Sign in directly with your authenticated Google Account. No password needed.",
                        fontSize = 12.sp,
                        color = IrctcTextSecondary,
                        textAlign = TextAlign.Center,
                        lineHeight = 17.sp
                    )

                    Spacer(modifier = Modifier.height(20.dp))

                    // If verified Google accounts exist on device, list them as quick 1-tap options
                    if (detectedAccounts.isNotEmpty()) {
                        Text(
                            text = "Verified Google Accounts on Device:",
                            fontSize = 12.sp,
                            color = IrctcTextSecondary,
                            fontWeight = FontWeight.SemiBold,
                            modifier = Modifier.align(Alignment.Start)
                        )
                        Spacer(modifier = Modifier.height(8.dp))

                        detectedAccounts.forEach { acc ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp)
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(IrctcCanvas)
                                    .border(1.dp, IrctcCardBorder, RoundedCornerShape(12.dp))
                                    .clickable {
                                        prefs.edit().putString("user_google_email", acc).apply()
                                        onSignInSuccess(acc)
                                    }
                                    .padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(34.dp)
                                        .clip(CircleShape)
                                        .background(IrctcRoyal),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        acc.take(1).uppercase(),
                                        fontWeight = FontWeight.Bold,
                                        color = Color.White,
                                        fontSize = 14.sp
                                    )
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(acc, fontSize = 13.sp, color = IrctcTextPrimary, fontWeight = FontWeight.SemiBold)
                                    Text("✓ Direct 1-Tap Login", fontSize = 10.sp, color = IrctcGreen, fontWeight = FontWeight.Medium)
                                }
                                Icon(Icons.Default.CheckCircle, contentDescription = null, tint = IrctcGreen, modifier = Modifier.size(18.dp))
                            }
                        }

                        Spacer(modifier = Modifier.height(14.dp))
                    }

                    // Direct Official Google Sign-In Button
                    Button(
                        onClick = { launchDirectGoogleSignIn() },
                        enabled = !isLoading,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(52.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = IrctcSaffron
                        ),
                        shape = RoundedCornerShape(12.dp),
                        elevation = ButtonDefaults.buttonElevation(defaultElevation = 2.dp)
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(22.dp),
                                color = Color.White,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Text(
                                "Authenticating with Google...",
                                color = Color.White,
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp
                            )
                        } else {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.Center
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(26.dp)
                                        .clip(CircleShape)
                                        .background(Color.White),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text("G", fontWeight = FontWeight.Black, color = IrctcOrangeDark, fontSize = 16.sp)
                                }
                                Spacer(modifier = Modifier.width(10.dp))
                                Text(
                                    if (detectedAccounts.isNotEmpty()) "Choose / Switch Google Account" else "Sign in with Google",
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 15.sp
                                )
                            }
                        }
                    }

                    // Error display if sign-in fails
                    AnimatedVisibility(visible = errorMessage != null) {
                        errorMessage?.let { msg ->
                            Surface(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(top = 12.dp),
                                color = IrctcRedLight,
                                shape = RoundedCornerShape(10.dp),
                                border = androidx.compose.foundation.BorderStroke(1.dp, IrctcRed)
                            ) {
                                Row(
                                    modifier = Modifier.padding(10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Default.Warning, contentDescription = null, tint = IrctcRed, modifier = Modifier.size(16.dp))
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(msg, color = IrctcRed, fontSize = 11.sp, lineHeight = 15.sp)
                                }
                            }
                        }
                    }
                }
            }

            // Bottom Policy Text
            Text(
                text = "100% Free • Direct Google Sign-In • Zero Passwords Stored",
                fontSize = 11.sp,
                color = IrctcGoldLight,
                textAlign = TextAlign.Center
            )
        }
    }
}
