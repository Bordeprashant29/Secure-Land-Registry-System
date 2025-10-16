const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirm_password");

const lengthReq = document.getElementById("length");
const upperReq = document.getElementById("uppercase");
const numReq = document.getElementById("number");
const specialReq = document.getElementById("special");

// Live password validation
passwordInput.addEventListener("input", () => {
  const password = passwordInput.value;

  password.length >= 8 ? lengthReq.classList.replace("invalid", "valid") : lengthReq.classList.replace("valid", "invalid");
  /[A-Z]/.test(password) ? upperReq.classList.replace("invalid", "valid") : upperReq.classList.replace("valid", "invalid");
  /[0-9]/.test(password) ? numReq.classList.replace("invalid", "valid") : numReq.classList.replace("valid", "invalid");
  /[!@#$%^&*(),.?":{}|<>]/.test(password) ? specialReq.classList.replace("invalid", "valid") : specialReq.classList.replace("valid", "invalid");
});

// Final form validation
function validatePassword() {
  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  const isStrong =
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[0-9]/.test(password) &&
    /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (!isStrong) {
    alert("Password does not meet all strength requirements!");
    return false;
  }

  if (password !== confirmPassword) {
    alert("Passwords do not match!");
    return false;
  }

  return true;
}
