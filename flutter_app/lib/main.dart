import 'dart:async';
import 'dart:io';
import 'dart:developer';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:zxing_scanner/zxing_scanner.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Creative App Name',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const MyHomePage(title: 'dApper Boys - GreenProof'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _scanResult = "No result yet.";
  bool _showCameraView = false;
  
  // Camera-related variables
  CameraController? _cameraController;
  Future<void>? _initializeControllerFuture;
  Timer? _scanTimer;
  bool _processing = false;
  XFile? image; // Changed from default value to nullable

  @override
  void dispose() {
    _stopCamera();
    super.dispose();
  }

  // Function to initialize the camera
  Future<void> _startCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        setState(() => _scanResult = "No cameras found on device");
        return;
      }
      
      _cameraController = CameraController(
        cameras.first,
        ResolutionPreset.ultraHigh, // Lower resolution for better performance
      );
      
      _initializeControllerFuture = _cameraController!.initialize();
      await _initializeControllerFuture;
      
      // Start periodic scanning
      _scanTimer = Timer.periodic(const Duration(milliseconds: 500), (timer) {
        if (!_processing) {
          _captureAndScanImage();
        }
      });
      
      setState(() {});
    } catch (e) {
      setState(() => _scanResult = "Error initializing camera: $e");
    }
  }
  
  // Stop camera and clean up resources
  void _stopCamera() {
    _scanTimer?.cancel();
    _scanTimer = null;
    _processing = false; //This is very important for resetting the state to be able to take photos again after closing camera on first iteration
    log("set processing to false in close");
    if (_cameraController != null && _cameraController!.value.isInitialized) {
      _cameraController!.dispose();
      _cameraController = null;
    }
  }
  
  // Capture image and process it for barcodes
  Future<void> _captureAndScanImage() async {
    log("_captureAndScanImage");
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }
    
    _processing = true;
    log("set processing to true");
    try {
      image = await _cameraController!.takePicture();
      log("took image $image");
      
      // Process the image with the existing scan method
      final List<Result>? results = await scanImage(
        await File(image!.path).readAsBytes(),
      );

      log("processed results to be $results");
      
      if (results != null && results.isNotEmpty) {
        setState(() {
          _scanResult = results.first.text;
          // Optional: Stop camera when barcode is found
          _toggleCameraView();
          _callApi(_scanResult, image);
        });
      }
    } catch (e) {
      log("Error capturing image: $e");
    } finally {
      log("Setting processing to false again");
      _processing = false;
    }
  }

  Future<void> _callApi(String barcode, XFile? image) async {
    try {
      // For Android emulator, use 10.0.2.2 instead of localhost
      // For physical devices, use your computer's actual IP address
      final url = Uri.parse('http://10.0.2.2:5000/api/proof');
      
      // Create a multipart request (required for file uploads)
      var request = http.MultipartRequest('POST', url);
      
      // Add barcode_id as a field
      request.fields['barcode_id'] = barcode;
      
      // Add the image as a file
      if (image != null) {
        request.files.add(
          await http.MultipartFile.fromPath('image', image.path),
        );
      }
      
      // Send the request
      var streamedResponse = await request.send();
      
      // Get response as string
      var response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        log("API response: ${response.body}");
        setState(() {
          _scanResult = "✅Barcode: $barcode";
        });
      } else {
        log("Error: ${response.statusCode} - ${response.body}");
        setState(() {
          _scanResult = "API Error: ${response.statusCode}";
        });
      }
    } catch (e) {
      log("Exception when calling API: $e");
      setState(() {
        _scanResult = "Error: $e";
      });
    }
  }


  // Toggle camera view on/off
  void _toggleCameraView() {
    setState(() {
      _showCameraView = !_showCameraView;
    });
    
    if (_showCameraView) {
      _startCamera();
    } else {
      _stopCamera();
    }
  }

  // Keep the existing scan from file functionality
  Future<void> _scanFromFile() async {
    try {
      final ImagePicker picker = ImagePicker();
      image = await picker.pickImage(source: ImageSource.gallery);

      if (image != null) {
        final List<Result>? results = await scanImage(
          await File(image!.path).readAsBytes(),
        );

        setState(() {
          if (results == null) {
            _scanResult = "Scan failed: Could not process image";
          } else if (results.isEmpty) {
            _scanResult = "No barcode found in the image";
          } else {
            _scanResult = results.first.text;
          }
        });
      }
    } catch (e) {
      setState(() {
        _scanResult = "Error scanning image: ${e.toString()}";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: SingleChildScrollView( // Wrap the Column in SingleChildScrollView
        child: Column(
          children: [
            // Camera preview section
            if (_showCameraView)
              SizedBox(
                height: 500, // Fixed height for the camera preview
                child: FutureBuilder<void>(
                  future: _initializeControllerFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.done) {
                      return CameraPreview(_cameraController!);
                    } else {
                      return const Center(child: CircularProgressIndicator());
                    }
                  },
                ),
              ),
            // Results and buttons section
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  Text('Scan Result:', style: Theme.of(context).textTheme.headlineSmall),
                  if (image != null)
                    SizedBox(
                      width: 300, // Fixed width
                      height: 300, // Fixed height
                      child: Image.file(
                        File(image!.path),
                        fit: BoxFit.cover,
                      ),
                    ),
                  Text(_scanResult, style: Theme.of(context).textTheme.bodyLarge),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: _toggleCameraView,
                    child:
                        Text(_showCameraView ? "Close Camera" : "Scan from Camera"),
                  ),
                  ElevatedButton(
                    onPressed: _scanFromFile,
                    child: const Text("Scan from File"),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}