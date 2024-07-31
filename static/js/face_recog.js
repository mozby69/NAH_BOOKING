const video = document.getElementById('videoInput')

Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/static/models'),
    faceapi.nets.faceRecognitionNet.loadFromUri('/static/models'),
    faceapi.nets.faceLandmark68Net.loadFromUri('/static/models'),
    faceapi.nets.ssdMobilenetv1.loadFromUri('/static/models') // heavier/more accurate version of tiny face detector
]).then(start)

function start() {
    document.body.append('Models Loaded')
    
    navigator.getUserMedia(
        { video:{} },
        stream => video.srcObject = stream,
        err => console.error(err)
    )
    
    // video.src = '../videos/speech.mp4'
    console.log('video added')
    recognizeFaces()
}

async function recognizeFaces() {
    const labeledDescriptors = await loadLabeledImages()
    console.log(labeledDescriptors)
    const faceMatcher = new faceapi.FaceMatcher(labeledDescriptors, 0.5)

    video.addEventListener('play', async () => {
        console.log('Playing')
        const canvas = faceapi.createCanvasFromMedia(video)
        document.body.append(canvas)

        const displaySize = { width: video.width, height: video.height }
        faceapi.matchDimensions(canvas, displaySize)

        setInterval(async () => {
            const detections = await faceapi.detectAllFaces(video)
                .withFaceLandmarks()
                .withFaceDescriptors()

            const resizedDetections = faceapi.resizeResults(detections, displaySize)

            canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)

            const results = resizedDetections.map(d => {
                return faceMatcher.findBestMatch(d.descriptor)
            })

            results.forEach((result, i) => {
                // console.log(`Detected: ${result.toString()}`) 
                const box = resizedDetections[i].detection.box
                const drawBox = new faceapi.draw.DrawBox(box, { label: result.toString() })
                drawBox.draw(canvas)
            })
        }, 100)
    })
}

async function loadLabeledImages() {
    const labels = ['johnxyryl','john','xtian']; // Adjust for your labels
    return Promise.all(
        labels.map(async (label) => {
            const descriptions = [];
            for (let i = 2; i <= 3; i++) { // Adjust for number of images per label
                try {
                    const img = await faceapi.fetchImage(`/static/images/${label}/${label}${i}.jpg`);
                    const detections = await faceapi.detectSingleFace(img)
                        .withFaceLandmarks()
                        .withFaceDescriptor();
                    descriptions.push(detections.descriptor);
                    console.log(`${label}/${label}${i}.jpg processed`); // Print message after successful processing
                    document.body.append(`${label} Image ${label}${i} Loaded | `); // Append to body as well
                } catch (error) {
                    console.error(`Error loading image ${label}/${label}${i}.jpg:`, error);
                }
            }
            console.log(`${label} Faces Loaded`); // Print after all images for a label are processed
            return new faceapi.LabeledFaceDescriptors(label, descriptions);
        })
    );
}
