import 'package:flutter_test/flutter_test.dart';
import 'package:gideon_ui/main.dart';

void main() {
  testWidgets('App loads correctly', (WidgetTester tester) async {
    // Basic test to verify the app widget mounts
    await tester.pumpWidget(const GideonApp());
    expect(find.text('Gideon AI'), findsOneWidget);
  });
}
