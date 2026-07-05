import 'package:flutter/foundation.dart';
import '../models/message.dart';
import '../services/api_service.dart';

class ChatProvider with ChangeNotifier {
  List<Message> _messages = [];
  final ApiService _apiService = ApiService();
  bool _isLoading = false;

  List<Message> get messages => _messages;
  bool get isLoading => _isLoading;

  String _currentMission = "None";
  String get currentMission => _currentMission;

  ChatProvider() {
    // Sync state immediately on startup
    syncWithBackend();
  }

  void addMessage(Message message) {
    _messages.add(message);
    notifyListeners();
  }

  Future<void> syncWithBackend() async {
    _isLoading = true;
    notifyListeners();

    try {
      final state = await _apiService.syncState();

      // Update World State / Mission
      if (state['world_state'] != null && state['world_state']['Active Mission'] != null) {
        _currentMission = state['world_state']['Active Mission'];
      }

      // Sync History
      if (state['messages'] != null) {
        _messages = (state['messages'] as List).map((msgData) {
           return Message(
             content: msgData['content'],
             isUser: msgData['role'] == 'user'
           );
        }).toList();
      }
    } catch (e) {
      // If we fail to sync (e.g. backend offline or wrong VPN IP), don't crash, just log it.
      debugPrint("Sync Error: $e");
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateBackendUrl(String url) async {
    await _apiService.setBaseUrl(url);
    await syncWithBackend();
  }

  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    final userMsg = Message(content: text, isUser: true);
    addMessage(userMsg);

    _isLoading = true;
    notifyListeners();

    try {
      final responseText = await _apiService.sendMessageToGideon(text);
      final gideonMsg = Message(content: responseText, isUser: false);
      addMessage(gideonMsg);

      // Re-sync after sending a message to catch any World State updates (like a newly assigned mission)
      await syncWithBackend();
    } catch (e) {
      final errorMsg = Message(content: "System Error: Failed to connect to Gideon Core. Make sure the backend is running and reachable via Tailscale/Localhost.\nDetails: $e", isUser: false);
      addMessage(errorMsg);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
