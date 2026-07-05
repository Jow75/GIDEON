import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  String _baseUrl = "http://127.0.0.1:8000";
  // The secret matches the default in the Python backend. In a real app, this should be configurable.
  final String _syncSecret = "default_dev_secret_change_in_production";

  ApiService() {
    _loadBaseUrl();
  }

  Future<void> _loadBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    _baseUrl = prefs.getString('gideon_backend_url') ?? "http://127.0.0.1:8000";
  }

  Future<void> setBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('gideon_backend_url', url);
    _baseUrl = url;
  }

  String get currentUrl => _baseUrl;

  Future<String> sendMessageToGideon(String message) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/chat'),
        headers: {
          'Content-Type': 'application/json',
          'x-sync-token': _syncSecret,
        },
        body: jsonEncode({
          'message': message,
          'device': 'Flutter Client (Mobile/Desktop)'
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['response'] ?? "Error: Empty response from Gideon.";
      } else {
        throw Exception('Server responded with status code ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to communicate with Gideon backend: $e');
    }
  }

  Future<Map<String, dynamic>> syncState() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/sync'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'x-sync-token': _syncSecret,
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Server responded with status code ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to sync with Gideon backend: $e');
    }
  }
}
