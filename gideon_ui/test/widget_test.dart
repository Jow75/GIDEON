import 'package:flutter_test/flutter_test.dart';
import 'package:gideon_ui/main.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  testWidgets('App loads correctly', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({'gideon_backend_url': 'http://127.0.0.1:8100'});
    await tester.pumpWidget(const GideonApp());
    expect(find.text('Gideon AI'), findsOneWidget);
  });
}
