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

let currentMode = 'electronics';

// Mode Selection Toggle
document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.onclick = () => {
        document.querySelector('.mode-btn.active').classList.remove('active');
        btn.classList.add('active');
        currentMode = btn.dataset.mode;
        
        // 배경 테마 전환
        if (currentMode === 'electronics') {
            document.body.className = 'elec-mode';
        } else if (currentMode === 'furniture') {
            document.body.className = 'furn-mode';
        }
    };
});

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
    formData.append('mode', currentMode); // 선택된 모드 추가

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
    const elecSpecs = result.electrical_info;
    const furnSpecs = result.furniture_info;
    const isElectronic = result.is_electronic;
    const isFurniture = result.is_furniture;
    const isAiGenerated = result.is_ai_generated;
    
    // 제품명 표시
    document.getElementById('obj-name').textContent = result.object_name;
    
    // AI 배지 노출 제어
    const aiBadge = document.getElementById('ai-badge');
    if (isAiGenerated) {
        aiBadge.textContent = '인식된 사물에 대해 AI 가 분석한 정보가 표시됩니다';
        aiBadge.style.display = 'block';
    } else {
        aiBadge.style.display = 'none';
    }
    
    // 설명 표시
    document.getElementById('obj-desc').textContent = result.description;

    // 섹션 관리
    const resultCard = document.getElementById('main-result-card');
    const categoryTag = document.getElementById('category-tag');
    const elecGrid = document.getElementById('elec-specs');
    const furnGrid = document.getElementById('furn-specs');

    // 초기화
    elecGrid.style.display = 'none';
    furnGrid.style.display = 'none';
    resultCard.className = 'result-card'; //Reset themes
    categoryTag.className = 'tag';
    document.getElementById('obj-name').style.color = '';

    if (result.object_name === "사물 사진 필요") {
        document.getElementById('obj-name').style.color = '#f87171';
        categoryTag.textContent = '알림';
    } else if (isElectronic && elecSpecs) {
        // 전자기기 테마 적용
        resultCard.classList.add('elec-theme');
        categoryTag.classList.add('elec-tag');
        categoryTag.textContent = '카테고리: 전자기기';
        
        elecGrid.style.display = 'grid';
        // AI가 구체적인 정보를 찾아왔다면 is_variable과 상관없이 우선 표시
        const displayVoltage = (elecSpecs.voltage_range && !elecSpecs.voltage_range.includes('확인 필요')) 
                               ? elecSpecs.voltage_range 
                               : (elecSpecs.is_variable ? '제품별 상이(불분명)' : elecSpecs.voltage_range);
        
        document.getElementById('spec-voltage').textContent = displayVoltage;
        document.getElementById('spec-power').textContent = elecSpecs.typical_power || '-';
    } else if (isFurniture && furnSpecs) {
        // 가구 테마 적용
        resultCard.classList.add('furn-theme');
        categoryTag.classList.add('furn-tag');
        categoryTag.textContent = '카테고리: 가구';
        
        furnGrid.style.display = 'grid';
        document.getElementById('spec-material').textContent = furnSpecs.material || '확인 중';
        document.getElementById('spec-care').textContent = furnSpecs.care_tip || '-';
    } else {
        categoryTag.classList.add('general-tag');
        categoryTag.textContent = '카테고리: 일반 사물';
    }

    resultContainer.style.display = 'block';
    
    // Scroll to result
    setTimeout(() => {
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}
