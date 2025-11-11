// Password visibility toggle
document.addEventListener('DOMContentLoaded', () => {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    if (toggleButtons && toggleButtons.length) {
        toggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Find the input inside the same .password-input container.
                const container = button.closest('.password-input');
                const input = container ? container.querySelector('input[type="password"], input[type="text"]') : null;
                if (!input) return;
                if (input.type === 'password') {
                    input.type = 'text';
                    button.classList.remove('fa-eye');
                    button.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    button.classList.remove('fa-eye-slash');
                    button.classList.add('fa-eye');
                }
            });
        });
    }

    // Form validation
    const registerForm = document.querySelector('.register-form');
    // Password strength meter setup
    function setupPasswordMeter(passwordInput, meterBar, reqList) {
        if (!passwordInput) return;
        function evaluate(pw) {
            const rules = {
                length: /.{8,}/.test(pw),
                upper: /[A-Z]/.test(pw),
                lower: /[a-z]/.test(pw),
                number: /\d/.test(pw),
                special: /[^A-Za-z0-9]/.test(pw)
            };
            const passed = Object.values(rules).filter(Boolean).length;
            const pct = Math.min(100, Math.round((passed / 5) * 100));
            if (meterBar) meterBar.style.width = pct + '%';
            // color change
            if (pct <= 40) {
                meterBar.style.background = 'linear-gradient(90deg,#ff6b6b,#ffb86b)';
            } else if (pct <= 80) {
                meterBar.style.background = 'linear-gradient(90deg,#ffd66b,#b8f2c2)';
            } else {
                meterBar.style.background = 'linear-gradient(90deg,#7be495,#3be58f)';
            }
            // update rules list
            if (reqList) {
                reqList.querySelectorAll('li').forEach(li => {
                    const rule = li.getAttribute('data-rule');
                    if (rules[rule]) li.classList.add('pass'); else li.classList.remove('pass');
                });
            }
        }

        passwordInput.addEventListener('input', (e) => {
            evaluate(e.target.value);
        });
        // initialize
        evaluate(passwordInput.value || '');
    }

    // hook register page meter
    const pwInput = document.querySelector('#password');
    const pwBar = document.querySelector('#pw-bar');
    const pwReq = document.querySelector('#pw-requirements');
    setupPasswordMeter(pwInput, pwBar, pwReq);

    // hook reset page meter (if present)
    const pwInputReset = document.querySelector('#pw-bar-reset') ? document.querySelector('#password') : null;
    if (document.querySelector('#pw-bar-reset')) {
        const pwBarReset = document.querySelector('#pw-bar-reset');
        const pwReqReset = document.querySelector('#pw-requirements-reset');
        // If password input is same id (#password) on reset page, reuse that input
        const inputForReset = document.querySelector('#password');
        setupPasswordMeter(inputForReset, pwBarReset, pwReqReset);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const fullName = document.getElementById('full_name');
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            const mobile = document.getElementById('mobile');
            const email = document.getElementById('email');

            // helper to show inline error
            function setError(el, msg) {
                const err = document.getElementById(el.id + '-error');
                if (err) err.textContent = msg || '';
            }

            // Clear previous errors
            [fullName, email, mobile, password, confirmPassword].forEach(i => { if (i) setError(i, ''); });

            // Name validation: letters, spaces, hyphen/apostrophe allowed, min 2 chars
            if (!fullName || !/^[A-Za-z\s\-']{2,}$/.test(fullName.value.trim())) {
                e.preventDefault();
                setError(fullName, 'Please enter a valid name (letters, spaces only, min 2 chars)');
                fullName.focus();
                return;
            }

            // Email validation
            const emailPattern = /^[\w\.-]+@[\w\.-]+\.\w{2,}$/;
            if (!email || !emailPattern.test(email.value.trim())) {
                e.preventDefault();
                setError(email, 'Please enter a valid email address');
                email.focus();
                return;
            }

            // Mobile number validation: strip non-digits then require 10 digits
            const digits = mobile ? mobile.value.replace(/\D/g, '') : '';
            if (!mobile || digits.length !== 10) {
                e.preventDefault();
                setError(mobile, 'Mobile number must contain 10 digits');
                mobile.focus();
                return;
            }

            // Password strength and match validation
            const pw = password ? password.value : '';
            const pwConstraints = [
                {r: /.{8,}/, msg: 'at least 8 characters'},
                {r: /[A-Z]/, msg: 'an uppercase letter'},
                {r: /[a-z]/, msg: 'a lowercase letter'},
                {r: /\d/, msg: 'a number'},
                {r: /[^A-Za-z0-9]/, msg: 'a special character'}
            ];
            const failed = pwConstraints.filter(c => !c.r.test(pw)).map(c => c.msg);
            if (failed.length) {
                e.preventDefault();
                setError(password, 'Password must contain ' + failed.join(', '));
                password.focus();
                return;
            }

            if (!password || pw !== (confirmPassword ? confirmPassword.value : '')) {
                e.preventDefault();
                setError(confirmPassword, 'Passwords do not match');
                confirmPassword.focus();
                return;
            }
        });
    }
});