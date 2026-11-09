"use strict";

var currentVideo = null;

function setStatus(text) {
  var status = document.querySelector("#status");
  if (status) status.textContent = text;
}

async function ensureServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    throw new Error("This browser does not support service workers");
  }
  var workerUrl = "/service-worker.js?v=4";
  await navigator.serviceWorker.register(workerUrl, { scope: "/", updateViaCache: "none" });
  await navigator.serviceWorker.ready;
  if (!navigator.serviceWorker.controller ||
      !navigator.serviceWorker.controller.scriptURL.endsWith(workerUrl)) {
    await new Promise(function (resolve) {
      navigator.serviceWorker.addEventListener("controllerchange", resolve, { once: true });
    });
  }
}

async function selectVideo(video) {
  var player = document.querySelector("#player");
  currentVideo = video.id;
  setStatus("Preparing encrypted stream for " + video.name + "…");
  try {
    await ensureServiceWorker();
    if (currentVideo !== video.id) return;
    player.muted = false;
    player.volume = 1;
    player.src = "/decrypted/" + encodeURIComponent(video.id);
    player.load();
    setStatus(video.name + " is ready. Playback decrypts later ranges as needed.");
    player.addEventListener("canplay", function () {
      if (currentVideo === video.id) {
        setStatus(video.name + " can play while the rest decrypts.");
      }
    }, { once: true });
  } catch (error) {
    setStatus("Could not prepare " + video.name + ". " + (error && error.message ? error.message : error));
  }
}

async function loadVideoList() {
  var list = document.querySelector("#video-list");
  setStatus("Fetching video list…");
  try {
    var response = await fetch("/api/videos", { cache: "no-store" });
    if (!response.ok) throw new Error("HTTP " + response.status);
    var payload = await response.json();
    var videos = payload.videos || [];
    if (!list) throw new Error("video-list element missing");
    list.innerHTML = "";
    for (var i = 0; i < videos.length; i++) {
      (function (video) {
        var button = document.createElement("button");
        button.type = "button";
        button.textContent = video.name + " ";
        var details = document.createElement("span");
        details.textContent = (video.size / 1024 / 1024).toFixed(1) + " MiB";
        button.appendChild(details);
        button.onclick = function () { selectVideo(video); };
        list.appendChild(button);
      })(videos[i]);
    }
    setStatus(videos.length ? "Choose a video." : "No videos are available.");
  } catch (error) {
    setStatus("Could not load the video list. " + (error && error.message ? error.message : error));
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", loadVideoList);
} else {
  loadVideoList();
}
