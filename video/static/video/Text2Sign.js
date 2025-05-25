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
      const data = await res.json();
      console.log(data);
      const videoList = data.results; // 배열 [{gloss, signVideoUrl, signDescription, signImages}, ...]
      const videoSources = videoList.map(item => item.signVideoUrl);
      const descriptions = videoList.map(item => item.signDescription);
      const images = videoList.map(item => item.signImages);
      console.log(videoList);
      let currentIndex = 0;

      function playNextVideo() {
        if (currentIndex < videoSources.length) {
          outputVideo.src = videoSources[currentIndex];
          outputVideo.playbackRate = 0.6  ;
          // 해당 인덱스의 설명과 이미지를 업데이트
          document.getElementById('description').innerText = descriptions[currentIndex];
          document.getElementById('signImage').src = images[currentIndex];
          outputVideo.play();
          currentIndex++;
        }
      }
      // 이전에 등록된 ended 이벤트가 있다면 제거
      outputVideo.removeEventListener('ended', playNextVideo);
      // 비디오가 끝날 때마다 다음 동영상 재생
      outputVideo.addEventListener('ended', playNextVideo);

      // 첫 번째 비디오부터 시작
      playNextVideo();

    } catch (err) {
      console.error(err);
      alert('영상 생성 중 오류가 발생했습니다: ' + err.message);
    } finally {
      generateBtn.disabled = false;
      generateBtn.innerText = '변환하기';
    }
  });
});
