// 画面中央に動画をポップアップ表示して再生する関数（これは今のままでOK）
function playVideoFile(url, options = {}) {
    const autoclose = options.autoclose !== false;
    const onEnded = options.onEnded;   // ★ 追加

    const old = document.getElementById("video-modal-wrapper");
    if (old) old.remove();

    const wrapper = document.createElement("div");
    wrapper.id = "video-modal-wrapper";
    wrapper.style.position = "fixed";
    wrapper.style.inset = "0";
    wrapper.style.background = "rgba(0,0,0,0.6)";
    wrapper.style.display = "flex";
    wrapper.style.alignItems = "center";
    wrapper.style.justifyContent = "center";
    wrapper.style.zIndex = "9999";

    const video = document.createElement("video");
    video.src = url;
    video.controls = true;
    video.autoplay = true;
    video.style.maxWidth = "95%";
    video.style.maxHeight = "95%";
    video.style.borderRadius = "8px";
    video.style.boxShadow = "0 0 30px rgba(0,0,0,0.7)";
    wrapper.appendChild(video);

    if (autoclose) {
        wrapper.addEventListener("click", (e) => {
            if (e.target === wrapper) {
                wrapper.remove();
            }
        });

        video.addEventListener("ended", () => {
            wrapper.remove();
        });
    }

    // ★ 終了時：閉じる＋コールバック
    video.addEventListener("ended", () => {
        if (autoclose) {
            wrapper.remove();
        }
        if (typeof onEnded === "function") {
            onEnded();
        }
    });

    document.body.appendChild(wrapper);
}

// ★ 音声を再生して、再生終了まで待つ
function playSound(url) {
    return new Promise((resolve, reject) => {
        const audio = new Audio(url);

        audio.addEventListener("ended", () => {
            resolve();
        });

        audio.addEventListener("error", (e) => {
            console.error("音声再生エラー:", e);
            reject(e);
        });

        audio.play().catch((err) => {
            console.error("audio.play() に失敗:", err);
            reject(err);
        });
    });
}

// ========================
// ⚠ 絶対に押すなボタン
// ========================
document.addEventListener("DOMContentLoaded", () => {
    const dangerBtn = document.getElementById("dangerBtn");
    if (!dangerBtn) return;

    const explosionUrl = dangerBtn.dataset.videoUrl;
    console.log("explosionUrl =", explosionUrl);

    // explosionUrl を元に mp3 の URL を作る
    // 例: "/static/mp4/爆発素材.mp4" → "/static/mp4/zettai.mp3"
    const soundUrl = explosionUrl.replace(/[^/]+$/, "zettai.mp3");
    console.log("soundUrl =", soundUrl);

    // ★ async にして順番制御する
    async function playExplosion() {

        // ① zettai.mp3 再生（同じディレクトリなので安全）
        try {
            await playSound(soundUrl);
        } catch (e) {
            console.error("音声再生エラー:", e);
        }

        // 画面揺らす
        document.body.classList.add("shake-strong");
        setTimeout(() => {
            document.body.classList.remove("shake-strong");
        }, 600);

        // ② 爆発動画
        playVideoFile(explosionUrl, { autoclose: true });
    }

    dangerBtn.addEventListener("click", () => {
        playExplosion();
    });
});

// ========================
// CAボタン
// ========================
async function playZundamon(apiUrl, text) {
    try {
        const url = apiUrl + "?text=" + encodeURIComponent(text || "");
        const resp = await fetch(url);
        if (!resp.ok) {
            throw new Error("HTTP " + resp.status);
        }

        const blob = await resp.blob();
        const audioUrl = URL.createObjectURL(blob);

        const audio = new Audio(audioUrl);
        audio.play();

        audio.addEventListener("ended", () => {
            URL.revokeObjectURL(audioUrl);
        });
    } catch (err) {
        console.error("ずんだもん音声の再生に失敗:", err);
    }
}

document.addEventListener("click", function (e) {
    const btn = e.target.closest(".js-ca-intro");
    if (!btn) return;

    e.preventDefault();

    const videoUrl   = btn.dataset.videoUrl;
    const apiUrl     = btn.getAttribute("href");     // /ca_intro
    const caText     = btn.dataset.caText || "";     // 読み上げテキスト

    playVideoFile(videoUrl, {
        onEnded: () => {
            // 動画終了後にずんだもん再生
            playZundamon(apiUrl, caText);
        }
    });
});