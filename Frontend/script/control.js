

const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

const listenToUI = function () {
    const btn = document.querySelector('.js-manual-mode');
    btn.addEventListener("click", function () {
        console.log(btn.checked);
        if (btn.checked == true){
            socket.emit("F2B_Manual_Mode_change", {"setting": "manual mode", "value": 1})
        } else {
            socket.emit("F2B_Manual_Mode_change", {"setting": "manual mode", "value": 0})
        }
    });
    const xServo = document.querySelector(".js-sliderX");
    xServo.addEventListener("change", function(){
        console.log(xServo.value)
        value = xServo.value
        socket.emit("F2B_servoX", value)
    })
    const yServo = document.querySelector(".js-sliderY");
    yServo.addEventListener("change", function(){
        console.log(yServo.value)
        socket.emit("F2B_servoY", yServo.value)
    })
}


document.addEventListener("DOMContentLoaded", function () {
    console.info("DOM geladen");
    listenToUI();
});