document.addEventListener('DOMContentLoaded', () => {
    const quizForm = document.getElementById('quiz-form');
    const generateBtn = document.getElementById('generate-btn');
    //const customPromptField = document.getElementById('custom-prompt');
    const customPromptField = "";
    
    const quizOutput = document.getElementById('quiz-output');
    const executionTime = document.getElementById('execution-time');
    const loadingIndicator = document.getElementById('loading');
    
    // Configure marked options
    marked.setOptions({
        breaks: true,
        highlight: function(code, lang) {
            return hljs.highlightAuto(code, [lang]).value;
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
            const response = await fetch('/generate-quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    // customPrompt: customPromptField.value.trim()
                    customPrompt: customPromptField
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            
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