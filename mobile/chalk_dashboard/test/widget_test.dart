import 'package:chalk_dashboard/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('setup code decodes gist id and key', () {
    final s = Setup.decode('eyJnIjoiYWJjMTIzIiwiayI6InNlY3JldCJ9');
    expect(s?.gist, 'abc123');
    expect(s?.key, 'secret');
  });

  test('bad setup code is rejected', () {
    expect(Setup.decode('not-a-code'), isNull);
  });

  test('only cloudflare tunnel addresses are trusted', () {
    expect(trusted('https://abc-def.trycloudflare.com'), isTrue);
    expect(trusted('https://evil.example.com'), isFalse);
    expect(trusted('http://abc.trycloudflare.com'), isFalse);
    expect(trusted('https://abc.trycloudflare.com.evil.com'), isFalse);
    expect(trusted('https://abc.trycloudflare.com/x'), isFalse);
  });
}
