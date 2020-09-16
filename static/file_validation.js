let ALLOWED_EXTENSIONS = ["pdf", "png", "jpg", "txt", "jpeg", "gif", "doc", "docx", "xls", "ppt", "pptx", "csv"]
// Add the following code if you want the name of the file appear on select
$(".custom-file-input").on("change", function () {
    var fileName = $(this).val().split("\\").pop();
    $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
});
var file = document.getElementById("customFile")

var size_field = document.getElementById("size")

function form_submit(user_size, user_max_size) {
    let size_consumed = user_size
    let max_size = user_max_size
    var size = file.files[0].size
    console.log(size)
    let name = file.files[0].name
    let type = name.split(".")
    if (ALLOWED_EXTENSIONS.find(function (value) {
        return value === type[type.length - 1]
    })) {
        if (size + size_consumed > max_size) {
            document.getElementById("jserrormessage").innerText = "Not enough space"
            document.getElementById("jserror").style.display = "block"
            return
        }
        console.log("allowed")
        size_field.setAttribute("value", size.toString())
        $("#form").submit()
    } else {
        document.getElementById("jserrormessage").innerText = "File type not supported"
        document.getElementById("jserror").style.display = "block"
        document.getElementById("form").reset()
    }

}