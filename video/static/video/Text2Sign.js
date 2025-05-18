document.addEventListener('DOMContentLoaded', () => {
  const textInput = document.getElementById('textInput');
  const generateBtn = document.getElementById('generateBtn');
  const outputVideo = document.getElementById('outputVideo');

  generateBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) {
      alert('텍스트를 입력해주세요.');
      return;
    }

    generateBtn.disabled = true;
    generateBtn.innerText = '생성 중…';

    try {
      const res = await fetch('/api/text-to-video', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ text })
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);

      const { url } = await res.json();
      outputVideo.src = url;
      outputVideo.load();
      outputVideo.play();

    } catch (err) {
      console.error(err);
      alert('영상 생성 중 오류가 발생했습니다: ' + err.message);
    } finally {
      generateBtn.disabled = false;
      generateBtn.innerText = '변환하기';
    }
  });
});
