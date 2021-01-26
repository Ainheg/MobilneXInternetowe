check_for_notifications = function() {
    xhr = new XMLHttpRequest();
    xhr.open("GET", "/notifications");
    xhr.onreadystatechange = function() {
        if(xhr.readyState == 4 && xhr.status == 200){
            notifications = JSON.parse(xhr.responseText)
            notifications.forEach(x => alert(x))
        }
    }
    xhr.send();
}
setInterval(check_for_notifications, 10500)