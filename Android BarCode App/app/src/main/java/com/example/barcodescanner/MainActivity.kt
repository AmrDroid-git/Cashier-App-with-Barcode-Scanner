package com.example.barcodescanner

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Environment
import android.util.Log
import android.util.Size
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.Executors
import androidx.compose.foundation.border
import androidx.compose.ui.graphics.RectangleShape
import androidx.camera.core.ExperimentalGetImage


class MainActivity : ComponentActivity() {

    private val executor = Executors.newSingleThreadExecutor()
    private val REQUEST_CODE = 123

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (allPermissionsGranted()) {
            setContent { CameraScreen() }
        } else {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(
                    Manifest.permission.CAMERA,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE,
                    Manifest.permission.READ_EXTERNAL_STORAGE
                ),
                REQUEST_CODE
            )
        }
    }

    private fun allPermissionsGranted() = listOf(
        Manifest.permission.CAMERA,
        Manifest.permission.WRITE_EXTERNAL_STORAGE,
        Manifest.permission.READ_EXTERNAL_STORAGE
    ).all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_CODE && allPermissionsGranted()) {
            setContent { CameraScreen() }
        }
    }

    @Composable
    fun CameraScreen() {
        val context = LocalContext.current
        val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
        val previewView = remember { PreviewView(context) }
        val coroutineScope = rememberCoroutineScope()

        var camera by remember { mutableStateOf<Camera?>(null) }
        var scanNow by remember { mutableStateOf(false) }
        var flashOn by remember { mutableStateOf(false) }
        var showMessage by remember { mutableStateOf(false) }
        var messageText by remember { mutableStateOf("Scan status") }

        var lastScanned: String? = null
        var lastTimestamp by remember { mutableStateOf(0L) }

        LaunchedEffect(Unit) {
            val cameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

            val imageAnalyzer = ImageAnalysis.Builder()
                .setTargetResolution(Size(1280, 720))
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()

            imageAnalyzer.setAnalyzer(executor, object : ImageAnalysis.Analyzer {

                @androidx.annotation.OptIn(ExperimentalGetImage::class)
                @OptIn(ExperimentalGetImage::class)
                override fun analyze(imageProxy: ImageProxy) {
                    if (!scanNow) {
                        imageProxy.close()
                        return
                    }

                    val mediaImage = imageProxy.image ?: run {
                        imageProxy.close()
                        return
                    }

                    val image = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)

                    val options = BarcodeScannerOptions.Builder()
                        .setBarcodeFormats(
                            Barcode.FORMAT_EAN_13,
                            Barcode.FORMAT_EAN_8,
                            Barcode.FORMAT_UPC_A,
                            Barcode.FORMAT_UPC_E
                        ).build()

                    val scanner = BarcodeScanning.getClient(options)

                    scanner.process(image)
                        .addOnSuccessListener { barcodes ->
                            val now = System.currentTimeMillis()
                            if (barcodes.isNotEmpty()) {
                                val rawValue = barcodes.first().rawValue
                                if (!rawValue.isNullOrEmpty()
                                    && (rawValue != lastScanned || now - lastTimestamp > 1500)
                                ) {
                                    saveToFile(rawValue)
                                    lastScanned = rawValue
                                    lastTimestamp = now
                                    messageText = "Scanned: $rawValue"
                                } else {
                                    messageText = "Duplicate or invalid"
                                }
                            } else {
                                messageText = "Nothing detected"
                            }

                            scanNow = false
                            showMessage = true
                            coroutineScope.launch {
                                delay(1000)
                                showMessage = false
                            }

                            imageProxy.close()
                        }
                        .addOnFailureListener {
                            scanNow = false
                            messageText = "Scan error"
                            showMessage = true
                            coroutineScope.launch {
                                delay(1000)
                                showMessage = false
                            }
                            imageProxy.close()
                        }
                }
            })

            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            cameraProvider.unbindAll()
            camera = cameraProvider.bindToLifecycle(this@MainActivity, cameraSelector, preview, imageAnalyzer)
        }

        Box(modifier = Modifier.fillMaxSize()) {
            AndroidView(factory = { previewView }, modifier = Modifier.fillMaxSize())

            // ✅ Center scanning guide rectangle
            Box(
                modifier = Modifier
                    .align(Alignment.Center)
                    .size(width = 280.dp, height = 120.dp)
                    .border(
                        width = 2.dp,
                        color = MaterialTheme.colorScheme.primary,
                        shape = RectangleShape
                    )
            )

            // ✅ Buttons
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
                    .align(Alignment.BottomCenter),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Button(
                    onClick = { scanNow = true },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(70.dp)
                ) {
                    Text("Scan", style = MaterialTheme.typography.titleLarge)
                }

                Spacer(modifier = Modifier.height(8.dp))

                Button(
                    onClick = {
                        flashOn = !flashOn
                        camera?.cameraControl?.enableTorch(flashOn)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(70.dp)
                ) {
                    Text(if (flashOn) "Turn Flash OFF" else "Turn Flash ON")
                }

                Spacer(modifier = Modifier.height(16.dp))

                if (showMessage) {
                    Snackbar(modifier = Modifier.padding(8.dp)) {
                        Text(text = messageText)
                    }
                }
            }
        }

    }

    private fun saveToFile(data: String) {
        try {
            val timestamp = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(java.util.Date())
            val line = "$data | $timestamp\n"
            val file = File(Environment.getExternalStorageDirectory(), "barcode.txt")
            FileOutputStream(file, true).use { it.write(line.toByteArray()) }
        } catch (e: Exception) {
            Log.e("FILE_WRITE", "Error writing barcode: ${e.message}")
        }
    }
}
