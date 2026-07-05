import 'package:flutter/foundation.dart';
import '../models/message.dart';
import '../services/api_service.dart';

class ChatProvider with ChangeNotifier {
  final List<Message> _messages = [];
  final ApiService _apiService = ApiService();
  bool _isLoading = false;

  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;

  // Expose current mission state from backend in future
  String _currentMission = "None";
  String get currentMission => _currentMission;

  void addMessage(Message message) {
    _messages.add(message);
    notifyListeners();
  }

  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    // Add user message
    final userMsg = Message(content: text, isUser: true);
    addMessage(userMsg);

    _isLoading = true;
    notifyListeners();

    try {
      final responseText = await _apiService.sendMessageToGideon(text);
      final gideonMsg = Message(content: responseText, isUser: false);
      addMessage(gideonMsg);
    } catch (e) {
      final errorMsg = Message(content: "System Error: Failed to connect to Gideon Core. Make sure the backend is running.\nDetails: $e", isUser: false);
      addMessage(errorMsg);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
