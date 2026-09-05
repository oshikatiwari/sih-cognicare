package net.kibotu.geofencerelay.ui.guardian

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import net.kibotu.geofencerelay.ui.theme.*
import net.kibotu.geofencerelay.util.LocationUtils

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GuardianScreen(
    googleAccountEmail: String,
    onBack: () -> Unit,
    onSignOut: () -> Unit = onBack,
    vm: GuardianViewModel = viewModel()
) {
    val context = LocalContext.current

    val notificationPermissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { /* granted */ }

    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    LaunchedEffect(googleAccountEmail) {
        vm.init(googleAccountEmail)
    }

    val isConnected by vm.isConnected.collectAsState()
    val zone by vm.zone.collectAsState()
    val targetPing by vm.targetPing.collectAsState()
    val latestAlert by vm.latestAlert.collectAsState()
    val isBreached by vm.isBreached.collectAsState()
    val broadcastSuccess by vm.broadcastSuccess.collectAsState()
    val recenterTrigger by vm.recenterTrigger.collectAsState()
    val isPlayingSound by vm.isPlayingSound.collectAsState()

    var showZoneEditor by remember { mutableStateOf(false) }
    var sliderRadius by remember(zone.radiusMeters) {
        mutableFloatStateOf(zone.radiusMeters.toFloat().coerceIn(50f, 2000f))
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            "IRCTC Sentinel Guardian",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            googleAccountEmail,
                            fontSize = 12.sp,
                            color = IrctcGold
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Color.White)
                    }
                },
                actions = {
                    // Online / Connecting Indicator
                    Box(
                        modifier = Modifier
                            .padding(end = 8.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (isConnected) IrctcGreen else IrctcRed)
                            .clickable { vm.reconnect() }
                            .padding(horizontal = 10.dp, vertical = 5.dp)
                    ) {
                        Text(
                            text = if (isConnected) "LIVE RADAR" else "CONNECTING... (TAP)",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            letterSpacing = 0.5.sp
                        )
                    }

                    // Sign Out Button
                    IconButton(onClick = {
                        context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE).edit().clear().apply()
                        onSignOut()
                    }) {
                        Icon(Icons.AutoMirrored.Filled.ExitToApp, contentDescription = "Sign Out", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = IrctcNavy)
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(IrctcCanvas)
        ) {
            // Interactive Map View
            OsmMapView(
                modifier = Modifier.fillMaxSize(),
                zone = zone,
                targetPing = targetPing,
                isBreached = isBreached,
                recenterTrigger = recenterTrigger,
                onMapTapped = { lat, lon ->
                    if (showZoneEditor) {
                        vm.updateCenter(lat, lon)
                    }
                }
            )

            // Safe Zone Breach Banner
            AnimatedVisibility(
                visible = isBreached || latestAlert != null,
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(12.dp),
                enter = fadeIn(),
                exit = fadeOut()
            ) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = IrctcRed),
                    shape = RoundedCornerShape(16.dp),
                    elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(Color.White.copy(alpha = 0.2f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Default.Warning, contentDescription = null, tint = Color.White, modifier = Modifier.size(24.dp))
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text("SAFE ZONE BREACH DETECTED!", fontWeight = FontWeight.ExtraBold, color = Color.White, fontSize = 14.sp)
                            Text(
                                "Target is outside '${zone.name}' (${LocationUtils.formatDistance(targetPing?.distanceFromCenter ?: 0.0)} from center).",
                                color = Color.White.copy(alpha = 0.9f),
                                fontSize = 12.sp
                            )
                        }
                    }
                }
            }

            // Floating Recenter Button
            FloatingActionButton(
                onClick = { vm.triggerRecenter() },
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(bottom = 270.dp, end = 16.dp),
                containerColor = IrctcCardBg,
                contentColor = IrctcRoyal,
                shape = CircleShape,
                elevation = FloatingActionButtonDefaults.elevation(defaultElevation = 6.dp)
            ) {
                Icon(Icons.Default.GpsFixed, contentDescription = "Recenter on Device")
            }

            // Bottom IRCTC Clean Control Panel
            Card(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = IrctcCardBg),
                shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 14.dp),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(IrctcCardBorder))
            ) {
                Column(
                    modifier = Modifier
                        .padding(horizontal = 20.dp, vertical = 14.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    // Drawer Handle
                    Box(
                        modifier = Modifier
                            .size(36.dp, 4.dp)
                            .clip(RoundedCornerShape(2.dp))
                            .background(IrctcCardBorder)
                            .align(Alignment.CenterHorizontally)
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    // Device Telemetry Row
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = targetPing?.deviceName ?: "Locating Beacon...",
                                fontSize = 17.sp,
                                fontWeight = FontWeight.Bold,
                                color = IrctcTextPrimary
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = targetPing?.address ?: "Acquiring live GPS fix...",
                                fontSize = 12.sp,
                                color = IrctcTextSecondary,
                                maxLines = 1
                            )
                        }

                        // Battery & Status Badges
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            if (targetPing != null) {
                                Row(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(IrctcGreenLight)
                                        .padding(horizontal = 8.dp, vertical = 4.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = if (targetPing!!.isCharging) Icons.Default.BatteryChargingFull else Icons.Default.BatteryFull,
                                        contentDescription = "Battery",
                                        tint = if (targetPing!!.batteryLevel <= 20) IrctcRed else IrctcGreen,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        "${targetPing!!.batteryLevel}%",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = IrctcTextPrimary
                                    )
                                }
                                Spacer(modifier = Modifier.width(8.dp))
                            }

                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(
                                        if (isBreached) IrctcRed else IrctcGreen
                                    )
                                    .padding(horizontal = 10.dp, vertical = 5.dp)
                            ) {
                                Text(
                                    text = if (isBreached) "BREACH" else "IN ZONE",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // Distance, Speed, Last Ping row
                    if (targetPing != null) {
                        val lastSeen = LocationUtils.formatTime(targetPing!!.timestamp)
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(IrctcCanvas)
                                .border(1.dp, IrctcCardBorder, RoundedCornerShape(10.dp))
                                .padding(horizontal = 12.dp, vertical = 8.dp),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                "Dist: ${LocationUtils.formatDistance(targetPing!!.distanceFromCenter)}",
                                fontSize = 12.sp,
                                color = IrctcRoyal,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                "Speed: ${LocationUtils.formatSpeed(targetPing!!.speed)}",
                                fontSize = 12.sp,
                                color = IrctcTextSecondary
                            )
                            Text(
                                if (lastSeen == "Just now") "Live Ping" else "Seen: $lastSeen",
                                fontSize = 12.sp,
                                color = if (lastSeen == "Just now") IrctcGreen else IrctcTextSecondary,
                                fontWeight = if (lastSeen == "Just now") FontWeight.Bold else FontWeight.Normal
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // 4 Interactive Action Tiles
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        // 1. Play Sound / Alarm
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            modifier = Modifier
                                .weight(1f)
                                .clickable {
                                    if (isPlayingSound) vm.stopSound() else vm.playSound()
                                }
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(50.dp)
                                    .clip(CircleShape)
                                    .background(if (isPlayingSound) IrctcRed else IrctcRoyal),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.AutoMirrored.Filled.VolumeUp, contentDescription = "Play Sound", tint = Color.White)
                            }
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                if (isPlayingSound) "Stop Sound" else "Play Sound",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = IrctcTextPrimary
                            )
                        }

                        // 2. Directions in Google Maps
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            modifier = Modifier
                                .weight(1f)
                                .clickable {
                                    val ping = targetPing
                                    val lat = ping?.latitude ?: zone.latitude
                                    val lon = ping?.longitude ?: zone.longitude
                                    if (lat != 0.0 && lon != 0.0) {
                                        val uri = "google.navigation:q=$lat,$lon"
                                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(uri)).apply {
                                            setPackage("com.google.android.apps.maps")
                                        }
                                        try {
                                            context.startActivity(intent)
                                        } catch (_: Exception) {
                                            val webUri = "https://www.google.com/maps/dir/?api=1&destination=$lat,$lon"
                                            context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(webUri)))
                                        }
                                    }
                                }
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(50.dp)
                                    .clip(CircleShape)
                                    .background(IrctcLightBlue),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Default.Directions, contentDescription = "Directions", tint = Color.White)
                            }
                            Spacer(modifier = Modifier.height(6.dp))
                            Text("Directions", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = IrctcTextPrimary)
                        }

                        // 3. Safe Zone Setup
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            modifier = Modifier
                                .weight(1f)
                                .clickable {
                                    showZoneEditor = !showZoneEditor
                                }
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(50.dp)
                                    .clip(CircleShape)
                                    .background(if (showZoneEditor) IrctcSaffron else IrctcNavy),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Default.Security, contentDescription = "Safe Zone", tint = Color.White)
                            }
                            Spacer(modifier = Modifier.height(6.dp))
                            Text("Safe Zone", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = IrctcTextPrimary)
                        }

                        // 4. Recenter & Sync
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            modifier = Modifier
                                .weight(1f)
                                .clickable {
                                    vm.triggerRecenter()
                                }
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(50.dp)
                                    .clip(CircleShape)
                                    .background(IrctcRoyal),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Default.MyLocation, contentDescription = "Recenter Radar", tint = Color.White)
                            }
                            Spacer(modifier = Modifier.height(6.dp))
                            Text("Center Radar", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = IrctcTextPrimary)
                        }
                    }

                    // Collapsible Safe Geofence Editor
                    AnimatedVisibility(visible = showZoneEditor) {
                        Column(
                            modifier = Modifier
                                .padding(top = 16.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(IrctcCanvas)
                                .border(1.dp, IrctcCardBorder, RoundedCornerShape(16.dp))
                                .padding(16.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    "Geofence Configuration",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 15.sp,
                                    color = IrctcTextPrimary
                                )
                                Text(
                                    "${sliderRadius.toInt()} m radius",
                                    color = IrctcRoyal,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 13.sp
                                )
                            }

                            Spacer(modifier = Modifier.height(4.dp))

                            Text(
                                "Tap anywhere on the map to place center coordinate. Adjust boundary radius with the slider below.",
                                fontSize = 11.sp,
                                color = IrctcTextSecondary,
                                lineHeight = 16.sp
                            )

                            Spacer(modifier = Modifier.height(10.dp))

                            Slider(
                                value = sliderRadius,
                                onValueChange = {
                                    sliderRadius = it
                                    vm.updateRadius(it.toDouble())
                                },
                                valueRange = 50f..2000f,
                                colors = SliderDefaults.colors(
                                    thumbColor = IrctcSaffron,
                                    activeTrackColor = IrctcSaffron,
                                    inactiveTrackColor = IrctcCardBorder
                                )
                            )

                            Spacer(modifier = Modifier.height(8.dp))

                            OutlinedTextField(
                                value = zone.name,
                                onValueChange = { vm.updateName(it) },
                                label = { Text("Zone Name (e.g., Home, Campus, Work)") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                shape = RoundedCornerShape(12.dp)
                            )

                            Spacer(modifier = Modifier.height(12.dp))

                            Button(
                                onClick = { vm.broadcastZone() },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(46.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = IrctcGreen),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Icon(Icons.AutoMirrored.Filled.Send, contentDescription = null, modifier = Modifier.size(18.dp), tint = Color.White)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    if (broadcastSuccess) "Safe Zone Synced to Device! ✓" else "Broadcast Safe Zone to Tracker",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 13.sp,
                                    color = Color.White
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
