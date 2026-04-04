const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const imagePreview = document.getElementById('image-preview');
const loading = document.querySelector('.loading');
const resultContainer = document.getElementById('result-container');
const analysisView = document.getElementById('analysis-view');

// Event Listeners for Upload
dropZone.onclick = () => fileInput.click();

fileInput.onchange = (e) => {
    const file = e.target.files[0];
    if (file) handleUpload(file);
};

// Drag & Drop
dropZone.ondragover = (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
    dropZone.style.borderColor = 'var(--primary)';
};

dropZone.ondragleave = () => {
    dropZone.classList.remove('drag-over');
    dropZone.style.borderColor = 'var(--glass-border)';
};

dropZone.ondrop = (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    dropZone.style.borderColor = 'var(--glass-border)';
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
};

// Main Upload Function
async function handleUpload(file) {
    if (!file.type.startsWith('image/')) {
        alert('이미지 파일만 업로드 가능합니다.');
        return;
    }

    // Show Preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        analysisView.style.display = 'flex'; // 가로 배치를 위해 flex 사용
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // Initial UI State
    resultContainer.style.display = 'none';
    loading.style.display = 'block';

    // Scroll to loading
    loading.scrollIntoView({ behavior: 'smooth' });

    // Prepare Multipart Form Data
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('서버 처리 중 오류가 발생했습니다.');

        const data = await response.json();
        displayResult(data.results[0]);
    } catch (error) {
        alert(error.message);
    } finally {
        loading.style.display = 'none';
    }
}

// Display Result in UI
function displayResult(result) {
    const specs = result.electrical_info;
    
    // 제품명 표시 (한국어 명칭 우선, 서술어 제거)
    let displayName = specs ? specs.korean_name : result.object_name;
    
    // UI에서 제목에 마침표나 불필요한 서술어가 남지 않도록 한 번 더 정제
    displayName = displayName.replace(/\.$/, '').trim();
    displayName = displayName.replace(/(입니다|보입니다|보여줍니다|나타냅니다|라고 합니다)$/, '').trim();
    
    document.getElementById('obj-name').textContent = displayName;
    
    // 설명 표시
    document.getElementById('obj-desc').textContent = result.description;

    // UI 클린업 (비사물 사진일 경우 사양 카드 숨김)
    const specsGrid = document.querySelector('.specs-grid');
    if (result.object_name === "사물 사진 필요" || !specs) {
        specsGrid.style.display = 'none';
        if (result.object_name === "사물 사진 필요") {
            document.getElementById('obj-name').style.color = '#f87171'; // 경고색(빨강)
        }
    } else {
        specsGrid.style.display = 'grid';
        document.getElementById('obj-name').style.color = ''; // 기본색 복품
        document.getElementById('spec-voltage').textContent = specs.is_variable ? '제품별 상이(불분명)' : specs.voltage_range;
        document.getElementById('spec-power').textContent = specs.typical_power || '-';
    }

    resultContainer.style.display = 'block';
    
    // Scroll to result
    setTimeout(() => {
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}
