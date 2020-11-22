var submitButton;
var isFirstNameOk = false;
var isLastNameOk = false;
var isPasswordOk = false;
var isPasswordMatched = false;
var isUsernameOk = false;
var isEmailOk = false;
var isAddressOk = false;

const nameRegex = /^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/;
const passwordRegex = /^.{8,}$/;
const usernameRegex = /^[a-z]{3,12}$/;
const emailRegex = /^[a-z0-9]+([\._]?[a-z0-9])+[@]\w+([.]\w+)+$/;
const addressRegex = /^[\wĄĆĘŁŃÓŚŹŻąćęłńóśźż.\-,\/ ]+$/;

window.onload = function() {
    loadListeners();
    submitButton = document.getElementById("submitButton");
    submitButton.disabled = true;
}

function loadListeners(){
    var firstNameField = document.getElementById("firstNameField");
    firstNameField.addEventListener("input", firstNameCheck);
    var lastNameField = document.getElementById("lastNameField");
    lastNameField.addEventListener("input", lastNameCheck);
    var passwordField = document.getElementById("passwordField");
    passwordField.addEventListener("input", passwordCheck);
    var repeatPasswordField = document.getElementById("repeatPasswordField");
    repeatPasswordField.addEventListener("input", passwordCheck);
    var usernameField = document.getElementById("usernameField");
    usernameField.addEventListener("input", usernameCheck);
    var emailField = document.getElementById("emailField");
    emailField.addEventListener("input", emailCheck);
    var addressField = document.getElementById("addressField");
    addressField.addEventListener("input", addressCheck);
}

function firstNameCheck(){
    var field = document.getElementById("firstNameField");
    isFirstNameOk = nameRegex.test(field.value);
    if (!isFirstNameOk){
        field.className = "formInputWrong";
        document.getElementById("firstNameInfo").className = "formInfoShow";
        document.getElementById("firstNameInfo").innerText = "Imię musi zaczynać się wielką literą i mieć co najmniej 2 znaki" 
    } else {
        field.className = "formInputWhite";
        document.getElementById("firstNameInfo").className = "formInfo";
    }
    validateForm();
}

function lastNameCheck(){
    var field = document.getElementById("lastNameField");
    isLastNameOk = nameRegex.test(field.value);
    if (!isLastNameOk){
        field.className = "formInputWrong";
        document.getElementById("lastNameInfo").className = "formInfoShow";
        document.getElementById("lastNameInfo").innerText = "Nazwisko musi zaczynać się wielką literą i mieć co najmniej 2 znaki" 
    } else {
        field.className = "formInputWhite";
        document.getElementById("lastNameInfo").className = "formInfo";
    }
    validateForm();
}

function passwordCheck(){
    var firstField = document.getElementById("passwordField");
    var secondField = document.getElementById("repeatPasswordField");
    isPasswordOk = passwordRegex.test(firstField.value);
    if (isPasswordOk) {
        isPasswordMatched = (firstField.value == secondField.value)  
        firstField.className = "formInputWhite";
        document.getElementById("passwordInfo").className = "formInfo";
        if (!isPasswordMatched) {
            secondField.className = "formInputWrong";
            document.getElementById("repeatPasswordInfo").className = "formInfoShow";
            document.getElementById("repeatPasswordInfo").innerText = "Hasła się nie zgadzają" 
        } else {
            secondField.className = "formInputWhite";
            document.getElementById("repeatPasswordInfo").className = "formInfo";
        }
    } else {
        firstField.className = "formInputWrong";
        document.getElementById("passwordInfo").className = "formInfoShow";
        document.getElementById("passwordInfo").innerText = "Hasło musi mieć co najmniej 8 znaków" 
    }
    validateForm();
}

function usernameCheck(){
    var field = document.getElementById("usernameField");
    var username = field.value;
    isUsernameOk = usernameRegex.test(username)
    if (isUsernameOk){
        var xhr = new XMLHttpRequest();
        var url = document.location + "/username-check/" + username;
        xhr.open("GET", url, true);
        xhr.onreadystatechange = function () {
            if(xhr.readyState == 4){
                if (xhr.status == 200) {                    
                    var json = JSON.parse(xhr.responseText);
                    isUsernameAvailable = (json["available"] == "yes");
                } else if (xhr.status >= 400 && xhr.status < 500) {
                    console.log("Client side error: ", xhr.status)
                } else if (xhr.status >= 500 && xhr.status < 600) {
                    console.log("Server side error: ", xhr.status)
                }
                if(!isUsernameAvailable){
                    field.className = "formInputWrong";
                    document.getElementById("usernameInfo").className = "formInfoShow";
                    document.getElementById("usernameInfo").innerText = "Nazwa użytkownika jest zajęta"
                } else {
                    field.className = "formInputWhite";
                    document.getElementById("usernameInfo").className = "formInfo";
                }
                validateForm();
            }
        }
        xhr.send();
    } else {
        isUsernameAvailable = false;
        field.className = "formInputWrong";
        document.getElementById("usernameInfo").className = "formInfoShow";
        document.getElementById("usernameInfo").innerText = "Nazwa musi składać się z 3-12 małych liter" 
        validateForm();
    }
}

function emailCheck() {
    var field = document.getElementById("emailField");
    var email = field.value;
    isEmailOk = emailRegex.test(email)
    if (isEmailOk){
        field.className = "formInputWhite";
        document.getElementById("emailInfo").className = "formInfo";
        validateForm();
    } else {
        field.className = "formInputWrong";
        document.getElementById("emailInfo").className = "formInfoShow";
        document.getElementById("emailInfo").innerText = "Podaj poprawny adres e-mail" 
        validateForm();
    }
}

function addressCheck(){
    var field = document.getElementById("addressField");
    isAddressOk = addressRegex.test(field.value);
    if (!isAddressOk){
        field.className = "formInputWrong";
        document.getElementById("addressInfo").className = "formInfoShow";
        document.getElementById("addressInfo").innerText = "Podaj adres lub usuń niedozwolone znaki" 
    } else {
        field.className = "formInputWhite";
        document.getElementById("addressInfo").className = "formInfo";
    }
    validateForm();
}

function validateForm(){
    if (isFirstNameOk && isLastNameOk && isPasswordOk && isPasswordMatched && isUsernameOk && isUsernameAvailable && isEmailOk && isAddressOk){
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}