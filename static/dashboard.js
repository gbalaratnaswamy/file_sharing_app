// let modal_content = document.getElementById("modal_content")
// let modal_delete = document.getElementById("delete")
// let delete_link = document.getElementById("deletelink")
// let delete_alert = function (link) {
//     delete_link.setAttribute("onClick", 'delete_item("' + link + '")')
//     $("#delete").modal("show")
// }
// let show_modal = function (link) {
//     modal_content.setAttribute("value", "http://127.0.0.1:5000" + link)
//     $("#modal").modal("show")
//
// }
// let delete_item = function (link) {
//     let xhttp = new XMLHttpRequest();
//     xhttp.onreadystatechange = function () {
//         if (this.readyState === 4 && this.status === 200) {
//             if (this.responseText === "success") {
//                 $('.card[data-link="' + link + '"]')[0].remove()
//             }
//             $("#delete").modal("hide")
//         }
//     };
//     xhttp.open("GET", "http://127.0.0.1:5000/js" + link, true);
//     xhttp.send();
//
// }
//
// let copy_content = function () {
//     modal_content.select()
//     document.execCommand("copy");
//     let copy_button = document.getElementById("copy")
//     copy_button.innerHTML = "copied!"
//     copy_button.classList.remove("btn-primary")
//     copy_button.classList.add("btn-success")
//
// }


let modal_content = document.getElementById("modal_content")
let modal_delete = document.getElementById("delete")
let delete_link = document.getElementById("deletelink")
let delete_alert = function (link) {
    delete_link.setAttribute("href", link)
    $("#delete").modal("show")
}
let show_modal = function (link) {
    modal_content.setAttribute("value", "localhost:5000" + link)
    $("#modal").modal("show")

}
let copy_content = function () {
    modal_content.select()
    document.execCommand("copy");
    let copy_button = document.getElementById("copy")
    copy_button.innerHTML = "copied!"
    copy_button.classList.remove("btn-primary")
    copy_button.classList.add("btn-success")

}