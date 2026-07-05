import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _urlController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Pre-fill with current URL
    _urlController.text = ApiService().currentUrl;
  }

  void _saveSettings() {
    final newUrl = _urlController.text.trim();
    if (newUrl.isNotEmpty) {
      context.read<ChatProvider>().updateBackendUrl(newUrl);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Backend URL updated. Syncing...')),
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Backend Connection (Tailscale/Local IP)',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                hintText: 'e.g., http://100.x.x.x:8100',
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Color(0xFF3E3E5C),
              ),
              style: const TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 16),
            const Text(
              'Enter the IP address and dynamically assigned port of your Windows Desktop where Gideon Core is running (check the Python console output for the active port, typically starting at 8100).',
              style: TextStyle(color: Colors.grey, fontSize: 14),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueGrey,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                onPressed: _saveSettings,
                child: const Text('Save & Sync', style: TextStyle(color: Colors.white, fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
