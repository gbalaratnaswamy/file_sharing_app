let pswd_field = document.getElementById("password")
let conf_field = document.getElementById("conf_password")
let error_field = document.getElementById("error_log")
let len_field = document.getElementById("len")
let lower_field = document.getElementById("lower")
let upper_field = document.getElementById("upper")
let spec_field = document.getElementById("spec")
let submit = document.getElementById("submit")
let len_cond = false
let lower_cond = false
let upper_cond = false
let spec_cond = false
let pass_equal = false
let pass_pass = false
pswd_field.addEventListener("keyup", function () {

    if (pswd_field.value.length > 7) {
        len_cond = true
        len_field.style.display = "none"
    } else {
        len_cond = false
        len_field.style.display = "block"
    }
    if (pswd_field.value.match(/[a-z]/g)) {
        lower_cond = true
        lower_field.style.display = "none"
    } else {
        lower_cond = false
        lower_field.style.display = "block"
    }
    if (pswd_field.value.match(/[A-Z]/g)) {
        upper_cond = true
        upper_field.style.display = "none"
    } else {
        upper_cond = false
        upper_field.style.display = "block"
    }
    if (pswd_field.value.match(/[@#$%&*!><{}();:]/) != null) {
        spec_cond = true
        spec_field.style.display = "none"
    } else {
        spec_cond = false
        spec_field.style.display = "block"
    }
    if (len_cond && upper_cond && lower_cond && spec_cond) {
        pswd_field.classList.remove("is-invalid")
        pswd_field.classList.add("is-valid")
        pass_pass = true
    } else {
        pswd_field.classList.add("is-invalid")
        pswd_field.classList.remove("is-valid")
        pass_pass = false
    }
    check_validity()
})
conf_field.addEventListener("keyup", function () {
    if (pswd_field.value !== conf_field.value) {
        pass_equal = false
        conf_field.classList.add("is-invalid")
        conf_field.classList.remove("is-valid")
    } else {
        pass_equal = true
        conf_field.classList.remove("is-invalid")
        conf_field.classList.add("is-valid")
    }
    check_validity()

})

function check_validity() {

    submit.disabled = !(pass_pass && pass_equal);
}