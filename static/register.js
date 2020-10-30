var submitButton;
var isFirstNameOk = false;
var isLastNameOk = false;
var isPasswordOk = false;
var isPasswordMatched = false;
var isUsernameOk = false;
var isUsernameAvailable = false;
var isPhotoOk = false;
var isSexSelected = false;
var fileNotified = false;
var sexNotified = false;
const nameRegex = /^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/;
const passwordRegex = /^.{8,}$/;
const usernameRegex = /^[a-z]{3,12}$/;
const wrongColor = "#ff7373";

window.onload = function() {
    loadListeners();
    submitButton = document.getElementById("submitButton");
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
    var photoField = document.getElementById("photoField");
    photoField.addEventListener("change", fileCheck);
    var fRadio = document.getElementById("fRadio");
    fRadio.addEventListener("change", sexCheck);
    var mRadio = document.getElementById("mRadio");
    mRadio.addEventListener("change", sexCheck);
}

function firstNameCheck(){
    var field = document.getElementById("firstNameField");
    isFirstNameOk = nameRegex.test(field.value);
    if (!isFirstNameOk){
        field.style.backgroundColor = wrongColor;
        document.getElementById("firstNameInfo").className = "formInfoShow";
        document.getElementById("firstNameInfo").innerText = "Imię musi zaczynać się wielką literą i mieć co najmniej 2 znaki" 
    } else {
        field.style.backgroundColor="white";
        document.getElementById("firstNameInfo").className = "formInfo";
    }
    validateForm();
}

function lastNameCheck(){
    var field = document.getElementById("lastNameField");
    isLastNameOk = nameRegex.test(field.value);
    if (!isLastNameOk){
        field.style.backgroundColor = wrongColor;
        document.getElementById("lastNameInfo").className = "formInfoShow";
        document.getElementById("lastNameInfo").innerText = "Nazwisko musi zaczynać się wielką literą i mieć co najmniej 2 znaki" 
    } else {
        field.style.backgroundColor="white";
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
        firstField.style.backgroundColor = "white";
        document.getElementById("passwordInfo").className = "formInfo";
        if (!isPasswordMatched) {
            secondField.style.backgroundColor = wrongColor;
            document.getElementById("repeatPasswordInfo").className = "formInfoShow";
            document.getElementById("repeatPasswordInfo").innerText = "Hasła się nie zgadzają" 
        } else {
            secondField.style.backgroundColor = "white";
            document.getElementById("repeatPasswordInfo").className = "formInfo";
        }
    } else {
        firstField.style.backgroundColor = wrongColor;
        document.getElementById("passwordInfo").className = "formInfoShow";
        document.getElementById("passwordInfo").innerText = "Hasło musi mieć co najmniej 8 znaków" 
    }
    validateForm();
}

function fileCheck(){
    var field = document.getElementById("photoField");
    if (field.files.length == 1){
        photo = field.files[0];
        isPhotoOk = (photo.type == "image/jpeg" || photo.type == "image/png")
        if(!isPhotoOk){
            field.style.backgroundColor = wrongColor;
            document.getElementById("photoInfo").className = "formInfoShow";
            document.getElementById("photoInfo").innerText = "Wybrany plik nie jest zdjęciem"
        } else {
            field.style.backgroundColor = "initial";
            document.getElementById("photoInfo").className = "formInfo";
        }
    } else if (field.files.length > 1) {
        field.style.backgroundColor = wrongColor;
        document.getElementById("photoInfo").className = "formInfoShow";
        document.getElementById("photoInfo").innerText = "Wybrano więcej niż jedno zdjęcie"
    } else {
        field.style.backgroundColor = wrongColor;
        document.getElementById("photoInfo").className = "formInfoShow";
        document.getElementById("photoInfo").innerText = "Nie wybrano zdjęcia"
    }
    validateForm();
}

function sexCheck(){
    if(document.getElementById("fRadio").checked || document.getElementById("mRadio").checked){
            document.getElementById("sexSelect").style.backgroundColor= "initial";
            document.getElementById("sexInfo").className = "formInfo";
            isSexSelected = true;
    } else {
        document.getElementById("sexSelect").style.backgroundColor = wrongColor;
        document.getElementById("sexInfo").className = "formInfoShow";
        document.getElementById("sexInfo").innerText = "Nie wybrano płci"
    }
    validateForm();
}

function usernameCheck(){
    var field = document.getElementById("usernameField");
    var username = field.value;
    isUsernameOk = usernameRegex.test(username)
    if (isUsernameOk){
        var xhr = new XMLHttpRequest();
        var url = "https://infinite-hamlet-29399.herokuapp.com/check/" + username;
        xhr.open("GET", url, true);
        //xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if(xhr.readyState == 4){
                if (xhr.status == 200) {                    
                    var json = JSON.parse(xhr.responseText);
                    isUsernameAvailable = (json[username] == "available");
                } else if (xhr.status >= 400 && xhr.status < 500) {
                    console.log("Client side error: ", xhr.status)
                } else if (xhr.status >= 500 && xhr.status < 600) {
                    console.log("Server side error: ", xhr.status)
                }
                if(!isUsernameAvailable){
                    field.style.backgroundColor = wrongColor;
                    document.getElementById("usernameInfo").className = "formInfoShow";
                    document.getElementById("usernameInfo").innerText = "Nazwa użytkownika jest zajęta"
                } else {
                    field.style.backgroundColor="white";
                    document.getElementById("usernameInfo").className = "formInfo";
                }
            }
        }
        xhr.send();
    } else {
        isUsernameAvailable = false;
        field.style.backgroundColor = wrongColor;
        document.getElementById("usernameInfo").className = "formInfoShow";
        document.getElementById("usernameInfo").innerText = "Nazwa musi składać się z 3-12 małych liter" 
    }
    validateForm();
}

function validateForm(){
    if (isFirstNameOk && isLastNameOk && isPasswordOk && isPasswordMatched && isUsernameOk 
        && isUsernameAvailable){
            if (isSexSelected){
                if (isPhotoOk){
                    submitButton.disabled = false;
                } else {
                    if (!fileNotified){
                        fileNotified = true;
                        fileCheck();
                    }
                    submitButton.disabled = true;
                }
            } else {
                if (!sexNotified){
                    sexNotified = true;
                    sexCheck();
                }
                submitButton.disabled = true;
            }
    } else {
        submitButton.disabled = true;
    }
}