import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/chat_provider.dart';
import 'screens/chat_screen.dart';

void main() {
  runApp(const GideonApp());
}

class GideonApp extends StatelessWidget {
  const GideonApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ChatProvider()),
      ],
      child: MaterialApp(
        title: 'Gideon AI',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          brightness: Brightness.dark,
          primarySwatch: Colors.blueGrey,
          useMaterial3: true,
          scaffoldBackgroundColor: const Color(0xFF1E1E2C),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF2D2D44),
            elevation: 0,
          ),
        ),
        home: const ChatScreen(),
      ),
    );
  }
}
