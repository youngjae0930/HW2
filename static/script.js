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
    const isElectronic = result.is_electronic;
    const isAiGenerated = result.is_ai_generated;
    
    // 제품명 표시
    document.getElementById('obj-name').textContent = result.object_name;
    
    // AI 배지 노출 제어 (제품명 위에 삽입)
    const aiBadge = document.getElementById('ai-badge');
    if (isAiGenerated) {
        aiBadge.textContent = '인식된 사물에 대해 AI 가 분석한 정보가 표시됩니다';
        aiBadge.style.display = 'block';
    } else {
        aiBadge.style.display = 'none';
    }
    
    // 설명 표시
    document.getElementById('obj-desc').textContent = result.description;

    // UI 클린업 (비사물 사진이거나 비전자기기일 경우 사양 카드 숨김)
    const specsGrid = document.querySelector('.specs-grid');
    if (result.object_name === "사물 사진 필요" || !isElectronic || !specs) {
        specsGrid.style.display = 'none';
        if (result.object_name === "사물 사진 필요") {
            document.getElementById('obj-name').style.color = '#f87171'; // 경고색(빨강)
        }
    } else {
        specsGrid.style.display = 'grid';
        document.getElementById('obj-name').style.color = ''; // 기본색 복원
        document.getElementById('spec-voltage').textContent = specs.is_variable ? '제품별 상이(불분명)' : specs.voltage_range;
        document.getElementById('spec-power').textContent = specs.typical_power || '-';
    }

    resultContainer.style.display = 'block';
    
    // Scroll to result
    setTimeout(() => {
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}
