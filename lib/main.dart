import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:wakelock_plus/wakelock_plus.dart';
import 'package:youtube_player_iframe/youtube_player_iframe.dart';

// CAMBIAR ttde-entertainment-TV por tu usuario de GitHub (repo: ttde-tv)
const feedUrl =
    'https://raw.githubusercontent.com/ttde-entertainment-TV/ttde-tv/main/assets/videos.json';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations(
      [DeviceOrientation.landscapeLeft, DeviceOrientation.landscapeRight]);
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
  WakelockPlus.enable();
  runApp(const MaterialApp(debugShowCheckedModeBanner: false, home: TV()));
}

class TV extends StatefulWidget {
  const TV({super.key});
  @override
  State<TV> createState() => _TVState();
}

class _TVState extends State<TV> {
  late final YoutubePlayerController c;
  List<String> ids = [];
  int i = 0;
  bool playing = false;
  Timer? refresh, watchdog;
  final rnd = Random();

  @override
  void initState() {
    super.initState();
    c = YoutubePlayerController(
        params: const YoutubePlayerParams(
            showControls: false,
            showFullscreenButton: false,
            strictRelatedVideos: true));
    c.listen((v) {
      if (v.playerState == PlayerState.ended || v.hasError) _next();
    });
    _load();
    refresh = Timer.periodic(const Duration(hours: 1), (_) => _load(false));
    // si se cuelga, salta al siguiente
    watchdog = Timer.periodic(const Duration(seconds: 20), (_) async {
      if (ids.isEmpty) return;
      final s = await c.playerState;
      if (s == PlayerState.unStarted || s == PlayerState.unknown) _next();
    });
  }

  Future<List<String>> _fetch() async {
    String body;
    try {
      body = (await http.get(Uri.parse(feedUrl))
              .timeout(const Duration(seconds: 15)))
          .body;
    } catch (_) {
      body = await rootBundle.loadString('assets/videos.json');
    }
    try {
      return List<String>.from(jsonDecode(body)['videos']);
    } catch (_) {
      return [];
    }
  }

  Future<void> _load([bool first = true]) async {
    final l = await _fetch();
    if (l.isEmpty) {
      if (first) Timer(const Duration(seconds: 30), _load);
      return;
    }
    l.shuffle(rnd);
    ids = l;
    if (!playing) {
      setState(() => playing = true);
      i = 0;
      c.loadVideoById(videoId: ids[0]);
    }
  }

  void _next() {
    if (ids.isEmpty) return;
    i = (i + 1) % ids.length;
    c.loadVideoById(videoId: ids[i]);
  }

  @override
  void dispose() {
    refresh?.cancel();
    watchdog?.cancel();
    c.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(fit: StackFit.expand, children: [
        Center(child: YoutubePlayer(controller: c, aspectRatio: 16 / 9)),
        if (!playing)
          Container(
              color: Colors.white,
              child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Image.asset('assets/logo.jpg'))),
      ]),
    );
  }
}
