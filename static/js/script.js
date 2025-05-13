document.addEventListener('DOMContentLoaded', () => {
    // Application state
    const state = {
        user: null,
        token: localStorage.getItem('token'),
        currentQuiz: null,
        currentQuizData: null,
        currentQuestionIndex: 0,
        userAnswers: [],
        quizzes: []
    };

    // DOM Elements
    const elements = {
        // User auth elements
        userInfo: document.getElementById('user-info'),
        username: document.getElementById('username'),
        loginBtn: document.getElementById('login-btn'),
        registerBtn: document.getElementById('register-btn'),
        logoutBtn: document.getElementById('logout-btn'),
        loginForm: document.getElementById('login-form'),
        registerForm: document.getElementById('register-form'),
        switchToLogin: document.getElementById('switch-to-login'),
        switchToRegister: document.getElementById('switch-to-register'),

        // Quiz list elements
        quizListContainer: document.getElementById('quiz-list-container'),
        quizList: document.getElementById('quiz-list'),

        // Create quiz elements
        createQuizContainer: document.getElementById('create-quiz-container'),
        createQuizForm: document.getElementById('create-quiz-form'),
        addQuestionBtn: document.getElementById('add-question-btn'),
        questionsContainer: document.getElementById('questions-container'),

        // Take quiz elements
        takeQuizContainer: document.getElementById('take-quiz-container'),
        quizTitleDisplay: document.getElementById('quiz-title-display'),
        quizDescriptionDisplay: document.getElementById('quiz-description-display'),
        currentQuestion: document.getElementById('current-question'),
        totalQuestions: document.getElementById('total-questions'),
        questionText: document.getElementById('question-text'),
        answersList: document.getElementById('answers-list'),
        nextQuestionBtn: document.getElementById('next-question'),
        submitQuizBtn: document.getElementById('submit-quiz'),

        // Results elements
        quizResults: document.getElementById('quiz-results'),
        score: document.getElementById('score'),
        maxScore: document.getElementById('max-score'),
        percentage: document.getElementById('percentage'),
        backToQuizzesBtn: document.getElementById('back-to-quizzes'),

        // My results elements
        myResultsContainer: document.getElementById('my-results-container'),
        resultsList: document.getElementById('results-list'),

        // Navigation elements
        homeBtn: document.getElementById('home-btn'),
        createBtn: document.getElementById('create-btn'),
        myResultsBtn: document.getElementById('my-results-btn'),

        // Message element
        messageContainer: document.getElementById('message-container'),
        messageText: document.getElementById('message-text')
    };

    // API endpoints
    const API = {
        login: '/api/users/token',
        register: '/api/users/register',
        quizzes: '/api/quiz/quizzes',
        quiz: (id) => `/api/quiz/quizzes/${id}`,
        questions: (quizId) => `/api/quiz/quizzes/${quizId}/questions`,
        submitQuiz: (quizId) => `/api/quiz/quizzes/${quizId}/submit`,
        userResults: '/api/quiz/results'
    };

    // Event Listeners
    function setupEventListeners() {
        // Auth related listeners
        elements.loginBtn.addEventListener('click', () => showElement(elements.loginForm));
        elements.registerBtn.addEventListener('click', () => showElement(elements.registerForm));
        elements.logoutBtn.addEventListener('click', handleLogout);
        elements.switchToLogin.addEventListener('click', () => {
            hideElement(elements.registerForm);
            showElement(elements.loginForm);
        });
        elements.switchToRegister.addEventListener('click', () => {
            hideElement(elements.loginForm);
            showElement(elements.registerForm);
        });

        // Form submissions
        elements.loginForm.querySelector('form').addEventListener('submit', handleLogin);
        elements.registerForm.querySelector('form').addEventListener('submit', handleRegister);
        elements.createQuizForm.addEventListener('submit', handleCreateQuiz);

        // Navigation
        elements.homeBtn.addEventListener('click', () => showHome());
        elements.createBtn.addEventListener('click', () => {
            if (!state.user) {
                showMessage('Please login to create a quiz', 'error');
                return;
            }
            hideAllContainers();
            showElement(elements.createQuizContainer);
            setActiveNavButton(elements.createBtn);
        });
        elements.myResultsBtn.addEventListener('click', () => {
            if (!state.user) {
                showMessage('Please login to view your results', 'error');
                return;
            }
            hideAllContainers();
            loadUserResults();
            showElement(elements.myResultsContainer);
            setActiveNavButton(elements.myResultsBtn);
        });

        // Quiz creation
        elements.addQuestionBtn.addEventListener('click', addQuestionItem);
        document.addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('add-answer-btn')) {
                addAnswerItem(e.target.closest('.question-item').querySelector('.answers-container'));
            }
        });

        // Quiz taking
        elements.nextQuestionBtn.addEventListener('click', handleNextQuestion);
        elements.submitQuizBtn.addEventListener('click', handleSubmitQuiz);
        elements.backToQuizzesBtn.addEventListener('click', showHome);
    }

    // Authentication Functions
    async function handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch(API.login, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    username: email,
                    password: password
                })
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            state.token = data.access_token;
            
            // Get user info
            await fetchUserInfo();
            
            hideElement(elements.loginForm);
            showHome();
            updateAuthUI();
            showMessage('Login successful', 'success');
        } catch (error) {
            showMessage('Login failed: ' + error.message, 'error');
        }
    }

    async function handleRegister(e) {
        e.preventDefault();
        const email = document.getElementById('register-email').value;
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;

        try {
            const response = await fetch(API.register, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    username: username,
                    password: password
                })
            });

            if (!response.ok) {
                throw new Error('Registration failed');
            }

            hideElement(elements.registerForm);
            showElement(elements.loginForm);
            showMessage('Registration successful! Please login.', 'success');
        } catch (error) {
            showMessage('Registration failed: ' + error.message, 'error');
        }
    }

    async function fetchUserInfo() {
        try {
            const response = await fetch('/api/users/me', {
                headers: {
                    'Authorization': `Bearer ${state.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch user info');
            }

            state.user = await response.json();
            elements.username.textContent = state.user.username;
        } catch (error) {
            console.error('Error fetching user info:', error);
            handleLogout();
        }
    }

    function handleLogout() {
        localStorage.removeItem('token');
        state.token = null;
        state.user = null;
        updateAuthUI();
        showHome();
        showMessage('Logged out successfully', 'success');
    }

    function updateAuthUI() {
        if (state.token) {
            elements.loginBtn.classList.add('hidden');
            elements.registerBtn.classList.add('hidden');
            elements.logoutBtn.classList.remove('hidden');
        } else {
            elements.username.textContent = 'Guest';
            elements.loginBtn.classList.remove('hidden');
            elements.registerBtn.classList.remove('hidden');
            elements.logoutBtn.classList.add('hidden');
        }
    }

    // Quiz Functions
    async function fetchQuizzes() {
        try {
            const response = await fetch(API.quizzes);
            if (!response.ok) {
                throw new Error('Failed to fetch quizzes');
            }
            state.quizzes = await response.json();
            renderQuizList();
        } catch (error) {
            showMessage('Error loading quizzes: ' + error.message, 'error');
        }
    }

    function renderQuizList() {
        elements.quizList.innerHTML = '';
        
        if (state.quizzes.length === 0) {
            elements.quizList.innerHTML = '<p class="text-center">No quizzes available</p>';
            return;
        }

        state.quizzes.forEach(quiz => {
            const quizCard = document.createElement('div');
            quizCard.classList.add('quiz-card');
            quizCard.innerHTML = `
                <h3>${quiz.title}</h3>
                <p>${quiz.description}</p>
                <button class="btn take-quiz-btn" data-quiz-id="${quiz.id}">Take Quiz</button>
            `;
            
            quizCard.querySelector('.take-quiz-btn').addEventListener('click', () => loadQuiz(quiz.id));
            
            elements.quizList.appendChild(quizCard);
        });
    }

    async function loadQuiz(quizId) {
        try {
            const response = await fetch(API.quiz(quizId));
            if (!response.ok) {
                throw new Error('Failed to load quiz');
            }
            
            state.currentQuiz = quizId;
            state.currentQuizData = await response.json();
            state.currentQuestionIndex = 0;
            state.userAnswers = [];
            
            startQuiz();
        } catch (error) {
            showMessage('Error loading quiz: ' + error.message, 'error');
        }
    }

    function startQuiz() {
        hideAllContainers();
        showElement(elements.takeQuizContainer);
        
        elements.quizTitleDisplay.textContent = state.currentQuizData.title;
        elements.quizDescriptionDisplay.textContent = state.currentQuizData.description;
        elements.totalQuestions.textContent = state.currentQuizData.questions.length;
        
        displayCurrentQuestion();
    }

    function displayCurrentQuestion() {
        const currentQuestion = state.currentQuizData.questions[state.currentQuestionIndex];
        elements.currentQuestion.textContent = state.currentQuestionIndex + 1;
        elements.questionText.textContent = currentQuestion.text;
        
        elements.answersList.innerHTML = '';
        currentQuestion.answers.forEach((answer, index) => {
            const answerOption = document.createElement('div');
            answerOption.classList.add('answer-option');
            answerOption.dataset.answerId = answer.id;
            answerOption.textContent = answer.text;
            
            answerOption.addEventListener('click', () => {
                // Remove selection from all options
                document.querySelectorAll('.answer-option').forEach(opt => opt.classList.remove('selected'));
                // Add selection to clicked option
                answerOption.classList.add('selected');
            });
            
            elements.answersList.appendChild(answerOption);
        });
        
        // Show next button or submit button
        if (state.currentQuestionIndex < state.currentQuizData.questions.length - 1) {
            elements.nextQuestionBtn.classList.remove('hidden');
            elements.submitQuizBtn.classList.add('hidden');
        } else {
            elements.nextQuestionBtn.classList.add('hidden');
            elements.submitQuizBtn.classList.remove('hidden');
        }
    }

    function handleNextQuestion() {
        const selectedAnswer = document.querySelector('.answer-option.selected');
        if (!selectedAnswer) {
            showMessage('Please select an answer', 'error');
            return;
        }
        
        state.userAnswers.push({
            question_id: state.currentQuizData.questions[state.currentQuestionIndex].id,
            answer_id: parseInt(selectedAnswer.dataset.answerId)
        });
        
        state.currentQuestionIndex++;
        displayCurrentQuestion();
    }

    async function handleSubmitQuiz() {
        const selectedAnswer = document.querySelector('.answer-option.selected');
        if (!selectedAnswer) {
            showMessage('Please select an answer', 'error');
            return;
        }
        
        // Add last answer
        state.userAnswers.push({
            question_id: state.currentQuizData.questions[state.currentQuestionIndex].id,
            answer_id: parseInt(selectedAnswer.dataset.answerId)
        });
        
        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            
            if (state.token) {
                headers['Authorization'] = `Bearer ${state.token}`;
            }
            
            const response = await fetch(API.submitQuiz(state.currentQuiz), {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    answers: state.userAnswers
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to submit quiz');
            }
            
            const result = await response.json();
            displayQuizResults(result);
        } catch (error) {
            showMessage('Error submitting quiz: ' + error.message, 'error');
        }
    }

    function displayQuizResults(result) {
        hideElement(elements.takeQuizContainer);
        showElement(elements.quizResults);
        
        elements.score.textContent = result.score;
        elements.maxScore.textContent = state.currentQuizData.questions.length;
        
        const percentage = Math.round((result.score / state.currentQuizData.questions.length) * 100);
        elements.percentage.textContent = `${percentage}%`;
    }

    async function loadUserResults() {
        if (!state.token) return;
        
        try {
            const response = await fetch(API.userResults, {
                headers: {
                    'Authorization': `Bearer ${state.token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to load results');
            }
            
            const results = await response.json();
            renderUserResults(results);
        } catch (error) {
            showMessage('Error loading results: ' + error.message, 'error');
        }
    }

    function renderUserResults(results) {
        elements.resultsList.innerHTML = '';
        
        if (results.length === 0) {
            elements.resultsList.innerHTML = '<p class="text-center">No quiz results yet</p>';
            return;
        }
        
        results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.classList.add('result-item');
            
            const percentage = Math.round((result.score / result.total_questions) * 100);
            
            resultItem.innerHTML = `
                <div>
                    <h3>${result.quiz_title}</h3>
                    <p>Score: ${result.score}/${result.total_questions} (${percentage}%)</p>
                    <p>Completed: ${new Date(result.created_at).toLocaleDateString()}</p>
                </div>
            `;
            
            elements.resultsList.appendChild(resultItem);
        });
    }

    // Create Quiz Functions
    function addQuestionItem() {
        const questionItems = document.querySelectorAll('.question-item');
        const questionNumber = questionItems.length + 1;
        
        const questionItem = document.createElement('div');
        questionItem.classList.add('question-item');
        questionItem.innerHTML = `
            <div class="form-group">
                <label>Question ${questionNumber}:</label>
                <input type="text" class="question-text" required>
            </div>
            <div class="answers-container">
                <div class="answer-item">
                    <input type="text" class="answer-text" placeholder="Answer option" required>
                    <label>
                        <input type="checkbox" class="is-correct"> Correct
                    </label>
                </div>
                <div class="answer-item">
                    <input type="text" class="answer-text" placeholder="Answer option" required>
                    <label>
                        <input type="checkbox" class="is-correct"> Correct
                    </label>
                </div>
            </div>
            <button type="button" class="btn add-answer-btn">Add Answer</button>
            <button type="button" class="btn remove-question-btn">Remove Question</button>
        `;
        
        questionItem.querySelector('.remove-question-btn').addEventListener('click', function() {
            questionItem.remove();
            // Renumber questions
            document.querySelectorAll('.question-item').forEach((item, index) => {
                item.querySelector('label').textContent = `Question ${index + 1}:`;
            });
        });
        
        elements.questionsContainer.appendChild(questionItem);
    }

    function addAnswerItem(container) {
        const answerItem = document.createElement('div');
        answerItem.classList.add('answer-item');
        answerItem.innerHTML = `
            <input type="text" class="answer-text" placeholder="Answer option" required>
            <label>
                <input type="checkbox" class="is-correct"> Correct
            </label>
            <button type="button" class="btn remove-answer-btn">Remove</button>
        `;
        
        answerItem.querySelector('.remove-answer-btn').addEventListener('click', function() {
            answerItem.remove();
        });
        
        container.appendChild(answerItem);
    }

    async function handleCreateQuiz(e) {
        e.preventDefault();
        
        const title = document.getElementById('quiz-title').value;
        const description = document.getElementById('quiz-description').value;
        
        // Collect questions and answers
        const questionItems = document.querySelectorAll('.question-item');
        const questions = [];
        
        questionItems.forEach(item => {
            const questionText = item.querySelector('.question-text').value;
            const answerItems = item.querySelectorAll('.answer-item');
            
            const answers = [];
            let hasCorrectAnswer = false;
            
            answerItems.forEach(answerItem => {
                const answerText = answerItem.querySelector('.answer-text').value;
                const isCorrect = answerItem.querySelector('.is-correct').checked;
                
                if (isCorrect) {
                    hasCorrectAnswer = true;
                }
                
                answers.push({
                    text: answerText,
                    is_correct: isCorrect
                });
            });
            
            if (!hasCorrectAnswer) {
                showMessage(`Question "${questionText}" must have at least one correct answer`, 'error');
                return;
            }
            
            questions.push({
                text: questionText,
                answers: answers
            });
        });
        
        if (questions.length === 0) {
            showMessage('Please add at least one question', 'error');
            return;
        }
        
        try {
            // First create the quiz
            const quizResponse = await fetch(API.quizzes, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${state.token}`
                },
                body: JSON.stringify({
                    title: title,
                    description: description
                })
            });
            
            if (!quizResponse.ok) {
                throw new Error('Failed to create quiz');
            }
            
            const quizData = await quizResponse.json();
            
            // Then add questions
            for (const question of questions) {
                const questionResponse = await fetch(API.questions(quizData.id), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${state.token}`
                    },
                    body: JSON.stringify(question)
                });
                
                if (!questionResponse.ok) {
                    throw new Error('Failed to add question');
                }
            }
            
            // Reset form
            elements.createQuizForm.reset();
            elements.questionsContainer.innerHTML = `
                <h3>Questions</h3>
                <div class="question-item">
                    <div class="form-group">
                        <label>Question 1:</label>
                        <input type="text" class="question-text" required>
                    </div>
                    <div class="answers-container">
                        <div class="answer-item">
                            <input type="text" class="answer-text" placeholder="Answer option" required>
                            <label>
                                <input type="checkbox" class="is-correct"> Correct
                            </label>
                        </div>
                        <div class="answer-item">
                            <input type="text" class="answer-text" placeholder="Answer option" required>
                            <label>
                                <input type="checkbox" class="is-correct"> Correct
                            </label>
                        </div>
                    </div>
                    <button type="button" class="btn add-answer-btn">Add Answer</button>
                </div>
            `;
            
            showHome();
            showMessage('Quiz created successfully', 'success');
        } catch (error) {
            showMessage('Error creating quiz: ' + error.message, 'error');
        }
    }

    // Utility Functions
    function hideAllContainers() {
        elements.loginForm.classList.add('hidden');
        elements.registerForm.classList.add('hidden');
        elements.quizListContainer.classList.add('hidden');
        elements.createQuizContainer.classList.add('hidden');
        elements.takeQuizContainer.classList.add('hidden');
        elements.quizResults.classList.add('hidden');
        elements.myResultsContainer.classList.add('hidden');
    }

    function showHome() {
        hideAllContainers();
        showElement(elements.quizListContainer);
        setActiveNavButton(elements.homeBtn);
        fetchQuizzes();
    }

    function showElement(element) {
        element.classList.remove('hidden');
    }

    function hideElement(element) {
        element.classList.add('hidden');
    }

    function setActiveNavButton(button) {
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    }

    function showMessage(message, type = 'info') {
        elements.messageText.textContent = message;
        elements.messageContainer.className = `message ${type}`;
        showElement(elements.messageContainer);
        
        setTimeout(() => {
            hideElement(elements.messageContainer);
        }, 3000);
    }

    // Initialization
    async function init() {
        setupEventListeners();
        
        if (state.token) {
            try {
                await fetchUserInfo();
                updateAuthUI();
            } catch (error) {
                console.error('Error during initialization:', error);
                handleLogout();
            }
        }
        
        showHome();
    }

    init();
});