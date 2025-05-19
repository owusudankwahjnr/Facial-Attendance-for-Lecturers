
const video = document.getElementById("video");
const overlay = document.getElementById("overlay");
const captureBtn = document.getElementById("captureBtn");
const submitBtn = document.getElementById("submitBtn");
const preview = document.getElementById("preview");
const MAX_IMAGES = 10;

let faceDetected = false;
let capturedImages = [];

// Load face-api models
Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri("{{ static_url }}models")
]).then(startVideo);

function startVideo() {
    navigator.mediaDevices.getUserMedia({ video: {} })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => console.error("Camera error:", err));
}

video.addEventListener("play", () => {
    const canvas = faceapi.createCanvasFromMedia(video);
    overlay.parentNode.insertBefore(canvas, overlay.nextSibling);
    const displaySize = { width: video.width, height: video.height };
    faceapi.matchDimensions(canvas, displaySize);

    setInterval(async () => {
        const detections = await faceapi.detectAllFaces(
            video,
            new faceapi.TinyFaceDetectorOptions()
        );

        canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
        const resized = faceapi.resizeResults(detections, displaySize);
        faceapi.draw.drawDetections(canvas, resized);

        if (detections.length > 0) {
            faceDetected = true;
            captureBtn.disabled = false;
        } else {
            faceDetected = false;
            captureBtn.disabled = true;
        }
    }, 200);
});

captureBtn.addEventListener("click", () => {
    if (!faceDetected || capturedImages.length >= MAX_IMAGES) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    const imgData = canvas.toDataURL("image/jpeg");
    capturedImages.push(imgData);

    // Preview captured image
    const img = document.createElement("img");
    img.src = imgData;
    img.width = 120;
    img.style.margin = "5px";
    preview.appendChild(img);

    if (capturedImages.length >= MAX_IMAGES) {
        submitBtn.disabled = false;
        captureBtn.disabled = true;
    }
});

submitBtn.addEventListener("click", () => {
    // Submit captured images to backend
    fetch("/accounts/submit-training-data/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ images: capturedImages })
    })
    .then(response => {
        if (response.ok) {
            alert("Training images submitted successfully!");
            window.location.href = "/";
        } else {
            alert("Submission failed.");
        }
    })
    .catch(err => console.error(err));
});

// CSRF helper
function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        if (cookie.trim().startsWith(name + "=")) {
            return decodeURIComponent(cookie.trim().substring(name.length + 1));
        }
    }
    return null;
}
