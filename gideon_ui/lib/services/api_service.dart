import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = "http://127.0.0.1:8000";

  Future<String> sendMessageToGideon(String message) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/chat'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'message': message,
          'device': 'Flutter UI'
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
}
