document.addEventListener('DOMContentLoaded', () => {
    const quizForm = document.getElementById('quiz-form');
    const generateBtn = document.getElementById('generate-btn');
    const customPromptField = document.getElementById('custom-prompt');
    
    const quizOutput = document.getElementById('quiz-output');
    const executionTime = document.getElementById('execution-time');
    const loadingIndicator = document.getElementById('loading');
    
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    let currentTab = 'default';
    let customTextbook = null;

    // PDF viewer elements
    const sourceViewer = document.getElementById('source-viewer');
    const toggleSourceBtn = document.getElementById('toggle-source');
    const closeSourceBtn = document.getElementById('close-source');
    const pdfViewer = document.getElementById('pdf-viewer');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const pageNumSpan = document.getElementById('page-num');
    const pageCountSpan = document.getElementById('page-count');
    
    // File upload element
    const textbookUpload = document.getElementById('textbook-upload');
    
    // Configure marked options
    marked.setOptions({
        breaks: true,
        highlight: function(code, lang) {
            return hljs.highlightAuto(code, [lang]).value;
        }
    });
    
    // Handle tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Show active tab content
            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${tabId}-tab`).classList.add('active');
            
            currentTab = tabId;
        });
    });
    
    // Handle source material toggle
    toggleSourceBtn.addEventListener('click', () => {
        sourceViewer.classList.remove('hidden');
        loadDefaultPDF();
    });
    
    closeSourceBtn.addEventListener('click', () => {
        sourceViewer.classList.add('hidden');
    });
    
    // PDF.js setup
    let pdfDoc = null;
    let pageNum = 1;
    let pageRendering = false;
    let pageNumPending = null;
    const scale = 1.5;
    
    function loadDefaultPDF() {
        const url = '/static/assets/dmbok-sample.pdf';
        loadPDF(url);
    }
    
    function loadPDF(url) {
        // Initialize PDF.js
        const pdfjsLib = window['pdfjs-dist/build/pdf'];
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
        
        // Load the PDF
        pdfjsLib.getDocument(url).promise.then(pdf => {
            pdfDoc = pdf;
            pageCountSpan.textContent = pdf.numPages;
            
            // Initial render
            renderPage(pageNum);
        }).catch(error => {
            console.error('Error loading PDF:', error);
            pdfViewer.innerHTML = `<div class="error">Error loading PDF: ${error.message}</div>`;
        });
    }
    
    function renderPage(num) {
        pageRendering = true;
        
        // Reset viewer contents
        pdfViewer.innerHTML = '';
        
        // Get page
        pdfDoc.getPage(num).then(page => {
            const viewport = page.getViewport({ scale });
            
            // Create canvas for the page
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            
            // Add canvas to the viewer
            pdfViewer.appendChild(canvas);
            
            // Render the page
            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            
            const renderTask = page.render(renderContext);
            
            // Wait for rendering to finish
            renderTask.promise.then(() => {
                pageRendering = false;
                
                if (pageNumPending !== null) {
                    renderPage(pageNumPending);
                    pageNumPending = null;
                }
            });
        });
        
        // Update page info
        pageNumSpan.textContent = num;
    }
    
    function queueRenderPage(num) {
        if (pageRendering) {
            pageNumPending = num;
        } else {
            renderPage(num);
        }
    }
    
    // Handle page navigation
    prevPageBtn.addEventListener('click', () => {
        if (pageNum <= 1) return;
        pageNum--;
        queueRenderPage(pageNum);
    });
    
    nextPageBtn.addEventListener('click', () => {
        if (pageNum >= pdfDoc.numPages) return;
        pageNum++;
        queueRenderPage(pageNum);
    });
    
    // Handle file uploads
    textbookUpload.addEventListener('change', event => {
        const file = event.target.files[0];
        if (!file) return;
        
        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File is too large. Maximum size is 10MB.');
            textbookUpload.value = '';
            return;
        }
        
        // Check file type
        if (file.type === 'application/pdf') {
            // Create object URL for the file
            const objectUrl = URL.createObjectURL(file);
            
            // Store file for later use
            customTextbook = {
                file: file,
                url: objectUrl,
                type: 'pdf'
            };
            
            // Show a preview option
            const previewBtn = document.createElement('button');
            previewBtn.textContent = 'Preview Uploaded PDF';
            previewBtn.className = 'secondary-button';
            previewBtn.style.marginTop = '1rem';
            previewBtn.addEventListener('click', () => {
                sourceViewer.classList.remove('hidden');
                loadPDF(objectUrl);
            });
            
            // Add or replace preview button
            const existingBtn = document.querySelector('#custom-tab .secondary-button');
            if (existingBtn) {
                existingBtn.parentNode.replaceChild(previewBtn, existingBtn);
            } else {
                document.getElementById('custom-tab').appendChild(previewBtn);
            }
        } else if (file.type === 'text/plain') {
            // For text files
            const reader = new FileReader();
            reader.onload = function(e) {
                customTextbook = {
                    file: file,
                    content: e.target.result,
                    type: 'text'
                };
            };
            reader.readAsText(file);
        } else {
            alert('Unsupported file type. Please upload a PDF or TXT file.');
            textbookUpload.value = '';
        }
    });
    
    quizForm.addEventListener('submit', async (e) => {
        e.preventDefault();
    
        const resultsSection = document.getElementById('results-section');
        resultsSection.classList.remove('hidden');
        // Small delay for transition to kick in
        setTimeout(() => {
            loadingIndicator.classList.remove('hidden');
        }, 10);
        quizOutput.innerHTML = '';
        executionTime.textContent = '';
        generateBtn.disabled = true;
        
        try {
            // Create FormData if using custom textbook
            let payload = {};
            let fetchOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            };
            
            if (currentTab === 'default') {
                // Use default textbook
                payload = {
                    customPrompt: customPromptField.value.trim(),
                    useCustomTextbook: false
                };
                fetchOptions.body = JSON.stringify(payload);
            } else if (customTextbook) {
                // Use custom textbook
                if (customTextbook.type === 'text') {
                    // For text files, send content directly
                    payload = {
                        customPrompt: customPromptField.value.trim(),
                        useCustomTextbook: true,
                        textbookContent: customTextbook.content
                    };
                    fetchOptions.body = JSON.stringify(payload);
                } else {
                    // For PDF files, use FormData
                    const formData = new FormData();
                    formData.append('textbook', customTextbook.file);
                    if (customPromptField.value.trim()) {
                        formData.append('customPrompt', customPromptField.value.trim());
                    }
                    formData.append('useCustomTextbook', 'true');
                    
                    fetchOptions = {
                        method: 'POST',
                        body: formData
                    };
                }
            } else {
                throw new Error('Please upload a textbook before generating.');
            }
            
            const response = await fetch('/generate-quiz', fetchOptions);
            
            const data = await response.json();
            
            if (!response.ok) {
                if (response.status === 429) {
                    // Rate limit error
                    const retryAfter = data.retry_after || 3600;
                    const retryMinutes = Math.ceil(retryAfter / 60);
                    throw new Error(`Rate limit exceeded. You can make 5 requests per hour. Please try again in ${retryMinutes} minute${retryMinutes > 1 ? 's' : ''}.`);
                } else {
                    throw new Error(`Server responded with status: ${response.status}`);
                }
            }
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Convert markdown to HTML
            const htmlContent = marked.parse(data.quiz);
            quizOutput.innerHTML = htmlContent;
            
            // Apply syntax highlighting to code blocks
            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
            
            // Format quiz elements
            formatQuizElements();
            
            executionTime.textContent = `Generation time: ${data.executionTime}`;
            
        } catch (error) {
            console.error(error);
            quizOutput.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        } finally {
            loadingIndicator.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });
    
    // Format quiz elements for better UI
    function formatQuizElements() {
        // Add classes to quiz components
        const questions = quizOutput.querySelectorAll('ol > li, ul > li');
        questions.forEach((q, i) => {
            q.classList.add('quiz-question');
            q.setAttribute('data-question', i + 1);
        });
        
        // Style options (typically in nested lists)
        const options = quizOutput.querySelectorAll('ol > li ul li, ul > li ul li');
        options.forEach(opt => {
            opt.classList.add('quiz-option');
            // Remove original list markers
            if (opt.parentElement.tagName === 'UL') {
                opt.parentElement.style.listStyleType = 'none';
            }
        });
        
        // Check for answers (usually bold text or marked with "Answer:")
        quizOutput.querySelectorAll('strong, b').forEach(el => {
            if(el.textContent.toLowerCase().includes('answer')) {
                el.parentElement.classList.add('quiz-answer');
            }
        });
    }
});