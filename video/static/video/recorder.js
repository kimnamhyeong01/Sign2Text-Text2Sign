document.addEventListener('DOMContentLoaded', () => {
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = '/static/video/style.css';
  document.head.appendChild(link);

  const preview = document.getElementById('preview');
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  const outputBtn = document.getElementById('outputBtn');
  const statusText = document.getElementById('statusText');
  const sentenceResult = document.getElementById('sentenceResult');
  let mediaRecorder, chunks = [];

  async function initCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({video:true,audio:false});
      preview.srcObject = stream;
      const opts = MediaRecorder.isTypeSupported('video/webm;codecs=vp8')
        ? {mimeType:'video/webm;codecs=vp8'} : {mimeType:'video/webm'};
      mediaRecorder = new MediaRecorder(stream, opts);
      mediaRecorder.ondataavailable = e => e.data.size>0 && chunks.push(e.data);
      mediaRecorder.onstop = handleStop;
      startBtn.disabled = false;
      statusText.innerText = '준비 완료';
    } catch (e) {
      statusText.innerText = '카메라 접근 실패: ' + e.message;
    }
  }

  function handleStop() {
    const blob = new Blob(chunks, {type: chunks[0].type});
    chunks = [];
    uploadVideo(blob);
  }

  function uploadVideo(blob) {
    statusText.innerText = '업로드 중…';
    const form = new FormData();
    form.append('video', blob, 'recording.webm');
    fetch('/api/upload', {method:'POST', body:form})
      .then(r => r.json())
      .then(json => {
        statusText.innerText = json.status==='saved'
          ? `저장 완료: ${json.filename}`
          : `오류: ${json.error||'알 수 없음'}`;

        const glossEl = document.getElementById('gloss');
        if (json.status === 'saved' && 'word' in json) {
          glossEl.innerText = json.word;
        } else {
          glossEl.innerText = '—';
        }
      })
      .catch(err => statusText.innerText = '업로드 오류: ' + err.message);
  }

  startBtn.addEventListener('click', () => {
    if (mediaRecorder.state==='inactive') {
      mediaRecorder.start(); startBtn.disabled=true; stopBtn.disabled=false; statusText.innerText='녹화 중…';
    }
  });
  stopBtn.addEventListener('click', () => {
    if (mediaRecorder.state==='recording') {
      mediaRecorder.stop(); startBtn.disabled=false; stopBtn.disabled=true;
    }
  });

  // 출력 버튼 클릭 시 저장된 글로스를 문장으로 변환하는 api 호출
  outputBtn.addEventListener('click', () => {
    sentenceResult.innerText = '처리 중…';
    fetch('/api/output_gloss')
      .then(response => response.json())
      .then(json => {
        if (json.error) {
          sentenceResult.innerText = json.error;
        } else {
          sentenceResult.innerText = json.sentence;
        }
      })
      .catch(err => sentenceResult.innerText = '오류 발생: ' + err.message);
  });

  initCamera();
});

