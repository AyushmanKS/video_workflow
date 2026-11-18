import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:webview_flutter/webview_flutter.dart';

const gistFile = 'chalk-dashboard.json';
const board = Color(0xFF15181A);
const chalk = Color(0xFFE2BE70);

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ChalkApp());
}

class ChalkApp extends StatelessWidget {
  const ChalkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chalk Dashboard',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: board,
        colorScheme: ColorScheme.fromSeed(seedColor: chalk, brightness: Brightness.dark),
      ),
      home: const Home(),
    );
  }
}

class Setup {
  final String gist;
  final String key;
  Setup(this.gist, this.key);

  static Setup? decode(String code) {
    try {
      var s = code.trim();
      s = s.padRight((s.length + 3) ~/ 4 * 4, '=');
      final m = jsonDecode(utf8.decode(base64Url.decode(s))) as Map<String, dynamic>;
      final g = m['g'] as String?;
      final k = m['k'] as String?;
      if (g == null || k == null || g.isEmpty || k.isEmpty) return null;
      return Setup(g, k);
    } catch (_) {
      return null;
    }
  }
}

enum Phase { loading, setup, connecting, offline, ready }

bool trusted(String? url) {
  if (url == null) return false;
  final u = Uri.tryParse(url);
  return u != null && u.scheme == 'https' && u.host.endsWith('.trycloudflare.com') && u.path.isEmpty && !u.hasQuery && u.userInfo.isEmpty;
}

class Home extends StatefulWidget {
  const Home({super.key});

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> with WidgetsBindingObserver {
  SharedPreferences? prefs;
  Setup? setup;
  Phase phase = Phase.loading;
  String status = '';
  String? base;
  late final WebViewController web;
  Timer? retry;
  int attempt = 0;
  bool resolving = false;
  final codeField = TextEditingController();
  String? codeError;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    web = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(board)
      ..setNavigationDelegate(NavigationDelegate(
        onWebResourceError: (err) {
          if (err.isForMainFrame ?? true) connect(force: true);
        },
        onHttpError: (err) {
          final code = err.response?.statusCode ?? 0;
          if (code == 502 || code == 503 || code == 530 || code == 1033) connect(force: true);
        },
      ));
    start();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    retry?.cancel();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState s) {
    if (s == AppLifecycleState.resumed && setup != null) check();
  }

  Future<void> start() async {
    prefs = await SharedPreferences.getInstance();
    final g = prefs!.getString('gist');
    final k = prefs!.getString('key');
    if (g == null || k == null) {
      setState(() => phase = Phase.setup);
      return;
    }
    setup = Setup(g, k);
    connect();
  }

  Future<bool> healthy(String url) async {
    try {
      final r = await http.get(Uri.parse('$url/healthz')).timeout(const Duration(seconds: 8));
      return r.statusCode == 200 && r.body.trim() == 'ok';
    } catch (_) {
      return false;
    }
  }

  Future<String?> lookup() async {
    try {
      final r = await http.get(Uri.parse('https://api.github.com/gists/${setup!.gist}'),
          headers: {'Accept': 'application/vnd.github+json', 'User-Agent': 'chalk-dashboard-app'}).timeout(const Duration(seconds: 12));
      if (r.statusCode != 200) return null;
      final files = (jsonDecode(r.body) as Map<String, dynamic>)['files'] as Map<String, dynamic>;
      final f = files[gistFile] as Map<String, dynamic>?;
      if (f == null) return null;
      final url = (jsonDecode(f['content'] as String) as Map<String, dynamic>)['url'] as String?;
      return trusted(url) ? url : null;
    } catch (_) {
      return null;
    }
  }

  Future<void> check() async {
    if (base == null || phase != Phase.ready) return;
    if (!await healthy(base!)) connect(force: true);
  }

  Future<void> connect({bool force = false}) async {
    if (resolving || setup == null) return;
    resolving = true;
    retry?.cancel();
    if (phase != Phase.ready || force) {
      setState(() {
        phase = Phase.connecting;
        status = 'Connecting to the Mac…';
      });
    }
    String? url = prefs!.getString('url');
    if (!trusted(url) || !await healthy(url!)) {
      setState(() => status = 'Looking up the current address…');
      final found = await lookup();
      url = (found != null && await healthy(found)) ? found : null;
    }
    resolving = false;
    if (url == null) {
      attempt += 1;
      final wait = [15, 30, 60, 90][attempt.clamp(1, 4) - 1];
      setState(() {
        phase = Phase.offline;
        status = 'Mac offline or asleep. Retrying in $wait s.';
      });
      retry = Timer(Duration(seconds: wait), () => connect(force: true));
      return;
    }
    attempt = 0;
    await prefs!.setString('url', url);
    final signedFor = prefs!.getString('signed');
    base = url;
    if (signedFor != url) {
      await web.loadRequest(Uri.parse('$url/login?k=${Uri.encodeQueryComponent(setup!.key)}'));
      await prefs!.setString('signed', url);
    } else {
      await web.loadRequest(Uri.parse('$url/'));
    }
    setState(() => phase = Phase.ready);
  }

