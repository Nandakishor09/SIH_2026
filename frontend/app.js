/**
 * Legal Metrology Compliance Checker - Frontend Controller & PDF Report Engine
 * Complies with Indian Government Portal Standard
 */

document.addEventListener('DOMContentLoaded', () => {
  // State variables
  let frontFile = null;
  let backFile = null;
  let sampleCatalog = [];
  let currentScanResult = null;
  let activeConfirmCallback = null;

  const STORAGE_KEY = 'legal_metrology_compliance_history';

  // Navigation & Views
  const tabChecker = document.getElementById('tab-checker');
  const tabHistory = document.getElementById('tab-history');
  const checkerView = document.getElementById('checker-view');
  const historySection = document.getElementById('history-section');
  const historyCountBadge = document.getElementById('history-count-badge');

  // DOM Elements - Upload
  const frontDropzone = document.getElementById('front-dropzone');
  const frontFileInput = document.getElementById('front-file-input');
  const frontEmptyState = document.getElementById('front-empty-state');
  const frontPreviewState = document.getElementById('front-preview-state');
  const frontPreviewImg = document.getElementById('front-preview-img');
  const frontFilename = document.getElementById('front-filename');
  const frontRemoveBtn = document.getElementById('front-remove-btn');
  const frontReplaceBtn = document.getElementById('front-replace-btn');

  const backDropzone = document.getElementById('back-dropzone');
  const backFileInput = document.getElementById('back-file-input');
  const backEmptyState = document.getElementById('back-empty-state');
  const backPreviewState = document.getElementById('back-preview-state');
  const backPreviewImg = document.getElementById('back-preview-img');
  const backFilename = document.getElementById('back-filename');
  const backRemoveBtn = document.getElementById('back-remove-btn');
  const backReplaceBtn = document.getElementById('back-replace-btn');

  const checkBtn = document.getElementById('check-btn');
  const clearBtn = document.getElementById('clear-btn');
  const recheckBtn = document.getElementById('recheck-btn');
  const bottomRecheckBtn = document.getElementById('bottom-recheck-btn');
  const downloadCurrentPdfBtn = document.getElementById('download-current-pdf-btn');
  const bottomDownloadPdfBtn = document.getElementById('bottom-download-pdf-btn');

  const validationAlert = document.getElementById('validation-alert');
  const validationAlertText = document.getElementById('validation-alert-text');
  const closeAlertBtn = document.getElementById('close-alert-btn');

  const uploadWorkspace = document.getElementById('upload-workspace');
  const loadingSection = document.getElementById('loading-section');
  const resultsSection = document.getElementById('results-section');
  const loadingStatusText = document.getElementById('loading-status-text');

  // Report Elements
  const overallStatusCard = document.getElementById('overall-status-card');
  const statusIcon = document.getElementById('status-icon');
  const statusTitle = document.getElementById('status-title');
  const statusScore = document.getElementById('status-score');
  const statusDesc = document.getElementById('status-desc');
  const complianceTableBody = document.getElementById('compliance-table-body');
  const failedSection = document.getElementById('failed-section');
  const failedItemsContainer = document.getElementById('failed-items-container');
  const rawOcrFrontText = document.getElementById('raw-ocr-front-text');
  const rawOcrBackText = document.getElementById('raw-ocr-back-text');

  // History Elements
  const clearHistoryBtn = document.getElementById('clear-history-btn');
  const historyEmpty = document.getElementById('history-empty');
  const historyList = document.getElementById('history-list');
  const emptyStartScanBtn = document.getElementById('empty-start-scan-btn');

  // Modal Elements
  const confirmModal = document.getElementById('confirm-modal');
  const modalTitle = document.getElementById('modal-title');
  const modalMessage = document.getElementById('modal-message');
  const modalIcon = document.getElementById('modal-icon');
  const modalCancelBtn = document.getElementById('modal-cancel-btn');
  const modalConfirmBtn = document.getElementById('modal-confirm-btn');

  // Step Indicators
  const step1 = document.getElementById('step-1');
  const step2 = document.getElementById('step-2');
  const step3 = document.getElementById('step-3');

  // Ordered check keys
  const CHECK_ORDER = [
    'commodity_name',
    'manufacturer_name',
    'manufacturer_address',
    'net_quantity',
    'mrp',
    'mrp_wording',
    'expiry',
    'customer_care'
  ];

  // --------------------------------------------------------------------------
  // Navigation Tabs Logic
  // --------------------------------------------------------------------------
  function switchTab(target) {
    if (target === 'checker') {
      tabChecker.classList.add('active');
      tabHistory.classList.remove('active');
      checkerView.classList.remove('hidden');
      historySection.classList.add('hidden');
    } else if (target === 'history') {
      tabHistory.classList.add('active');
      tabChecker.classList.remove('active');
      historySection.classList.remove('hidden');
      checkerView.classList.add('hidden');
      renderHistoryUI();
    }
  }

  tabChecker.addEventListener('click', () => switchTab('checker'));
  tabHistory.addEventListener('click', () => switchTab('history'));
  emptyStartScanBtn.addEventListener('click', () => {
    switchTab('checker');
    resetToUpload();
  });

  // --------------------------------------------------------------------------
  // Setup File Upload & Dropzone Handlers
  // --------------------------------------------------------------------------
  function setupDropzone(dropzone, fileInput, onFileSelected) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length > 0) {
        onFileSelected(dt.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        onFileSelected(e.target.files[0]);
      }
    });
  }

  // Front Handlers
  setupDropzone(frontDropzone, frontFileInput, (file) => {
    frontFile = file;
    displayImagePreview(file, frontPreviewImg, frontFilename, frontEmptyState, frontPreviewState);
    hideAlert();
  });

  frontRemoveBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    frontFile = null;
    frontFileInput.value = '';
    frontEmptyState.classList.remove('hidden');
    frontPreviewState.classList.add('hidden');
    frontPreviewImg.src = '';
  });

  frontReplaceBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    frontFileInput.click();
  });

  // Back Handlers
  setupDropzone(backDropzone, backFileInput, (file) => {
    backFile = file;
    displayImagePreview(file, backPreviewImg, backFilename, backEmptyState, backPreviewState);
    hideAlert();
  });

  backRemoveBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    backFile = null;
    backFileInput.value = '';
    backEmptyState.classList.remove('hidden');
    backPreviewState.classList.add('hidden');
    backPreviewImg.src = '';
  });

  backReplaceBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    backFileInput.click();
  });

  function displayImagePreview(file, imgElement, nameElement, emptyEl, previewEl) {
    nameElement.textContent = file.name || 'image.jpg';
    const reader = new FileReader();
    reader.onload = (e) => {
      imgElement.src = e.target.result;
      emptyEl.classList.add('hidden');
      previewEl.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  }

  // --------------------------------------------------------------------------
  // Sample Pack Presets
  // --------------------------------------------------------------------------
  async function loadSampleCatalog() {
    try {
      const resp = await fetch('/api/samples');
      if (resp.ok) {
        sampleCatalog = await resp.json();
      }
    } catch (e) {
      console.warn('Could not load sample catalog from API:', e);
    }
  }
  loadSampleCatalog();

  const sampleButtons = document.querySelectorAll('.sample-btn');
  sampleButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const sampleId = btn.getAttribute('data-sample');
      await applySamplePreset(sampleId);
    });
  });

  async function applySamplePreset(sampleId) {
    const sample = sampleCatalog.find(s => s.id === sampleId) || {
      compliant_biscuits: {
        front: '/api/sample-image/sample_compliant_front.jpg',
        back: '/api/sample-image/sample_compliant_back.jpg'
      },
      flagged_missing_mrp_wording: {
        front: '/api/sample-image/sample_flagged_mrp_front.jpg',
        back: '/api/sample-image/sample_flagged_mrp_back.jpg'
      },
      flagged_missing_customer_care: {
        front: '/api/sample-image/sample_flagged_care_front.jpg',
        back: '/api/sample-image/sample_flagged_care_back.jpg'
      },
      blurry_unverified: {
        front: '/api/sample-image/sample_blurry_front.jpg',
        back: '/api/sample-image/sample_compliant_back.jpg'
      }
    }[sampleId];

    const frontUrl = sample.front_file || sample.front;
    const backUrl = sample.back_file || sample.back;

    try {
      // Fetch Front
      const respF = await fetch(frontUrl);
      const blobF = await respF.blob();
      frontFile = new File([blobF], frontUrl.split('/').pop(), { type: 'image/jpeg' });
      displayImagePreview(frontFile, frontPreviewImg, frontFilename, frontEmptyState, frontPreviewState);

      // Fetch Back
      const respB = await fetch(backUrl);
      const blobB = await respB.blob();
      backFile = new File([blobB], backUrl.split('/').pop(), { type: 'image/jpeg' });
      displayImagePreview(backFile, backPreviewImg, backFilename, backEmptyState, backPreviewState);

      hideAlert();
    } catch (err) {
      showAlert('Failed to load sample package: ' + err.message);
    }
  }

  // --------------------------------------------------------------------------
  // Alert Helpers
  // --------------------------------------------------------------------------
  function showAlert(msg) {
    validationAlertText.textContent = msg;
    validationAlert.classList.remove('hidden');
  }

  function hideAlert() {
    validationAlert.classList.add('hidden');
  }

  closeAlertBtn.addEventListener('click', hideAlert);

  // --------------------------------------------------------------------------
  // Check Compliance Action
  // --------------------------------------------------------------------------
  checkBtn.addEventListener('click', async () => {
    // Validation check
    if (!frontFile || !backFile) {
      showAlert('Please upload both the front and back images.');
      return;
    }

    hideAlert();
    startLoading();

    const formData = new FormData();
    formData.append('front_image', frontFile);
    formData.append('back_image', backFile);

    try {
      // Progress simulation steps
      setTimeout(() => {
        step1.classList.remove('step-active');
        step2.classList.add('step-active');
        loadingStatusText.textContent = 'Extracting packaging text with PaddleOCR...';
      }, 1000);

      setTimeout(() => {
        step2.classList.remove('step-active');
        step3.classList.add('step-active');
        loadingStatusText.textContent = 'Verifying 8 mandatory Legal Metrology rules...';
      }, 2200);

      const response = await fetch('/check', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server error: ${response.status}`);
      }

      const resultData = await response.json();
      currentScanResult = resultData;

      // Automatically save to history
      saveHistoryRecord(resultData);

      // Render Results view
      renderResults(resultData);
    } catch (err) {
      stopLoading();
      showAlert('Analysis Error: ' + err.message);
    }
  });

  // --------------------------------------------------------------------------
  // Render Report
  // --------------------------------------------------------------------------
  function renderResults(data) {
    stopLoading();
    uploadWorkspace.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // 1. Overall Status Hero Banner
    overallStatusCard.className = 'status-hero';
    if (data.overall_status === 'COMPLIANT') {
      overallStatusCard.classList.add('status-compliant');
      statusIcon.textContent = '✅';
      statusTitle.textContent = 'PRODUCT COMPLIANT';
      statusScore.textContent = `${data.passed} / ${data.total_checks || 8} checks passed`;
      statusDesc.textContent = 'All mandatory Legal Metrology packaged commodity declarations are detected and verified.';
    } else if (data.overall_status === 'FLAGGED') {
      overallStatusCard.classList.add('status-flagged');
      statusIcon.textContent = '⚠️';
      statusTitle.textContent = 'PRODUCT FLAGGED';
      statusScore.textContent = `${data.passed} / ${data.total_checks || 8} checks passed`;
      statusDesc.textContent = 'One or more required declarations are missing or format non-compliant under Legal Metrology rules.';
    } else {
      overallStatusCard.classList.add('status-needs-review');
      statusIcon.textContent = '⚡';
      statusTitle.textContent = 'NEEDS REVIEW';
      statusScore.textContent = `${data.passed} / ${data.total_checks || 8} passed (${data.unverified || 0} unverified)`;
      statusDesc.textContent = data.disclaimer || 'Image quality or text clarity is insufficient for a reliable automated compliance decision.';
    }

    // 2. Compliance Table Rows
    complianceTableBody.innerHTML = '';
    const checks = data.checks || {};
    const failedOrUnverifiedItems = [];

    CHECK_ORDER.forEach(key => {
      const item = checks[key];
      if (!item) return;

      const tr = document.createElement('tr');

      // Status pill class & label
      let statusClass = 'pass';
      let statusLabel = '✓ PASS';
      if (item.status === 'FAIL') {
        statusClass = 'fail';
        statusLabel = '✗ FAIL';
        failedOrUnverifiedItems.push(item);
      } else if (item.status === 'UNVERIFIED') {
        statusClass = 'unverified';
        statusLabel = '⚡ UNVERIFIED';
        failedOrUnverifiedItems.push(item);
      }

      // Value formatting
      const valHtml = item.value
        ? `<span class="value-cell">${escapeHtml(item.value)}</span>`
        : `<span class="value-cell empty">Not detected</span>`;

      // Evidence formatting
      const evidenceHtml = item.evidence
        ? `<div class="evidence-cell">"${escapeHtml(item.evidence)}"</div>`
        : `<div class="evidence-cell empty">No matched OCR snippet</div>`;

      tr.innerHTML = `
        <td>
          <div class="req-name-cell">
            <span>${escapeHtml(item.requirement_name)}</span>
          </div>
        </td>
        <td>
          <span class="status-badge ${statusClass}">${statusLabel}</span>
        </td>
        <td>${valHtml}</td>
        <td>${evidenceHtml}</td>
      `;

      complianceTableBody.appendChild(tr);
    });

    // 3. Failed / Flagged Summary Section
    if (failedOrUnverifiedItems.length > 0) {
      failedItemsContainer.innerHTML = '';
      failedOrUnverifiedItems.forEach(f => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'failed-item';
        itemDiv.innerHTML = `
          <div class="failed-item-bullet">${f.status === 'FAIL' ? '✗' : '⚡'}</div>
          <div class="failed-item-body">
            <strong>${escapeHtml(f.requirement_name)} (${f.status})</strong>
            <p>${escapeHtml(f.details || 'The expected declaration could not be detected in the uploaded images.')}</p>
          </div>
        `;
        failedItemsContainer.appendChild(itemDiv);
      });
      failedSection.classList.remove('hidden');
    } else {
      failedSection.classList.add('hidden');
    }

    // 4. Raw OCR Text
    rawOcrFrontText.textContent = (data.raw_ocr_front && data.raw_ocr_front.length > 0)
      ? data.raw_ocr_front.join('\n')
      : 'No text extracted from front image.';

    rawOcrBackText.textContent = (data.raw_ocr_back && data.raw_ocr_back.length > 0)
      ? data.raw_ocr_back.join('\n')
      : 'No text extracted from back image.';

    window.scrollTo({ top: resultsSection.offsetTop - 40, behavior: 'smooth' });
  }

  // --------------------------------------------------------------------------
  // Loading & Reset UI Helpers
  // --------------------------------------------------------------------------
  function startLoading() {
    uploadWorkspace.classList.add('hidden');
    resultsSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');
    loadingStatusText.textContent = 'Analyzing product images...';
    step1.className = 'step-item step-active';
    step2.className = 'step-item';
    step3.className = 'step-item';
  }

  function stopLoading() {
    loadingSection.classList.add('hidden');
  }

  function resetToUpload() {
    resultsSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    uploadWorkspace.classList.remove('hidden');
    hideAlert();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  recheckBtn.addEventListener('click', resetToUpload);
  bottomRecheckBtn.addEventListener('click', resetToUpload);

  clearBtn.addEventListener('click', () => {
    frontFile = null;
    backFile = null;
    frontFileInput.value = '';
    backFileInput.value = '';
    frontEmptyState.classList.remove('hidden');
    frontPreviewState.classList.add('hidden');
    frontPreviewImg.src = '';
    backEmptyState.classList.remove('hidden');
    backPreviewState.classList.add('hidden');
    backPreviewImg.src = '';
    hideAlert();
  });

  // --------------------------------------------------------------------------
  // LocalStorage History Operations
  // --------------------------------------------------------------------------
  function getHistory() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Error reading history from localStorage:', e);
      return [];
    }
  }

  function saveHistory(historyArray) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(historyArray));
      updateHistoryBadge();
    } catch (e) {
      console.error('Error writing history to localStorage:', e);
    }
  }

  function updateHistoryBadge() {
    const history = getHistory();
    historyCountBadge.textContent = history.length;
  }

  function formatDateTime(dateObj) {
    // Format: "25 Aug 2026, 4:30 PM"
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = dateObj.getDate();
    const month = months[dateObj.getMonth()];
    const year = dateObj.getFullYear();
    let hours = dateObj.getHours();
    const minutes = dateObj.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // 0 -> 12
    return `${day} ${month} ${year}, ${hours}:${minutes} ${ampm}`;
  }

  function formatFullDate(dateObj) {
    // Format: "25 August 2026, 4:30 PM"
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    const day = dateObj.getDate();
    const month = months[dateObj.getMonth()];
    const year = dateObj.getFullYear();
    let hours = dateObj.getHours();
    const minutes = dateObj.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    return `${day} ${month} ${year}, ${hours}:${minutes} ${ampm}`;
  }

  function formatDateISO(dateObj) {
    const yyyy = dateObj.getFullYear();
    const mm = (dateObj.getMonth() + 1).toString().padStart(2, '0');
    const dd = dateObj.getDate().toString().padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  function resolveProductName(resultData) {
    if (
      resultData.checks &&
      resultData.checks.commodity_name &&
      resultData.checks.commodity_name.value &&
      resultData.checks.commodity_name.value.trim() !== ''
    ) {
      return resultData.checks.commodity_name.value.trim();
    }
    return 'Unknown Product';
  }

  function saveHistoryRecord(resultData) {
    const now = new Date();
    const productName = resolveProductName(resultData);
    const history = getHistory();

    const record = {
      id: 'rec_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
      product_name: productName,
      timestamp_str: formatDateTime(now),
      timestamp_full: formatFullDate(now),
      timestamp_iso: formatDateISO(now),
      created_at: now.toISOString(),
      result: resultData
    };

    // Newest first
    history.unshift(record);
    saveHistory(history);
    return record;
  }

  function deleteHistoryRecord(id) {
    let history = getHistory();
    history = history.filter(item => item.id !== id);
    saveHistory(history);
    renderHistoryUI();
  }

  function clearAllHistory() {
    saveHistory([]);
    renderHistoryUI();
  }

  // --------------------------------------------------------------------------
  // Confirmation Modal Controller
  // --------------------------------------------------------------------------
  function openConfirmModal({ title, message, icon = '⚠️', onConfirm }) {
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    modalIcon.textContent = icon;
    activeConfirmCallback = onConfirm;
    confirmModal.classList.remove('hidden');
  }

  function closeConfirmModal() {
    confirmModal.classList.add('hidden');
    activeConfirmCallback = null;
  }

  modalCancelBtn.addEventListener('click', closeConfirmModal);
  confirmModal.addEventListener('click', (e) => {
    if (e.target === confirmModal) {
      closeConfirmModal();
    }
  });

  modalConfirmBtn.addEventListener('click', () => {
    if (typeof activeConfirmCallback === 'function') {
      activeConfirmCallback();
    }
    closeConfirmModal();
  });

  clearHistoryBtn.addEventListener('click', () => {
    const history = getHistory();
    if (history.length === 0) return;

    openConfirmModal({
      title: 'Clear All History',
      message: 'Are you sure you want to delete all saved compliance records? This action cannot be undone.',
      icon: '🗑️',
      onConfirm: () => clearAllHistory()
    });
  });

  // --------------------------------------------------------------------------
  // Render History UI
  // --------------------------------------------------------------------------
  function renderHistoryUI() {
    updateHistoryBadge();
    const history = getHistory();

    if (history.length === 0) {
      historyEmpty.classList.remove('hidden');
      historyList.classList.add('hidden');
      clearHistoryBtn.classList.add('hidden');
      return;
    }

    historyEmpty.classList.add('hidden');
    historyList.classList.remove('hidden');
    clearHistoryBtn.classList.remove('hidden');

    historyList.innerHTML = '';

    history.forEach(item => {
      const card = document.createElement('div');
      const res = item.result || {};
      const status = res.overall_status || 'NEEDS REVIEW';

      let statusClass = 'status-needs-review';
      let statusBadgeClass = 'unverified';
      let statusIconSymbol = '⚡';
      let statusLabelText = 'NEEDS REVIEW';

      if (status === 'COMPLIANT') {
        statusClass = 'status-compliant';
        statusBadgeClass = 'pass';
        statusIconSymbol = '✓';
        statusLabelText = 'COMPLIANT';
      } else if (status === 'FLAGGED') {
        statusClass = 'status-flagged';
        statusBadgeClass = 'fail';
        statusIconSymbol = '⚠';
        statusLabelText = 'FLAGGED';
      }

      card.className = `history-card ${statusClass}`;
      card.innerHTML = `
        <div class="history-card-main">
          <h3 class="history-product-name">${escapeHtml(item.product_name || 'Unknown Product')}</h3>
          <div class="history-timestamp">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span>Checked: ${escapeHtml(item.timestamp_str || '')}</span>
          </div>
          <div class="history-meta-row">
            <span class="status-badge ${statusBadgeClass}">${statusIconSymbol} ${statusLabelText}</span>
            <span class="status-score-chip">${res.passed !== undefined ? res.passed : 0} / ${res.total_checks || 8} checks passed</span>
          </div>
        </div>
        <div class="history-card-actions">
          <button type="button" class="btn-download-pdf" data-history-id="${item.id}" title="Download PDF Report">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span>Download PDF</span>
          </button>
          <button type="button" class="btn-delete-entry" data-delete-id="${item.id}" title="Delete Record" aria-label="Delete Record">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
          </button>
        </div>
      `;

      // Download PDF button handler
      const downloadBtn = card.querySelector('.btn-download-pdf');
      downloadBtn.addEventListener('click', () => {
        generatePdfReport(item);
      });

      // Delete single button handler
      const deleteBtn = card.querySelector('.btn-delete-entry');
      deleteBtn.addEventListener('click', () => {
        openConfirmModal({
          title: 'Delete Compliance Record',
          message: `Are you sure you want to delete the compliance record for "${item.product_name}"?`,
          icon: '🗑️',
          onConfirm: () => deleteHistoryRecord(item.id)
        });
      });

      historyList.appendChild(card);
    });
  }

  // --------------------------------------------------------------------------
  // PDF Report Generation Engine
  // --------------------------------------------------------------------------
  function sanitizeFilename(name) {
    if (!name) return 'Unknown_Product';
    // Remove invalid Windows / OS filename characters: \ / : * ? " < > |
    return name
      .replace(/[\\/:*?"<>|]/g, '')
      .trim()
      .replace(/\s+/g, '_')
      .replace(/_+/g, '_');
  }

  function generatePdfReport(record) {
    if (!window.jspdf || !window.jspdf.jsPDF) {
      alert('PDF generation library is loading, please try again.');
      return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    const res = record.result || {};
    const checks = res.checks || {};
    const productName = record.product_name || 'Unknown Product';
    const dateTimeStr = record.timestamp_full || record.timestamp_str || formatFullDate(new Date());
    const overallStatus = res.overall_status || 'NEEDS REVIEW';
    const passedCount = res.passed !== undefined ? res.passed : 0;
    const failedCount = res.failed !== undefined ? res.failed : 0;
    const unverifiedCount = res.unverified !== undefined ? res.unverified : 0;
    const totalChecks = res.total_checks || 8;

    const pageWidth = 210;
    const pageHeight = 297;
    const margin = 14;
    const contentWidth = pageWidth - margin * 2; // 182mm

    let currentY = 12;

    // 1. National Tricolor Accent Strip at top edge
    doc.setFillColor(217, 83, 30); // Saffron
    doc.rect(margin, currentY, contentWidth / 3, 2, 'F');
    doc.setFillColor(240, 240, 240); // White/Off-white
    doc.rect(margin + contentWidth / 3, currentY, contentWidth / 3, 2, 'F');
    doc.setFillColor(19, 136, 8); // Green
    doc.rect(margin + (contentWidth / 3) * 2, currentY, contentWidth / 3, 2, 'F');
    currentY += 4;

    // 2. Government Header Box
    doc.setFillColor(11, 37, 69); // Deep Navy
    doc.roundedRect(margin, currentY, contentWidth, 22, 1.5, 1.5, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(13);
    doc.text('LEGAL METROLOGY COMPLIANCE REPORT', margin + contentWidth / 2, currentY + 9, { align: 'center' });

    doc.setTextColor(203, 213, 225);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8.5);
    doc.text('AI-Assisted Preliminary Compliance Verification', margin + contentWidth / 2, currentY + 16, { align: 'center' });

    currentY += 26;

    // 3. Product Information Box
    doc.setFillColor(248, 250, 252);
    doc.setDrawColor(209, 213, 219);
    doc.setLineWidth(0.3);
    doc.roundedRect(margin, currentY, contentWidth, 22, 1.5, 1.5, 'FD');

    // Left vertical accent bar
    doc.setFillColor(11, 37, 69);
    doc.rect(margin, currentY, 2.5, 22, 'F');

    // Product Info Texts
    doc.setFontSize(9);
    doc.setTextColor(17, 24, 39);

    // Row 1
    doc.setFont('helvetica', 'bold');
    doc.text('Product Name:', margin + 6, currentY + 7);
    doc.setFont('helvetica', 'normal');
    doc.text(productName, margin + 33, currentY + 7);

    doc.setFont('helvetica', 'bold');
    doc.text('Date & Time:', margin + 110, currentY + 7);
    doc.setFont('helvetica', 'normal');
    doc.text(dateTimeStr, margin + 132, currentY + 7);

    // Row 2
    doc.setFont('helvetica', 'bold');
    doc.text('Overall Status:', margin + 6, currentY + 15);

    if (overallStatus === 'COMPLIANT') {
      doc.setTextColor(21, 128, 61); // Green
      doc.text('✓ COMPLIANT (' + passedCount + ' / ' + totalChecks + ' checks passed)', margin + 33, currentY + 15);
    } else if (overallStatus === 'FLAGGED') {
      doc.setTextColor(185, 28, 28); // Red
      doc.text('⚠ FLAGGED (' + passedCount + ' / ' + totalChecks + ' passed, ' + failedCount + ' failed)', margin + 33, currentY + 15);
    } else {
      doc.setTextColor(180, 83, 9); // Amber
      doc.text('⚡ NEEDS REVIEW (' + unverifiedCount + ' unverified)', margin + 33, currentY + 15);
    }

    currentY += 28;

    // 4. Section Heading: 8 Mandatory Declaration Checks
    doc.setFontSize(10.5);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(11, 37, 69);
    doc.text('EIGHT MANDATORY DECLARATION CHECKS', margin, currentY);

    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(75, 85, 99);
    doc.text('Detailed evaluation under the Legal Metrology (Packaged Commodities) Rules', margin, currentY + 4.5);

    currentY += 8;

    // 8 Declaration items definition
    const declarations = [
      { key: 'commodity_name', num: '1', title: 'Name of Commodity' },
      { key: 'manufacturer_name', num: '2', title: 'Manufacturer Name' },
      { key: 'manufacturer_address', num: '3', title: 'Manufacturer Address' },
      { key: 'net_quantity', num: '4', title: 'Net Quantity' },
      { key: 'mrp', num: '5', title: 'MRP' },
      { key: 'mrp_wording', num: '6', title: 'MRP Wording / Format' },
      { key: 'expiry', num: '7', title: 'Best Before / Use By / Expiry' },
      { key: 'customer_care', num: '8', title: 'Customer-Care Details' }
    ];

    // Render 8 items in neat boxed cards
    declarations.forEach((decl) => {
      const item = checks[decl.key] || {
        requirement_name: decl.title,
        status: 'UNVERIFIED',
        value: null,
        evidence: null
      };

      const checkStatus = item.status || 'UNVERIFIED';
      const detectedVal = item.value ? String(item.value).trim() : 'Not detected';
      const evidenceVal = item.evidence ? `"${String(item.evidence).trim()}"` : 'No matched OCR snippet';

      // Check if space needed for next page
      if (currentY > pageHeight - 35) {
        doc.addPage();
        currentY = 16;
      }

      const cardHeight = 15.5;

      // Card container
      doc.setFillColor(255, 255, 255);
      doc.setDrawColor(229, 231, 235);
      doc.setLineWidth(0.25);
      doc.roundedRect(margin, currentY, contentWidth, cardHeight, 1, 1, 'FD');

      // Left status color bar
      if (checkStatus === 'PASS') {
        doc.setFillColor(21, 128, 61);
      } else if (checkStatus === 'FAIL') {
        doc.setFillColor(185, 28, 28);
      } else {
        doc.setFillColor(180, 83, 9);
      }
      doc.rect(margin, currentY, 1.8, cardHeight, 'F');

      // Title & Status
      doc.setFontSize(8.8);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(11, 37, 69);
      doc.text(`${decl.num}. ${decl.title}`, margin + 5, currentY + 4.8);

      // Status text
      if (checkStatus === 'PASS') {
        doc.setTextColor(21, 128, 61);
        doc.text('Status: PASS', margin + contentWidth - 28, currentY + 4.8);
      } else if (checkStatus === 'FAIL') {
        doc.setTextColor(185, 28, 28);
        doc.text('Status: FAIL', margin + contentWidth - 28, currentY + 4.8);
      } else {
        doc.setTextColor(180, 83, 9);
        doc.text('Status: UNVERIFIED', margin + contentWidth - 38, currentY + 4.8);
      }

      // Detected line
      doc.setFontSize(7.8);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(55, 65, 81);
      doc.text('Detected:', margin + 5, currentY + 9.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(17, 24, 39);
      const safeDetected = doc.splitTextToSize(detectedVal, 140);
      doc.text(safeDetected[0] || 'Not detected', margin + 22, currentY + 9.5);

      // Evidence line
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(75, 85, 99);
      doc.text('Evidence:', margin + 5, currentY + 13.5);
      doc.setFont('helvetica', 'italic');
      doc.setTextColor(75, 85, 99);
      const safeEvidence = doc.splitTextToSize(evidenceVal, 140);
      doc.text(safeEvidence[0] || 'No matched OCR snippet', margin + 22, currentY + 13.5);

      currentY += cardHeight + 2;
    });

    currentY += 4;

    // 5. Summary Table
    if (currentY > pageHeight - 65) {
      doc.addPage();
      currentY = 16;
    }

    doc.setFontSize(10.5);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(11, 37, 69);
    doc.text('COMPLIANCE SUMMARY TABLE', margin, currentY);
    currentY += 3;

    const tableRows = declarations.map(decl => {
      const item = checks[decl.key] || { status: 'UNVERIFIED' };
      return [decl.num, decl.title, item.status || 'UNVERIFIED'];
    });

    if (doc.autoTable) {
      doc.autoTable({
        startY: currentY,
        margin: { left: margin, right: margin },
        head: [['#', 'Mandatory Declaration', 'Status']],
        body: tableRows,
        theme: 'grid',
        headStyles: {
          fillColor: [11, 37, 69],
          textColor: [255, 255, 255],
          fontStyle: 'bold',
          fontSize: 8.2,
          cellPadding: 2
        },
        bodyStyles: {
          fontSize: 7.8,
          cellPadding: 1.8,
          textColor: [17, 24, 39]
        },
        columnStyles: {
          0: { cellWidth: 12, halign: 'center' },
          1: { cellWidth: 130 },
          2: { cellWidth: 40, fontStyle: 'bold' }
        },
        didParseCell: function(data) {
          if (data.section === 'body' && data.column.index === 2) {
            const val = data.cell.raw;
            if (val === 'PASS') {
              data.cell.styles.textColor = [21, 128, 61];
            } else if (val === 'FAIL') {
              data.cell.styles.textColor = [185, 28, 28];
            } else {
              data.cell.styles.textColor = [180, 83, 9];
            }
          }
        }
      });
      currentY = doc.lastAutoTable.finalY + 6;
    }

    // 6. Overall Result Block
    if (currentY > pageHeight - 48) {
      doc.addPage();
      currentY = 16;
    }

    doc.setFontSize(10.5);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(11, 37, 69);
    doc.text('OVERALL RESULT', margin, currentY);
    currentY += 4;

    if (overallStatus === 'COMPLIANT') {
      doc.setFillColor(240, 253, 244);
      doc.setDrawColor(134, 239, 172);
      doc.roundedRect(margin, currentY, contentWidth, 16, 1.5, 1.5, 'FD');
      doc.setFillColor(21, 128, 61);
      doc.rect(margin, currentY, 3, 16, 'F');

      doc.setTextColor(20, 83, 45);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.text('✓ PRODUCT COMPLIANT', margin + 8, currentY + 6.5);

      doc.setFontSize(8.5);
      doc.setFont('helvetica', 'normal');
      doc.text(`${passedCount} / ${totalChecks} checks passed (All mandatory packaged commodity declarations verified)`, margin + 8, currentY + 12);
      currentY += 21;
    } else if (overallStatus === 'FLAGGED') {
      doc.setFillColor(254, 242, 242);
      doc.setDrawColor(252, 165, 165);
      doc.roundedRect(margin, currentY, contentWidth, 18, 1.5, 1.5, 'FD');
      doc.setFillColor(185, 28, 28);
      doc.rect(margin, currentY, 3, 18, 'F');

      doc.setTextColor(127, 29, 29);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.text('⚠ PRODUCT FLAGGED', margin + 8, currentY + 6.5);

      doc.setFontSize(8.2);
      doc.setFont('helvetica', 'normal');
      doc.text(`${passedCount} / ${totalChecks} checks passed   |   ${failedCount} / ${totalChecks} checks failed   |   ${unverifiedCount} / ${totalChecks} checks unverified`, margin + 8, currentY + 11.5);
      doc.text('One or more mandatory declarations are missing or format non-compliant under Legal Metrology rules.', margin + 8, currentY + 15.5);
      currentY += 23;
    } else {
      doc.setFillColor(255, 251, 235);
      doc.setDrawColor(252, 211, 77);
      doc.roundedRect(margin, currentY, contentWidth, 18, 1.5, 1.5, 'FD');
      doc.setFillColor(180, 83, 9);
      doc.rect(margin, currentY, 3, 18, 'F');

      doc.setTextColor(120, 53, 15);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.text('⚡ NEEDS REVIEW', margin + 8, currentY + 6.5);

      doc.setFontSize(8.2);
      doc.setFont('helvetica', 'normal');
      doc.text(`${passedCount} / ${totalChecks} passed   |   ${unverifiedCount} / ${totalChecks} unverified`, margin + 8, currentY + 11.5);
      doc.text('Some declarations could not be reliably verified due to image resolution or clarity.', margin + 8, currentY + 15.5);
      currentY += 23;
    }

    // 7. Disclaimer Box
    if (currentY > pageHeight - 28) {
      doc.addPage();
      currentY = 16;
    }

    doc.setFillColor(248, 250, 252);
    doc.setDrawColor(209, 213, 219);
    doc.roundedRect(margin, currentY, contentWidth, 14, 1, 1, 'FD');

    doc.setFontSize(7.2);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(11, 37, 69);
    doc.text('Disclaimer:', margin + 4, currentY + 4.5);

    doc.setFont('helvetica', 'normal');
    doc.setTextColor(75, 85, 99);
    const disclaimerText =
      'This report provides AI-assisted preliminary verification based on information visible in the uploaded product images. ' +
      'It is not a legal certification and should not be treated as a substitute for verification by the appropriate Legal Metrology authority.';
    const splitDisclaimer = doc.splitTextToSize(disclaimerText, contentWidth - 25);
    doc.text(splitDisclaimer, margin + 20, currentY + 4.5);

    // 8. Page numbering on all pages
    const totalPages = doc.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      doc.setFontSize(7);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(156, 163, 175);
      doc.text(`Legal Metrology Product Compliance Checker  •  Page ${i} of ${totalPages}`, margin, pageHeight - 7);
      doc.text(`Report Date: ${dateTimeStr}`, margin + contentWidth, pageHeight - 7, { align: 'right' });
    }

    // 9. Save PDF file
    const sanitizedName = sanitizeFilename(productName);
    const dateStamp = record.timestamp_iso || formatDateISO(new Date());
    const filename = `${sanitizedName}_Compliance_Report_${dateStamp}.pdf`;

    doc.save(filename);
  }

  // Direct download button handlers from Results view
  if (downloadCurrentPdfBtn) {
    downloadCurrentPdfBtn.addEventListener('click', () => {
      if (currentScanResult) {
        const history = getHistory();
        const latestRecord = history[0] || {
          product_name: resolveProductName(currentScanResult),
          timestamp_str: formatDateTime(new Date()),
          timestamp_full: formatFullDate(new Date()),
          timestamp_iso: formatDateISO(new Date()),
          result: currentScanResult
        };
        generatePdfReport(latestRecord);
      }
    });
  }

  if (bottomDownloadPdfBtn) {
    bottomDownloadPdfBtn.addEventListener('click', () => {
      if (currentScanResult) {
        const history = getHistory();
        const latestRecord = history[0] || {
          product_name: resolveProductName(currentScanResult),
          timestamp_str: formatDateTime(new Date()),
          timestamp_full: formatFullDate(new Date()),
          timestamp_iso: formatDateISO(new Date()),
          result: currentScanResult
        };
        generatePdfReport(latestRecord);
      }
    });
  }

  // Initial load
  updateHistoryBadge();

  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