  Future<void> saveCode() async {
    final s = Setup.decode(codeField.text);
    if (s == null) {
      setState(() => codeError = 'That code is not valid. Send /app to the bot and paste the whole code.');
      return;
    }
    await prefs!.setString('gist', s.gist);
    await prefs!.setString('key', s.key);
    await prefs!.remove('signed');
    await prefs!.remove('url');
    codeField.clear();
    setState(() {
      setup = s;
      codeError = null;
    });
    connect(force: true);
  }

  Future<void> reset() async {
    await prefs!.clear();
    retry?.cancel();
    setState(() {
      setup = null;
      base = null;
      phase = Phase.setup;
    });
  }

  Future<void> refresh() async {
    if (phase == Phase.ready && base != null && await healthy(base!)) {
      await web.reload();
    } else {
      connect(force: true);
    }
  }

  Widget setupView() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 24),
            const Text('Chalk Dashboard', style: TextStyle(fontSize: 28, color: chalk, fontWeight: FontWeight.w600)),
            const SizedBox(height: 16),
            const Text('One-time setup: send /app to @Chalkstudiobot on Telegram, copy the code it replies with, and paste it here.',
                style: TextStyle(fontSize: 16, height: 1.4)),
            const SizedBox(height: 24),
            TextField(
              controller: codeField,
              minLines: 2,
              maxLines: 4,
              decoration: InputDecoration(border: const OutlineInputBorder(), labelText: 'Setup code', errorText: codeError, errorMaxLines: 3),
            ),
            const SizedBox(height: 12),
            Row(children: [
              TextButton.icon(
                onPressed: () async {
                  final d = await Clipboard.getData('text/plain');
                  if (d?.text != null) codeField.text = d!.text!;
                },
                icon: const Icon(Icons.content_paste),
                label: const Text('Paste'),
              ),
              const Spacer(),
              FilledButton(onPressed: saveCode, child: const Text('Connect')),
            ]),
          ],
        ),
      ),
    );
  }

  Widget waitView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Icon(phase == Phase.offline ? Icons.cloud_off : Icons.sync, size: 56, color: chalk),
          const SizedBox(height: 20),
          Text(status, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16, height: 1.4)),
          if (phase == Phase.offline) ...[
            const SizedBox(height: 8),
            const Text('The dashboard comes back by itself once the Mac is awake and online.',
                textAlign: TextAlign.center, style: TextStyle(fontSize: 13, color: Colors.white60)),
            const SizedBox(height: 20),
            OutlinedButton(onPressed: () => connect(force: true), child: const Text('Try now')),
          ],
          if (phase == Phase.connecting) const Padding(padding: EdgeInsets.only(top: 20), child: CircularProgressIndicator()),
        ]),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final showWeb = phase == Phase.ready;
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) async {
        if (didPop) return;
        if (showWeb && await web.canGoBack()) {
          await web.goBack();
        } else {
          SystemNavigator.pop();
        }
      },
      child: Scaffold(
        appBar: phase == Phase.setup || phase == Phase.loading
            ? null
            : AppBar(
                backgroundColor: board,
                toolbarHeight: 44,
                title: const Text('Chalk Dashboard', style: TextStyle(fontSize: 17, color: chalk)),
                actions: [
                  IconButton(onPressed: refresh, icon: const Icon(Icons.refresh), tooltip: 'Refresh'),
                  PopupMenuButton<String>(
                    onSelected: (v) {
                      if (v == 'reset') reset();
                    },
                    itemBuilder: (_) => const [PopupMenuItem(value: 'reset', child: Text('Enter a new setup code'))],
                  ),
                ],
              ),
        body: switch (phase) {
          Phase.loading => const Center(child: CircularProgressIndicator()),
          Phase.setup => setupView(),
          Phase.ready => WebViewWidget(controller: web),
          _ => waitView(),
        },
      ),
    );
  }
}
